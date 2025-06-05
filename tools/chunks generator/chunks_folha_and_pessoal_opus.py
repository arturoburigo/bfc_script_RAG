import json
import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import tiktoken
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter, 
    MarkdownHeaderTextSplitter,
    Language
)
from langchain.schema import Document
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ChunkMetadata:
    """Enhanced metadata structure for chunks"""
    chunk_id: str
    section_name: str
    chunk_index: int
    total_chunks: int
    parent_section: Optional[str]
    chunk_type: str  # 'header', 'description', 'method', 'types', 'expressions', 'code_example', 'mixed'
    semantic_type: str  # 'definition', 'example', 'reference', 'explanation'
    contains_code: bool
    code_language: Optional[str]
    token_count: int
    char_count: int
    overlap_with_previous: int
    overlap_with_next: int
    keywords: List[str]
    entities: List[str]  # function names, type names, etc.
    hierarchy_level: int
    timestamp: str
    source_file: str
    domain: str  # 'folha' or 'pessoal'
    hash: str
    related_chunks: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)

@dataclass
class ProcessedChunk:
    """Container for processed chunk with all necessary information"""
    content: str
    metadata: ChunkMetadata
    embeddings_text: str  # Optimized text for embedding generation
    search_text: str      # Optimized text for search indexing
    
class ContextualOverlapStrategy:
    """Smart overlap strategy based on content type"""
    
    def __init__(self):
        self.overlap_configs = {
            'code_example': {'tokens': 100, 'preserve_structure': True},
            'types': {'tokens': 150, 'preserve_definitions': True},
            'method': {'tokens': 200, 'preserve_signature': True},
            'description': {'tokens': 250, 'preserve_sentences': True},
            'expressions': {'tokens': 150, 'preserve_list_items': True},
            'default': {'tokens': 200, 'preserve_sentences': True}
        }
    
    def get_overlap_size(self, chunk_type: str, content: str) -> int:
        """Determine optimal overlap size based on content type"""
        config = self.overlap_configs.get(chunk_type, self.overlap_configs['default'])
        
        # Adjust based on content characteristics
        if 'preserve_structure' in config and config['preserve_structure']:
            # For code, ensure we don't break in the middle of a function
            if '```' in content:
                return min(300, config['tokens'])
        
        return config['tokens']

