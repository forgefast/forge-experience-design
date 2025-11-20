"""
Script para inicializar banco de dados
"""

import asyncio
import sys
import os

# Adicionar backend ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.storage.fix_repository import FixRepository


async def main():
    """Inicializa banco de dados."""
    print("Inicializando banco de dados...")
    
    db_path = os.getenv('DATABASE_PATH', 'data/fixes.db')
    repository = FixRepository(db_path=db_path)
    
    await repository.initialize()
    
    print(f"✅ Banco de dados inicializado em: {db_path}")


if __name__ == "__main__":
    asyncio.run(main())

