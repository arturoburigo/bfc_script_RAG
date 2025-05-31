#!/usr/bin/env python
"""
run.py - Ponto de entrada para o Sistema RAG Otimizado

Este arquivo permite executar o aplicativo diretamente com o sistema otimizado
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Importar e executar o main otimizado
    from app.main import main
    
    if __name__ == "__main__":
        print("🚀 Iniciando Sistema RAG Otimizado...")
        print("=" * 50)
        main()
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("\n📋 Verifique se:")
    print("1. Todas as dependências estão instaladas (pip install -r requirements.txt)")
    print("2. A variável OPENAI_API_KEY está configurada no .env")
    print("3. Os novos arquivos foram criados corretamente")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Erro ao iniciar o sistema: {e}")
    sys.exit(1)