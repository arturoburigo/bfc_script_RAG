#!/usr/bin/env python
"""
run.py - Ponto de entrada para o Sistema RAG Otimizado

Este arquivo inicializa todos os componentes do sistema:
1. Banco de dados ChromaDB
2. Sistema RAG Integrado
3. API FastAPI
"""

import sys
import os
from pathlib import Path
import uvicorn
from dotenv import load_dotenv
import logging
from app.core.integrated_rag_system import OptimizedSearchSystem
from app.core.initialize_chroma_db import initialize_chroma_db
from app.core.api.main import app

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def initialize_system():
    """Inicializa todos os componentes do sistema"""
    try:
        # Carregar variáveis de ambiente
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

        # 1. Inicializar banco de dados
        logger.info("📚 Inicializando banco de dados ChromaDB...")
        stats = initialize_chroma_db(reset_collections=True)
        logger.info(f"✅ Banco de dados inicializado: {stats}")

        # 2. Inicializar sistema RAG
        logger.info("🧠 Inicializando sistema RAG...")
        search_system = OptimizedSearchSystem(api_key=api_key)
        
        # Garantir que o sistema está inicializado
        if not search_system.is_initialized:
            logger.info("🔄 Inicializando banco de dados do sistema RAG...")
            search_system.initialize_database(reset_collections=False)  # Já resetamos antes
            
        logger.info("✅ Sistema RAG inicializado")
        return search_system

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar o sistema: {e}")
        raise

def main():
    """Função principal que inicia todos os componentes"""
    try:
        print("🚀 Iniciando Sistema RAG Otimizado...")
        print("=" * 50)

        # Inicializar componentes
        initialize_system()

        # Iniciar a API
        print("\n🌐 Iniciando API...")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )

    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("\n📋 Verifique se:")
        print("1. Todas as dependências estão instaladas (pip install -r requirements.txt)")
        print("2. A variável OPENAI_API_KEY está configurada no .env")
        print("3. Os arquivos foram criados corretamente")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Erro ao iniciar o sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()