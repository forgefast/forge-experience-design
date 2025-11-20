"""
Project Configuration

Configuração de projetos alvo para aplicação de correções.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

# Configuração padrão
DEFAULT_PROJECTS: Dict[str, Dict] = {
    "forgetest-studio": {
        "root_path": os.getenv(
            "FORGETEST_STUDIO_PATH",
            "/home/gabriel/softhill/forgetest-studio"
        ),
        "css_paths": [
            "gui/frontend/src/styles/*.css",
            "gui/frontend/src/index.css"
        ],
        "component_paths": [
            "gui/frontend/src/components/*.tsx"
        ],
        "backup_dir": "backups/forgetest-studio"
    }
}


class ProjectConfig:
    """Configuração de um projeto alvo."""
    
    def __init__(
        self,
        project_id: str,
        root_path: str,
        css_paths: List[str],
        component_paths: Optional[List[str]] = None,
        backup_dir: Optional[str] = None
    ):
        self.project_id = project_id
        self.root_path = Path(root_path).expanduser().resolve()
        self.css_paths = css_paths
        self.component_paths = component_paths or []
        self.backup_dir = Path(backup_dir) if backup_dir else Path(f"backups/{project_id}")
        
        # Garantir que diretório de backup existe
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def get_css_files(self) -> List[Path]:
        """Retorna lista de arquivos CSS do projeto."""
        css_files = []
        for pattern in self.css_paths:
            # Resolver padrão relativo ao root_path
            if "*" in pattern:
                # Glob pattern
                css_files.extend(self.root_path.glob(pattern))
            else:
                # Caminho direto
                css_file = self.root_path / pattern
                if css_file.exists():
                    css_files.append(css_file)
        return list(set(css_files))  # Remover duplicatas
    
    def get_component_files(self) -> List[Path]:
        """Retorna lista de arquivos de componentes do projeto."""
        component_files = []
        for pattern in self.component_paths:
            if "*" in pattern:
                component_files.extend(self.root_path.glob(pattern))
            else:
                component_file = self.root_path / pattern
                if component_file.exists():
                    component_files.append(component_file)
        return list(set(component_files))
    
    def get_backup_path(self, timestamp: Optional[str] = None) -> Path:
        """Retorna caminho para backup."""
        if timestamp:
            return self.backup_dir / timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        return self.backup_dir / timestamp
    
    def validate_path(self, file_path: Path) -> bool:
        """Valida se caminho está dentro do projeto (segurança)."""
        try:
            resolved = file_path.resolve()
            return str(resolved).startswith(str(self.root_path.resolve()))
        except Exception:
            return False


class ProjectConfigManager:
    """Gerenciador de configurações de projetos."""
    
    def __init__(self, projects: Optional[Dict[str, Dict]] = None):
        self.projects: Dict[str, ProjectConfig] = {}
        projects = projects or DEFAULT_PROJECTS
        
        for project_id, config in projects.items():
            self.projects[project_id] = ProjectConfig(
                project_id=project_id,
                **config
            )
    
    def get_project(self, project_id: str) -> Optional[ProjectConfig]:
        """Obtém configuração de um projeto."""
        return self.projects.get(project_id)
    
    def add_project(self, project_id: str, config: Dict):
        """Adiciona novo projeto."""
        self.projects[project_id] = ProjectConfig(
            project_id=project_id,
            **config
        )
    
    def list_projects(self) -> List[str]:
        """Lista IDs de projetos configurados."""
        return list(self.projects.keys())


# Instância global
project_manager = ProjectConfigManager()