class SemanticChunker:
    """Advanced semantic chunking with multiple strategies"""
    
    def __init__(self, 
                 max_tokens: int = 6000,  # Conservative limit for embeddings
                 min_tokens: int = 200,   # Minimum chunk size
                 target_tokens: int = 2000):  # Target size for optimal retrieval
        
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.target_tokens = target_tokens
        self.tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")
        self.overlap_strategy = ContextualOverlapStrategy()
        
        # Initialize specialized splitters
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )
        
        self.code_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.target_tokens,
            chunk_overlap=100,
            separators=["\n\n", "\n", ";", " ", ""],  # Code-specific separators
            length_function=self.count_tokens
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.target_tokens,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", ", ", " ", ""],
            length_function=self.count_tokens
        )
    
    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken"""
        return len(self.tokenizer.encode(text))
    
    def extract_semantic_sections(self, text: str) -> List[Tuple[str, str, str]]:
        """Extract semantic sections with their types"""
        sections = []
        
        # Patterns for different section types
        patterns = {
            'description': r'Description:\s*(.+?)(?=\n(?:Method:|Types:|Expressions:|Code Example:|$))',
            'method': r'Method:\s*(.+?)(?=\n(?:Description:|Types:|Expressions:|Code Example:|$))',
            'method_description': r'Method Description:\s*(.+?)(?=\n(?:Description:|Types:|Expressions:|Code Example:|$))',
            'types': r'Types:\s*(.+?)(?=\n(?:Description:|Method:|Expressions:|Code Example:|$))',
            'expressions': r'Expressions:\s*(.+?)(?=\n(?:Description:|Method:|Types:|Code Example:|$))',
            'code_example': r'Code Example:\s*```(.+?)```',
        }
        
        for section_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                content = match.group(1).strip()
                if content:
                    sections.append((section_type, content, match.span()))
        
        # Sort sections by position
        sections.sort(key=lambda x: x[2][0])
        return [(s[0], s[1]) for s in sections]
    
    def chunk_by_semantic_boundaries(self, 
                                   section_name: str,
                                   section_data: Dict[str, Any],
                                   domain: str) -> List[ProcessedChunk]:
        """Create chunks based on semantic boundaries"""
        chunks = []
        
        # Convert to text first
        full_text = self.convert_to_enhanced_text(section_data, section_name)
        
        # Extract semantic sections
        semantic_sections = self.extract_semantic_sections(full_text)
        
        if not semantic_sections:
            # Fallback to general text splitting
            return self.chunk_by_size(section_name, section_data, domain, full_text)
        
        # Process each semantic section
        for i, (section_type, content) in enumerate(semantic_sections):
            token_count = self.count_tokens(content)
            
            if token_count <= self.max_tokens:
                # Create a single chunk for this section
                chunk = self.create_chunk(
                    content=content,
                    section_name=section_name,
                    chunk_type=section_type,
                    chunk_index=i,
                    total_chunks=len(semantic_sections),
                    domain=domain,
                    section_data=section_data
                )
                chunks.append(chunk)
            else:
                # Split large sections intelligently
                sub_chunks = self.split_large_semantic_section(
                    content, section_type, section_name, domain, section_data
                )
                chunks.extend(sub_chunks)
        
        return chunks
    
    def split_large_semantic_section(self,
                                   content: str,
                                   section_type: str,
                                   section_name: str,
                                   domain: str,
                                   section_data: Dict[str, Any]) -> List[ProcessedChunk]:
        """Split large semantic sections intelligently"""
        chunks = []
        
        if section_type == 'code_example':
            # Use code-aware splitting
            splitter = self.code_splitter
        elif section_type in ['types', 'expressions']:
            # Use structured data splitting
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.target_tokens,
                chunk_overlap=150,
                separators=["\n##", "\n-", "\n", " "],
                length_function=self.count_tokens
            )
        else:
            # Use general text splitting
            splitter = self.text_splitter
        
        # Get overlap size for this content type
        overlap_size = self.overlap_strategy.get_overlap_size(section_type, content)
        splitter._chunk_overlap = overlap_size
        
        # Split content
        split_docs = splitter.split_text(content)
        
        for i, chunk_content in enumerate(split_docs):
            chunk = self.create_chunk(
                content=chunk_content,
                section_name=section_name,
                chunk_type=section_type,
                chunk_index=i,
                total_chunks=len(split_docs),
                domain=domain,
                section_data=section_data,
                parent_section=section_type
            )
            chunks.append(chunk)
        
        return chunks
    
    def chunk_by_size(self,
                     section_name: str,
                     section_data: Dict[str, Any],
                     domain: str,
                     full_text: Optional[str] = None) -> List[ProcessedChunk]:
        """Fallback chunking by size with smart boundaries"""
        if full_text is None:
            full_text = self.convert_to_enhanced_text(section_data, section_name)
        
        # Detect content type
        chunk_type = self.detect_content_type(full_text)
        
        # Choose appropriate splitter
        if "```" in full_text and chunk_type == 'code_example':
            splitter = self.code_splitter
        else:
            splitter = self.text_splitter
        
        # Split text
        chunks_text = splitter.split_text(full_text)
        
        chunks = []
        for i, chunk_content in enumerate(chunks_text):
            chunk = self.create_chunk(
                content=chunk_content,
                section_name=section_name,
                chunk_type=chunk_type,
                chunk_index=i,
                total_chunks=len(chunks_text),
                domain=domain,
                section_data=section_data
            )
            chunks.append(chunk)
        
        return chunks
    
    def create_chunk(self,
                    content: str,
                    section_name: str,
                    chunk_type: str,
                    chunk_index: int,
                    total_chunks: int,
                    domain: str,
                    section_data: Dict[str, Any],
                    parent_section: Optional[str] = None) -> ProcessedChunk:
        """Create a processed chunk with full metadata"""
        
        # Generate chunk ID
        chunk_id = self.generate_chunk_id(section_name, chunk_index, content)
        
        # Extract metadata
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            section_name=section_name,
            chunk_index=chunk_index,
            total_chunks=total_chunks,
            parent_section=parent_section,
            chunk_type=chunk_type,
            semantic_type=self.determine_semantic_type(content, chunk_type),
            contains_code=self.contains_code(content),
            code_language=self.detect_code_language(content) if self.contains_code(content) else None,
            token_count=self.count_tokens(content),
            char_count=len(content),
            overlap_with_previous=0,  # Will be calculated during post-processing
            overlap_with_next=0,      # Will be calculated during post-processing
            keywords=self.extract_keywords(content, section_data),
            entities=self.extract_entities(content, section_data),
            hierarchy_level=self.determine_hierarchy_level(section_name),
            timestamp=datetime.now().isoformat(),
            source_file=f"{domain}.json",
            domain=domain,
            hash=hashlib.md5(content.encode()).hexdigest(),
            quality_score=self.calculate_quality_score(content, chunk_type)
        )
        
        # Create optimized versions for different purposes
        embeddings_text = self.create_embeddings_text(content, metadata)
        search_text = self.create_search_text(content, metadata)
        
        return ProcessedChunk(
            content=content,
            metadata=metadata,
            embeddings_text=embeddings_text,
            search_text=search_text
        )
    
    def convert_to_enhanced_text(self, data: Dict[str, Any], section_name: str) -> str:
        """Enhanced conversion with better structure preservation"""
        text_parts = [f"# {section_name}"]
        
        # Add metadata context
        if "name" in data and data["name"] != section_name:
            text_parts.append(f"Function: {data['name']}")
        
        # Add description with proper formatting
        if "description" in data:
            text_parts.append(f"\nDescription: {data['description']}")
        
        # Add method information with structure
        if "method" in data:
            method = data["method"]
            text_parts.append(f"\nMethod: {method.get('name', 'N/A')} ({method.get('verb', 'N/A')})")
            if "description" in method:
                text_parts.append(f"Method Description: {method['description']}")
        
        # Add representation type
        if "representation" in data:
            rep = data["representation"]
            text_parts.append(f"\nRepresentation Type: {rep.get('type', 'N/A')}")
        
        # Add expressions with better structure
        if "expressions" in data and data["expressions"]:
            text_parts.append("\nExpressions:")
            for key, value in data["expressions"].items():
                if isinstance(value, dict):
                    desc = value.get("description", "")
                    type_info = value.get("type", "")
                    text_parts.append(f"- {key}: {desc} (Type: {type_info})")
                else:
                    text_parts.append(f"- {key}")
        
        # Add types with clear hierarchy
        if "types" in data and data["types"]:
            text_parts.append("\nTypes:")
            for type_name, type_data in data["types"].items():
                text_parts.append(f"\n## {type_name}")
                if isinstance(type_data, dict):
                    for field, field_data in type_data.items():
                        if isinstance(field_data, dict):
                            desc = field_data.get("description", "")
                            type_info = field_data.get("type", "")
                            required = field_data.get("required", False)
                            req_marker = " [REQUIRED]" if required else ""
                            text_parts.append(f"- {field}: {desc} (Type: {type_info}){req_marker}")
                        else:
                            text_parts.append(f"- {field}: {field_data}")
        
        # Add code example with proper formatting
        if "codeExample" in data:
            text_parts.append("\nCode Example:")
            text_parts.append("```groovy")  # Assuming BFC-Script is Groovy-based
            text_parts.append(data["codeExample"])
            text_parts.append("```")
        
        return "\n".join(text_parts)
    
    def detect_content_type(self, content: str) -> str:
        """Detect the primary content type of a chunk"""
        content_lower = content.lower()
        
        if "```" in content and "code example:" in content_lower:
            return 'code_example'
        elif "types:" in content_lower and "##" in content:
            return 'types'
        elif "method:" in content_lower and "method description:" in content_lower:
            return 'method'
        elif "expressions:" in content_lower:
            return 'expressions'
        elif "description:" in content_lower:
            return 'description'
        else:
            return 'mixed'
    
    def determine_semantic_type(self, content: str, chunk_type: str) -> str:
        """Determine the semantic purpose of the content"""
        content_lower = content.lower()
        
        if chunk_type == 'code_example' or '```' in content:
            return 'example'
        elif chunk_type in ['types', 'expressions']:
            return 'reference'
        elif chunk_type == 'method':
            return 'definition'
        elif 'how to' in content_lower or 'example' in content_lower:
            return 'explanation'
        else:
            return 'definition'
    
    def contains_code(self, content: str) -> bool:
        """Check if content contains code"""
        return '```' in content or 'Code Example:' in content
    
    def detect_code_language(self, content: str) -> Optional[str]:
        """Detect programming language from code blocks"""
        code_block_match = re.search(r'```(\w+)?', content)
        if code_block_match and code_block_match.group(1):
            return code_block_match.group(1)
        return 'groovy'  # Default for BFC-Script
    
    def extract_keywords(self, content: str, section_data: Dict[str, Any]) -> List[str]:
        """Extract relevant keywords from content"""
        keywords = set()
        
        # Extract from section name
        if 'name' in section_data:
            keywords.add(section_data['name'].lower())
        
        # Common BFC-Script keywords
        bfc_keywords = ['dados', 'folha', 'pessoal', 'busca', 'filtro', 'ordenacao', 
                       'campo', 'tipo', 'funcao', 'relatorio', 'v2']
        
        content_lower = content.lower()
        for keyword in bfc_keywords:
            if keyword in content_lower:
                keywords.add(keyword)
        
        # Extract type names
        type_matches = re.findall(r'##\s*(\w+)', content)
        keywords.update([t.lower() for t in type_matches])
        
        # Extract field names from expressions
        expr_matches = re.findall(r'-\s*(\w+):', content)
        keywords.update([e.lower() for e in expr_matches[:5]])  # Limit to top 5
        
        return list(keywords)
    
    def extract_entities(self, content: str, section_data: Dict[str, Any]) -> List[str]:
        """Extract named entities (functions, types, etc.)"""
        entities = set()
        
        # Function name
        if 'name' in section_data:
            entities.add(section_data['name'])
        
        # Method name
        if 'method' in section_data and 'name' in section_data['method']:
            entities.add(section_data['method']['name'])
        
        # Type names
        if 'types' in section_data:
            entities.update(section_data['types'].keys())
        
        # Extract from content
        type_matches = re.findall(r'##\s*(\w+)', content)
        entities.update(type_matches)
        
        # Data source references
        data_source_matches = re.findall(r'Dados\.(\w+)\.v2\.(\w+)', content)
        for domain, func in data_source_matches:
            entities.add(f"Dados.{domain}.v2.{func}")
        
        return list(entities)
    
    def determine_hierarchy_level(self, section_name: str) -> int:
        """Determine the hierarchy level based on section name"""
        # Count dots to determine nesting level
        return section_name.count('.')
    
    def calculate_quality_score(self, content: str, chunk_type: str) -> float:
        """Calculate quality score for ranking and filtering"""
        score = 0.0
        
        # Length score (prefer medium-sized chunks)
        token_count = self.count_tokens(content)
        if 500 <= token_count <= 2000:
            score += 0.3
        elif 200 <= token_count < 500 or 2000 < token_count <= 4000:
            score += 0.2
        else:
            score += 0.1
        
        # Content type score
        if chunk_type in ['code_example', 'types']:
            score += 0.3
        elif chunk_type in ['method', 'expressions']:
            score += 0.25
        else:
            score += 0.15
        
        # Structure score
        if content.count('\n') > 5:  # Well-structured content
            score += 0.2
        
        # Completeness score
        if chunk_type == 'code_example' and content.count('```') >= 2:
            score += 0.2  # Complete code block
        elif chunk_type == 'types' and '##' in content:
            score += 0.2  # Has type definitions
        
        return min(score, 1.0)
    
    def create_embeddings_text(self, content: str, metadata: ChunkMetadata) -> str:
        """Create optimized text for embedding generation"""
        parts = []
        
        # Add context from metadata
        parts.append(f"Section: {metadata.section_name}")
        parts.append(f"Type: {metadata.semantic_type}")
        
        if metadata.entities:
            parts.append(f"Related to: {', '.join(metadata.entities[:3])}")
        
        # Add main content
        parts.append("")  # Empty line
        parts.append(content)
        
        # Add keywords for better semantic matching
        if metadata.keywords:
            parts.append("")
            parts.append(f"Keywords: {', '.join(metadata.keywords)}")
        
        return "\n".join(parts)
    
    def create_search_text(self, content: str, metadata: ChunkMetadata) -> str:
        """Create optimized text for search indexing"""
        parts = []
        
        # Include all searchable elements
        parts.append(metadata.section_name)
        parts.extend(metadata.entities)
        parts.extend(metadata.keywords)
        
        # Add content without code blocks for cleaner search
        if metadata.contains_code:
            # Remove code blocks for search text
            search_content = re.sub(r'```[\s\S]*?```', '[CODE_BLOCK]', content)
            parts.append(search_content)
        else:
            parts.append(content)
        
        return " ".join(parts)
    
    def generate_chunk_id(self, section_name: str, chunk_index: int, content: str) -> str:
        """Generate unique chunk ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{section_name}_{chunk_index}_{content_hash}"

