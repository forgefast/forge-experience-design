"""
Source Code Analyzer

Analisa estrutura de arquivos do projeto alvo.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
import re

from ...config.project_config import ProjectConfig

logger = logging.getLogger(__name__)


class SourceAnalyzer:
    """Analisador de código-fonte."""
    
    def __init__(self, project_config: ProjectConfig):
        self.project_config = project_config
        logger.info(f"SourceAnalyzer inicializado para projeto: {project_config.project_id}")
    
    def analyze_css_structure(self) -> Dict[str, List[Dict]]:
        """
        Analisa estrutura de arquivos CSS.
        
        Returns:
            Dict com informações sobre cada arquivo CSS:
            {
                "file_path": str,
                "selectors": List[Dict],  # [{selector: str, line: int, properties: List[str]}]
                "imports": List[str],
                "variables": List[str]
            }
        """
        css_files = self.project_config.get_css_files()
        structure = {}
        
        for css_file in css_files:
            try:
                content = css_file.read_text(encoding='utf-8')
                selectors = self._extract_selectors(content, css_file)
                imports = self._extract_imports(content)
                variables = self._extract_css_variables(content)
                
                structure[str(css_file.relative_to(self.project_config.root_path))] = {
                    "file_path": str(css_file),
                    "relative_path": str(css_file.relative_to(self.project_config.root_path)),
                    "selectors": selectors,
                    "imports": imports,
                    "variables": variables,
                    "line_count": len(content.splitlines())
                }
            except Exception as e:
                logger.error(f"Erro ao analisar {css_file}: {e}")
                continue
        
        return structure
    
    def _extract_selectors(self, content: str, file_path: Path) -> List[Dict]:
        """Extrai seletores CSS do conteúdo."""
        selectors = []
        lines = content.splitlines()
        
        # Regex para seletores CSS (simplificado)
        selector_pattern = re.compile(r'^([^{]+)\s*\{', re.MULTILINE)
        
        for match in selector_pattern.finditer(content):
            selector_text = match.group(1).strip()
            # Remover comentários
            selector_text = re.sub(r'/\*.*?\*/', '', selector_text, flags=re.DOTALL).strip()
            
            if not selector_text or selector_text.startswith('@'):
                continue
            
            # Calcular linha
            line_number = content[:match.start()].count('\n') + 1
            
            # Extrair propriedades dentro do bloco
            start_pos = match.end()
            brace_count = 1
            end_pos = start_pos
            
            while end_pos < len(content) and brace_count > 0:
                if content[end_pos] == '{':
                    brace_count += 1
                elif content[end_pos] == '}':
                    brace_count -= 1
                end_pos += 1
            
            block_content = content[start_pos:end_pos-1]
            properties = self._extract_properties(block_content)
            
            selectors.append({
                "selector": selector_text,
                "line": line_number,
                "properties": properties,
                "block_start": start_pos,
                "block_end": end_pos - 1
            })
        
        return selectors
    
    def _extract_properties(self, block_content: str) -> List[str]:
        """Extrai propriedades CSS de um bloco."""
        properties = []
        # Regex para propriedades CSS
        prop_pattern = re.compile(r'([a-zA-Z-]+)\s*:\s*([^;]+);')
        
        for match in prop_pattern.finditer(block_content):
            prop_name = match.group(1).strip()
            properties.append(prop_name)
        
        return properties
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extrai imports CSS."""
        imports = []
        import_pattern = re.compile(r'@import\s+["\']([^"\']+)["\']', re.IGNORECASE)
        
        for match in import_pattern.finditer(content):
            imports.append(match.group(1))
        
        return imports
    
    def _extract_css_variables(self, content: str) -> List[str]:
        """Extrai variáveis CSS (custom properties)."""
        variables = []
        var_pattern = re.compile(r'--([a-zA-Z0-9-]+)\s*:', re.IGNORECASE)
        
        for match in var_pattern.finditer(content):
            variables.append(f"--{match.group(1)}")
        
        return variables
    
    def find_selector_in_files(self, selector: str) -> List[Dict]:
        """
        Encontra seletor em arquivos CSS.
        
        Args:
            selector: Seletor CSS a procurar (ex: ".btn-base")
        
        Returns:
            Lista de ocorrências: [{file_path, line, selector_info}]
        """
        structure = self.analyze_css_structure()
        matches = []
        
        # Normalizar seletor (remover espaços extras)
        selector = selector.strip()
        
        for file_path, file_info in structure.items():
            for sel_info in file_info["selectors"]:
                # Verificar se seletor corresponde (exato ou parcial)
                if self._selector_matches(sel_info["selector"], selector):
                    matches.append({
                        "file_path": file_info["file_path"],
                        "relative_path": file_info["relative_path"],
                        "line": sel_info["line"],
                        "selector": sel_info["selector"],
                        "properties": sel_info["properties"]
                    })
        
        return matches
    
    def _selector_matches(self, file_selector: str, target_selector: str) -> bool:
        """Verifica se seletor do arquivo corresponde ao alvo."""
        # Normalizar
        file_selector = file_selector.strip()
        target_selector = target_selector.strip()
        
        # Correspondência exata
        if file_selector == target_selector:
            return True
        
        # Correspondência parcial (ex: ".btn-base" em ".btn-base:hover")
        if target_selector in file_selector:
            return True
        
        # Correspondência de classe (ex: "btn-base" em ".btn-base")
        file_classes = re.findall(r'\.([a-zA-Z0-9_-]+)', file_selector)
        target_classes = re.findall(r'\.([a-zA-Z0-9_-]+)', target_selector)
        
        if target_classes and any(tc in file_classes for tc in target_classes):
            return True
        
        return False
    
    def get_file_content(self, relative_path: str) -> Optional[str]:
        """Obtém conteúdo de um arquivo."""
        file_path = self.project_config.root_path / relative_path
        
        if not self.project_config.validate_path(file_path):
            logger.error(f"Caminho inválido: {relative_path}")
            return None
        
        try:
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {relative_path}: {e}")
            return None

