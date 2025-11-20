"""
Patch Applier

Aplica correções nos arquivos fonte com backup.
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

from ...config.project_config import ProjectConfig
from .css_modifier import CSSModifier
from .file_locator import FileLocator

logger = logging.getLogger(__name__)


class PatchApplier:
    """Aplicador de patches em arquivos fonte."""
    
    def __init__(self, project_config: ProjectConfig):
        self.project_config = project_config
        self.css_modifier = CSSModifier(project_config)
        self.file_locator = FileLocator(project_config)
        logger.info(f"PatchApplier inicializado para projeto: {project_config.project_id}")
    
    def apply_fix(
        self,
        fix: Dict,
        create_backup: bool = True
    ) -> Dict:
        """
        Aplica correção no arquivo fonte.
        
        Args:
            fix: Dict com informações da correção
            create_backup: Criar backup antes de aplicar
        
        Returns:
            Dict com resultado:
            {
                "success": bool,
                "file_path": str,
                "backup_path": Optional[str],
                "changes_applied": List[Dict],
                "errors": List[str]
            }
        """
        # Localizar arquivo
        file_info = self.file_locator.locate_file_for_fix(fix)
        
        if not file_info:
            return {
                "success": False,
                "errors": ["Arquivo não encontrado para o seletor"]
            }
        
        file_path = file_info["relative_path"]
        selector = fix.get("target_selector") or fix.get("target_element", "")
        changes = fix.get("changes", [])
        
        # Criar backup se solicitado
        backup_path = None
        if create_backup:
            backup_path = self._create_backup(file_path)
            if not backup_path:
                return {
                    "success": False,
                    "errors": ["Falha ao criar backup"]
                }
        
        # Aplicar modificação
        result = self.css_modifier.modify_css_file(
            file_path=file_path,
            selector=selector,
            changes=changes
        )
        
        if not result["success"]:
            return {
                "success": False,
                "file_path": file_path,
                "backup_path": backup_path,
                "errors": result.get("errors", [])
            }
        
        # Validar CSS modificado
        is_valid, validation_errors = self.css_modifier.validate_css(
            result["modified_content"]
        )
        
        if not is_valid:
            # Restaurar backup se validação falhar
            if backup_path:
                self._restore_backup(file_path, backup_path)
            
            return {
                "success": False,
                "file_path": file_path,
                "backup_path": backup_path,
                "errors": validation_errors
            }
        
        # Escrever arquivo modificado
        try:
            full_path = self.project_config.root_path / file_path
            full_path.write_text(result["modified_content"], encoding='utf-8')
            
            return {
                "success": True,
                "file_path": file_path,
                "backup_path": str(backup_path) if backup_path else None,
                "changes_applied": result["changes_applied"],
                "errors": []
            }
        
        except Exception as e:
            logger.error(f"Erro ao escrever arquivo: {e}")
            
            # Restaurar backup se escrita falhar
            if backup_path:
                self._restore_backup(file_path, backup_path)
            
            return {
                "success": False,
                "file_path": file_path,
                "backup_path": str(backup_path) if backup_path else None,
                "errors": [str(e)]
            }
    
    def _create_backup(self, file_path: str) -> Optional[Path]:
        """Cria backup de um arquivo."""
        try:
            full_path = self.project_config.root_path / file_path
            
            if not full_path.exists():
                logger.warning(f"Arquivo não existe para backup: {file_path}")
                return None
            
            # Criar diretório de backup com timestamp
            backup_dir = self.project_config.get_backup_path()
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Caminho do backup (preservar estrutura de diretórios)
            backup_file = backup_dir / file_path
            
            # Criar diretórios necessários
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar arquivo
            shutil.copy2(full_path, backup_file)
            
            logger.info(f"Backup criado: {backup_file}")
            return backup_file
        
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return None
    
    def _restore_backup(self, file_path: str, backup_path: Path) -> bool:
        """Restaura arquivo do backup."""
        try:
            if not backup_path.exists():
                logger.error(f"Backup não existe: {backup_path}")
                return False
            
            full_path = self.project_config.root_path / file_path
            
            # Criar diretório se não existir
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Restaurar arquivo
            shutil.copy2(backup_path, full_path)
            
            logger.info(f"Arquivo restaurado do backup: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def rollback_fix(self, fix: Dict, backup_path: str) -> Dict:
        """
        Reverte correção usando backup.
        
        Args:
            fix: Dict com informações da correção
            backup_path: Caminho do backup
        
        Returns:
            Dict com resultado
        """
        file_info = self.file_locator.locate_file_for_fix(fix)
        
        if not file_info:
            return {
                "success": False,
                "errors": ["Arquivo não encontrado"]
            }
        
        file_path = file_info["relative_path"]
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {
                "success": False,
                "errors": [f"Backup não encontrado: {backup_path}"]
            }
        
        success = self._restore_backup(file_path, backup_file)
        
        return {
            "success": success,
            "file_path": file_path,
            "backup_path": backup_path,
            "errors": [] if success else ["Falha ao restaurar backup"]
        }
    
    def list_backups(self) -> List[Dict]:
        """Lista backups disponíveis."""
        backups = []
        backup_dir = self.project_config.backup_dir
        
        if not backup_dir.exists():
            return backups
        
        for backup_folder in sorted(backup_dir.iterdir(), reverse=True):
            if backup_folder.is_dir():
                # Listar arquivos no backup
                for backup_file in backup_folder.rglob('*'):
                    if backup_file.is_file():
                        relative_path = backup_file.relative_to(backup_folder)
                        backups.append({
                            "backup_path": str(backup_file),
                            "relative_path": str(relative_path),
                            "timestamp": backup_folder.name,
                            "size": backup_file.stat().st_size,
                            "created_at": datetime.fromtimestamp(
                                backup_file.stat().st_mtime
                            ).isoformat()
                        })
        
        return backups