class ChunkPostProcessor:
    """Post-process chunks for quality and relationships"""
    
    def __init__(self):
        self.tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")
    
    def process_chunks(self, chunks: List[ProcessedChunk]) -> List[ProcessedChunk]:
        """Apply post-processing to improve chunk quality"""
        
        # Sort chunks by section and index
        chunks.sort(key=lambda c: (c.metadata.section_name, c.metadata.chunk_index))
        
        # Calculate overlaps
        self.calculate_overlaps(chunks)
        
        # Find related chunks
        self.find_related_chunks(chunks)
        
        # Validate and fix issues
        self.validate_chunks(chunks)
        
        return chunks
    
    def calculate_overlaps(self, chunks: List[ProcessedChunk]):
        """Calculate overlap between consecutive chunks"""
        for i in range(len(chunks) - 1):
            current = chunks[i]
            next_chunk = chunks[i + 1]
            
            if current.metadata.section_name == next_chunk.metadata.section_name:
                # Calculate token overlap
                current_tokens = set(self.tokenizer.encode(current.content))
                next_tokens = set(self.tokenizer.encode(next_chunk.content))
                
                overlap_tokens = len(current_tokens.intersection(next_tokens))
                
                current.metadata.overlap_with_next = overlap_tokens
                next_chunk.metadata.overlap_with_previous = overlap_tokens
    
    def find_related_chunks(self, chunks: List[ProcessedChunk]):
        """Identify related chunks based on content and entities"""
        # Build entity index
        entity_index = defaultdict(list)
        for chunk in chunks:
            for entity in chunk.metadata.entities:
                entity_index[entity].append(chunk.metadata.chunk_id)
        
        # Find related chunks
        for chunk in chunks:
            related = set()
            
            # Related by entities
            for entity in chunk.metadata.entities:
                related.update(entity_index[entity])
            
            # Related by parent section
            if chunk.metadata.parent_section:
                for other in chunks:
                    if (other.metadata.section_name == chunk.metadata.section_name and
                        other.metadata.chunk_id != chunk.metadata.chunk_id):
                        related.add(other.metadata.chunk_id)
            
            # Remove self-reference
            related.discard(chunk.metadata.chunk_id)
            
            chunk.metadata.related_chunks = list(related)[:5]  # Limit to 5 related chunks
    
    def validate_chunks(self, chunks: List[ProcessedChunk]):
        """Validate chunks and log any issues"""
        issues = []
        
        for chunk in chunks:
            # Check minimum size
            if chunk.metadata.token_count < 50:
                issues.append(f"Chunk {chunk.metadata.chunk_id} is too small ({chunk.metadata.token_count} tokens)")
            
            # Check maximum size
            if chunk.metadata.token_count > 8000:
                issues.append(f"Chunk {chunk.metadata.chunk_id} exceeds max size ({chunk.metadata.token_count} tokens)")
            
            # Check for incomplete code blocks
            if chunk.metadata.contains_code:
                code_block_count = chunk.content.count('```')
                if code_block_count % 2 != 0:
                    issues.append(f"Chunk {chunk.metadata.chunk_id} has incomplete code blocks")
        
        if issues:
            logger.warning(f"Validation issues found: {len(issues)}")
            for issue in issues[:10]:  # Log first 10 issues
                logger.warning(issue)

