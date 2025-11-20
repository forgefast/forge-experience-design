"""
Main Entry Point - ForgeExperienceDesign Backend
"""

import asyncio
import logging
import os
import sys
import uvicorn
from .api.app import create_app
from .infrastructure.storage.fix_repository import FixRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/api.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)


async def initialize_database():
    """Inicializa banco de dados."""
    try:
        db_path = os.getenv('DATABASE_PATH', 'data/fixes.db')
        repository = FixRepository(db_path=db_path)
        await repository.initialize()
        logger.info(f"Banco de dados inicializado: {db_path}")
    except Exception as e:
        logger.warning(f"Erro ao inicializar banco de dados: {e}")


if __name__ == "__main__":
    import platform
    
    logger.info("=" * 60)
    logger.info("Starting ForgeExperienceDesign Backend")
    logger.info("=" * 60)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    try:
        # Inicializar banco de dados
        asyncio.run(initialize_database())
        
        # Create app
        app = create_app()
        
        logger.info("Starting Uvicorn server on port 8003")
        logger.info("=" * 60)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8003,
            reload=False,  # Desabilitado quando executado como módulo
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Fatal error starting server: {e}", exc_info=True)
        sys.exit(1)

