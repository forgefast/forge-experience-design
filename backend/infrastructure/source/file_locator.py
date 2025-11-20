"""
File Locator

Localiza arquivos CSS baseado em seletores.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional

from ...config.project_config import ProjectConfig
from .source_analyzer import SourceAnalyzer

logger = logging.getLogger(__name__)


class FileLocator:
    """Localizador de arquivos fonte."""
    
    def __init__(self, project_config: ProjectConfig):
        self.project_config = project_config
        self.analyzer = SourceAnalyzer(project_config)
        logger.info(f"FileLocator inicializado para projeto: {project_config.project_id}")
    
    def locate_file_for_selector(self, selector: str) -> Optional[Dict]:
        """
        Localiza arquivo mais apropriado para um seletor.
        
        Args:
            selector: Seletor CSS (ex: ".btn-base" ou "button, [role=\"button\"]")
        
        Returns:
            Dict com informações do arquivo:
            {
                "file_path": str,
                "relative_path": str,
                "line": int,
                "selector": str,
                "confidence": float  # 0.0 a 1.0
            }
        """
        # Se seletor for genérico (ex: "button, [role=\"button\"]"), 
        # tentar encontrar arquivo mais apropriado baseado em padrões
        if "," in selector or selector.strip() in ["button", "[role=\"button\"]"]:
            # Para seletores genéricos, usar arquivo de componentes
            css_files = self.project_config.get_css_files()
            # Preferir arquivo de componentes
            for css_file in css_files:
                if "components" in str(css_file):
                    # Retornar arquivo de componentes como fallback
                    return {
                        "file_path": str(css_file),
                        "relative_path": str(css_file.relative_to(self.project_config.root_path)),
                        "line": 1,
                        "selector": selector,
                        "confidence": 0.5
                    }
            # Se não encontrar components.css, usar primeiro arquivo CSS
            if css_files:
                css_file = css_files[0]
                return {
                    "file_path": str(css_file),
                    "relative_path": str(css_file.relative_to(self.project_config.root_path)),
                    "line": 1,
                    "selector": selector,
                    "confidence": 0.4
                }
        
        matches = self.analyzer.find_selector_in_files(selector)
        
        if not matches:
            logger.warning(f"Seletor não encontrado: {selector}")
            # Fallback: retornar arquivo de componentes se existir
            css_files = self.project_config.get_css_files()
            for css_file in css_files:
                if "components" in str(css_file):
                    return {
                        "file_path": str(css_file),
                        "relative_path": str(css_file.relative_to(self.project_config.root_path)),
                        "line": 1,
                        "selector": selector,
                        "confidence": 0.3
                    }
            return None
        
        # Se múltiplos matches, escolher o mais específico
        if len(matches) == 1:
            match = matches[0]
            match["confidence"] = 1.0
            return match
        
        # Escolher melhor match baseado em:
        # 1. Correspondência exata
        # 2. Arquivo mais específico (menos genérico)
        best_match = None
        best_score = 0.0
        
        for match in matches:
            score = 0.0
            
            # Correspondência exata = 1.0
            if match["selector"].strip() == selector.strip():
                score = 1.0
            # Correspondência parcial = 0.7
            elif selector.strip() in match["selector"]:
                score = 0.7
            # Correspondência de classe = 0.5
            else:
                score = 0.5
            
            # Preferir arquivos de componentes sobre index.css
            if "components" in match["relative_path"].lower():
                score += 0.1
            
            if score > best_score:
                best_score = score
                best_match = match
        
        if best_match:
            best_match["confidence"] = best_score
        
        return best_match
    
    def locate_file_for_fix(self, fix: Dict) -> Optional[Dict]:
        """
        Localiza arquivo para uma correção.
        
        Args:
            fix: Dict com informações da correção
        
        Returns:
            Dict com informações do arquivo alvo
        """
        selector = fix.get("target_selector") or fix.get("target_element", "")
        
        if not selector:
            logger.error("Fix sem seletor alvo")
            return None
        
        return self.locate_file_for_selector(selector)
    
    def get_all_css_files(self) -> List[Dict]:
        """Retorna lista de todos os arquivos CSS."""
        css_files = self.project_config.get_css_files()
        
        return [
            {
                "file_path": str(f),
                "relative_path": str(f.relative_to(self.project_config.root_path)),
                "exists": f.exists()
            }
            for f in css_files
        ]