class ChunkOutputManager:
    """Manage output of chunks in various formats"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.chunks_dir = self.output_dir / "chunks"
        self.metadata_dir = self.output_dir / "metadata"
        self.index_dir = self.output_dir / "index"
        
        for dir_path in [self.chunks_dir, self.metadata_dir, self.index_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def save_chunks(self, chunks: List[ProcessedChunk], domain: str):
        """Save chunks in multiple formats"""
        
        # Save individual chunk files
        self.save_chunk_files(chunks, domain)
        
        # Save metadata index
        self.save_metadata_index(chunks, domain)
        
        # Save chunk relationships
        self.save_chunk_relationships(chunks, domain)
        
        # Save quality report
        self.save_quality_report(chunks, domain)
        
        # Save embeddings-ready file
        self.save_embeddings_file(chunks, domain)
    
    def save_chunk_files(self, chunks: List[ProcessedChunk], domain: str):
        """Save individual chunk files"""
        domain_dir = self.chunks_dir / domain
        domain_dir.mkdir(exist_ok=True)
        
        for chunk in chunks:
            filename = f"{chunk.metadata.chunk_id}.json"
            filepath = domain_dir / filename
            
            chunk_data = {
                'content': chunk.content,
                'metadata': chunk.metadata.to_dict(),
                'embeddings_text': chunk.embeddings_text,
                'search_text': chunk.search_text
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, ensure_ascii=False, indent=2)
    
    def save_metadata_index(self, chunks: List[ProcessedChunk], domain: str):
        """Save metadata index for quick lookup"""
        index_data = {
            'domain': domain,
            'total_chunks': len(chunks),
            'generation_time': datetime.now().isoformat(),
            'chunks': []
        }
        
        for chunk in chunks:
            index_entry = {
                'chunk_id': chunk.metadata.chunk_id,
                'section_name': chunk.metadata.section_name,
                'chunk_type': chunk.metadata.chunk_type,
                'token_count': chunk.metadata.token_count,
                'quality_score': chunk.metadata.quality_score,
                'entities': chunk.metadata.entities,
                'keywords': chunk.metadata.keywords
            }
            index_data['chunks'].append(index_entry)
        
        filepath = self.metadata_dir / f"{domain}_index.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    def save_chunk_relationships(self, chunks: List[ProcessedChunk], domain: str):
        """Save chunk relationship graph"""
        relationships = {
            'nodes': [],
            'edges': []
        }
        
        # Create nodes
        for chunk in chunks:
            node = {
                'id': chunk.metadata.chunk_id,
                'label': chunk.metadata.section_name,
                'type': chunk.metadata.chunk_type,
                'quality': chunk.metadata.quality_score
            }
            relationships['nodes'].append(node)
        
        # Create edges
        edge_set = set()
        for chunk in chunks:
            for related_id in chunk.metadata.related_chunks:
                edge_key = tuple(sorted([chunk.metadata.chunk_id, related_id]))
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edge = {
                        'source': chunk.metadata.chunk_id,
                        'target': related_id,
                        'type': 'related'
                    }
                    relationships['edges'].append(edge)
        
        filepath = self.index_dir / f"{domain}_relationships.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, ensure_ascii=False, indent=2)
    
    def save_quality_report(self, chunks: List[ProcessedChunk], domain: str):
        """Generate and save quality report"""
        report = {
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_chunks': len(chunks),
                'avg_token_count': sum(c.metadata.token_count for c in chunks) / len(chunks) if chunks else 0,
                'avg_quality_score': sum(c.metadata.quality_score for c in chunks) / len(chunks) if chunks else 0,
            },
            'chunk_type_distribution': defaultdict(int),
            'semantic_type_distribution': defaultdict(int),
            'token_distribution': {
                'min': min(c.metadata.token_count for c in chunks) if chunks else 0,
                'max': max(c.metadata.token_count for c in chunks) if chunks else 0,
                'buckets': defaultdict(int)
            },
            'quality_distribution': defaultdict(int),
            'issues': []
        }
        
        # Analyze chunks
        for chunk in chunks:
            # Type distributions
            report['chunk_type_distribution'][chunk.metadata.chunk_type] += 1
            report['semantic_type_distribution'][chunk.metadata.semantic_type] += 1
            
            # Token buckets
            bucket = (chunk.metadata.token_count // 500) * 500
            report['token_distribution']['buckets'][f"{bucket}-{bucket+499}"] += 1
            
            # Quality buckets
            quality_bucket = int(chunk.metadata.quality_score * 10) / 10
            report['quality_distribution'][f"{quality_bucket:.1f}"] += 1
            
            # Check for issues
            if chunk.metadata.token_count < 100:
                report['issues'].append(f"Chunk {chunk.metadata.chunk_id} is too small")
            if chunk.metadata.quality_score < 0.3:
                report['issues'].append(f"Chunk {chunk.metadata.chunk_id} has low quality score")
        
        # Convert defaultdicts to regular dicts for JSON serialization
        report['chunk_type_distribution'] = dict(report['chunk_type_distribution'])
        report['semantic_type_distribution'] = dict(report['semantic_type_distribution'])
        report['token_distribution']['buckets'] = dict(report['token_distribution']['buckets'])
        report['quality_distribution'] = dict(report['quality_distribution'])
        
        filepath = self.index_dir / f"{domain}_quality_report.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def save_embeddings_file(self, chunks: List[ProcessedChunk], domain: str):
        """Save embeddings-ready file for vector processing"""
        embeddings_data = []
        
        for chunk in chunks:
            entry = {
                'id': chunk.metadata.chunk_id,
                'text': chunk.embeddings_text,
                'metadata': {
                    'section_name': chunk.metadata.section_name,
                    'chunk_type': chunk.metadata.chunk_type,
                    'semantic_type': chunk.metadata.semantic_type,
                    'domain': domain,
                    'entities': chunk.metadata.entities,
                    'keywords': chunk.metadata.keywords,
                    'quality_score': chunk.metadata.quality_score,
                    'token_count': chunk.metadata.token_count
                }
            }
            embeddings_data.append(entry)
        
        filepath = self.output_dir / f"{domain}_embeddings_ready.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(embeddings_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(embeddings_data)} embeddings-ready entries to {filepath}")

class AdvancedRAGChunker:
    """Main class orchestrating the entire chunking pipeline"""
    
    def __init__(self, 
                 max_tokens: int = 6000,
                 min_tokens: int = 200,
                 target_tokens: int = 2000):
        
        self.chunker = SemanticChunker(max_tokens, min_tokens, target_tokens)
        self.post_processor = ChunkPostProcessor()
        self.stats = {
            'total_sections': 0,
            'total_chunks': 0,
            'processing_time': 0,
            'errors': []
        }
    
    def process_json_file(self, 
                         input_file: Path,
                         output_dir: Path,
                         domain: str) -> Dict[str, Any]:
        """Process entire JSON file with the chunking pipeline"""
        
        start_time = datetime.now()
        logger.info(f"Starting processing of {input_file}")
        
        # Load JSON data
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except Exception as e:
            error_msg = f"Failed to load JSON file: {str(e)}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return self.stats
        
        # Process each section
        all_chunks = []
        self.stats['total_sections'] = len(json_data)
        
        for section_name, section_data in json_data.items():
            try:
                logger.info(f"Processing section: {section_name}")
                
                # Choose chunking strategy based on content
                chunks = self.chunker.chunk_by_semantic_boundaries(
                    section_name, section_data, domain
                )
                
                all_chunks.extend(chunks)
                logger.info(f"Created {len(chunks)} chunks for section {section_name}")
                
            except Exception as e:
                error_msg = f"Error processing section {section_name}: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)
                continue
        
        # Post-process all chunks
        logger.info("Starting post-processing...")
        processed_chunks = self.post_processor.process_chunks(all_chunks)
        
        # Save results
        logger.info("Saving results...")
        output_manager = ChunkOutputManager(output_dir)
        output_manager.save_chunks(processed_chunks, domain)
        
        # Update stats
        self.stats['total_chunks'] = len(processed_chunks)
        self.stats['processing_time'] = (datetime.now() - start_time).total_seconds()
        
        # Generate summary
        self.generate_summary(processed_chunks, output_dir, domain)
        
        logger.info(f"Processing completed. Total chunks: {self.stats['total_chunks']}")
        return self.stats
    
    def generate_summary(self, chunks: List[ProcessedChunk], output_dir: Path, domain: str):
        """Generate processing summary"""
        summary = {
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'total_sections': self.stats['total_sections'],
                'total_chunks': self.stats['total_chunks'],
                'processing_time_seconds': self.stats['processing_time'],
                'errors_count': len(self.stats['errors'])
            },
            'chunk_statistics': {
                'avg_tokens': sum(c.metadata.token_count for c in chunks) / len(chunks) if chunks else 0,
                'total_tokens': sum(c.metadata.token_count for c in chunks),
                'unique_entities': len(set(e for c in chunks for e in c.metadata.entities)),
                'unique_keywords': len(set(k for c in chunks for k in c.metadata.keywords))
            },
            'recommendations': self.generate_recommendations(chunks)
        }
        
        filepath = output_dir / f"{domain}_processing_summary.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    
    def generate_recommendations(self, chunks: List[ProcessedChunk]) -> List[str]:
        """Generate recommendations based on chunk analysis"""
        recommendations = []
        
        # Token size analysis
        avg_tokens = sum(c.metadata.token_count for c in chunks) / len(chunks) if chunks else 0
        if avg_tokens < 500:
            recommendations.append("Consider increasing chunk size for better context")
        elif avg_tokens > 3000:
            recommendations.append("Consider decreasing chunk size for better precision")
        
        # Quality analysis
        low_quality_chunks = [c for c in chunks if c.metadata.quality_score < 0.3]
        if len(low_quality_chunks) > len(chunks) * 0.1:
            recommendations.append(f"Review {len(low_quality_chunks)} low-quality chunks")
        
        # Type distribution
        type_counts = defaultdict(int)
        for chunk in chunks:
            type_counts[chunk.metadata.chunk_type] += 1
        
        if 'code_example' not in type_counts or type_counts['code_example'] < len(chunks) * 0.1:
            recommendations.append("Consider adding more code examples for better retrieval")
        
        return recommendations

def main():
    # --- Configuration ---
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent  # Go up two levels to reach project root
    
    # Choose the input file: "pessoal.json" or "folha.json"
    input_file_name = "pessoal.json"  # Default to pessoal.json
    
    # Location of input JSON files in project root
    input_file_path = project_root / input_file_name
    
    # Base directory for all enhanced chunk outputs
    output_base_dir = project_root / "chunks_enhanced_v2"
    # Specific output directory for this input file's chunks
    output_file_specific_dir = output_base_dir / Path(input_file_name).stem
    
    # Global MAX_TOKENS and TOKEN_OVERLAP are used from top of the script
    print(f"--- Starting Chunking Process ---")
    print(f"Input JSON file: {input_file_path}")
    print(f"Output directory for chunks: {output_file_specific_dir}")
    print(f"Max tokens per chunk: {MAX_TOKENS}")
    print(f"Token overlap: {TOKEN_OVERLAP}")

    if not input_file_path.exists():
        print(f"Error: Input file not found at {input_file_path}")
        return

    json_content = load_json_data(str(input_file_path))
    
    print(f"\nStarting chunk generation for: {input_file_name}...")
    document_chunks = create_document_chunks(
        json_data=json_content,
        document_id=Path(input_file_name).stem,
        max_tokens_per_chunk=MAX_TOKENS,
        chunk_overlap_tokens=TOKEN_OVERLAP
    )
    
    if document_chunks:
        save_chunks_to_files(document_chunks, output_file_specific_dir)
        print(f"\nSuccessfully generated and saved {len(document_chunks)} chunks for {input_file_name}.")
    else:
        print("\nNo chunks were generated from the input file.")
    
    print(f"--- Chunking Process Finished ---")

if __name__ == "__main__":
    main()