"""
CSS Modifier

Modifica arquivos CSS usando AST.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import re

from ...config.project_config import ProjectConfig

logger = logging.getLogger(__name__)


class CSSModifier:
    """Modificador de arquivos CSS."""
    
    def __init__(self, project_config: ProjectConfig):
        self.project_config = project_config
        logger.info(f"CSSModifier inicializado para projeto: {project_config.project_id}")
    
    def modify_css_file(
        self,
        file_path: str,
        selector: str,
        changes: List[Dict],
        preserve_formatting: bool = True
    ) -> Dict:
        """
        Modifica arquivo CSS.
        
        Args:
            file_path: Caminho relativo do arquivo
            selector: Seletor CSS a modificar
            changes: Lista de mudanças: [{"property": str, "value": str, "action": str}]
            preserve_formatting: Preservar formatação original
        
        Returns:
            Dict com resultado:
            {
                "success": bool,
                "original_content": str,
                "modified_content": str,
                "changes_applied": List[Dict],
                "errors": List[str]
            }
        """
        full_path = self.project_config.root_path / file_path
        
        if not self.project_config.validate_path(full_path):
            return {
                "success": False,
                "errors": [f"Caminho inválido: {file_path}"]
            }
        
        try:
            # Ler conteúdo original
            original_content = full_path.read_text(encoding='utf-8')
            
            # Modificar usando regex (mais simples e preserva formatação)
            modified_content, changes_applied, errors = self._modify_with_regex(
                original_content,
                selector,
                changes
            )
            
            return {
                "success": len(errors) == 0,
                "original_content": original_content,
                "modified_content": modified_content,
                "changes_applied": changes_applied,
                "errors": errors
            }
        
        except Exception as e:
            logger.error(f"Erro ao modificar CSS: {e}")
            return {
                "success": False,
                "errors": [str(e)]
            }
    
    def _modify_with_regex(
        self,
        content: str,
        selector: str,
        changes: List[Dict]
    ) -> tuple:
        """
        Modifica CSS usando regex (preserva formatação).
        
        Returns:
            (modified_content, changes_applied, errors)
        """
        modified = content
        changes_applied = []
        errors = []
        
        # Normalizar seletor
        selector = selector.strip()
        
        # Se seletor for genérico (ex: "button, [role=\"button\"]"), 
        # tentar encontrar seletor mais específico no arquivo
        if "," in selector or selector in ["button", "[role=\"button\"]"]:
            # Procurar por seletores de botão no arquivo
            button_patterns = [
                r'\.btn-base\s*\{',
                r'\.btn-primary\s*\{',
                r'\.btn-secondary\s*\{',
                r'button\s*\{',
                r'\[role=["\']button["\']\]\s*\{'
            ]
            
            match = None
            for pattern in button_patterns:
                match = re.search(pattern, modified, re.MULTILINE)
                if match:
                    # Encontrar início do seletor completo
                    start = match.start()
                    # Encontrar início da linha
                    line_start = modified.rfind('\n', 0, start) + 1
                    # Encontrar fim do seletor (até {)
                    brace_pos = modified.find('{', start)
                    if brace_pos > 0:
                        actual_selector = modified[line_start:brace_pos].strip()
                        selector = actual_selector
                        break
            
            if not match:
                errors.append(f"Seletor genérico não encontrado no arquivo: {selector}")
                return modified, changes_applied, errors
        
        selector_escaped = re.escape(selector)
        
        # Encontrar bloco do seletor
        # Padrão: selector { ... }
        pattern = rf'({selector_escaped})\s*\{{([^}}]*(?:\{{[^}}]*\}}[^}}]*)*)\}}'
        
        match = re.search(pattern, modified, re.MULTILINE | re.DOTALL)
        
        if not match:
            errors.append(f"Seletor não encontrado: {selector}")
            return modified, changes_applied, errors
        
        selector_text = match.group(1)
        block_content = match.group(2)
        block_start = match.start(2)
        block_end = match.end(2)
        
        # Modificar propriedades no bloco
        modified_block = block_content
        
        for change in changes:
            property_name = change.get("property", "").strip()
            property_value = change.get("value", "").strip()
            action = change.get("action", "modify").lower()
            
            if not property_name:
                errors.append("Propriedade não especificada")
                continue
            
            # Escapar nome da propriedade
            prop_escaped = re.escape(property_name)
            
            # Padrão para propriedade CSS
            prop_pattern = rf'({prop_escaped})\s*:\s*([^;]+);'
            
            prop_match = re.search(prop_pattern, modified_block)
            
            if action == "modify":
                if prop_match:
                    # Modificar propriedade existente
                    old_value = prop_match.group(2).strip()
                    new_prop = f"{property_name}: {property_value};"
                    modified_block = modified_block[:prop_match.start()] + new_prop + modified_block[prop_match.end():]
                    changes_applied.append({
                        "property": property_name,
                        "action": "modified",
                        "old_value": old_value,
                        "new_value": property_value
                    })
                else:
                    # Adicionar nova propriedade
                    # Adicionar no final do bloco (antes do })
                    if modified_block.strip():
                        modified_block = modified_block.rstrip() + f"\n  {property_name}: {property_value};"
                    else:
                        modified_block = f"  {property_name}: {property_value};"
                    changes_applied.append({
                        "property": property_name,
                        "action": "added",
                        "new_value": property_value
                    })
            
            elif action == "add":
                if not prop_match:
                    # Adicionar nova propriedade
                    if modified_block.strip():
                        modified_block = modified_block.rstrip() + f"\n  {property_name}: {property_value};"
                    else:
                        modified_block = f"  {property_name}: {property_value};"
                    changes_applied.append({
                        "property": property_name,
                        "action": "added",
                        "new_value": property_value
                    })
                else:
                    errors.append(f"Propriedade já existe: {property_name}")
            
            elif action == "remove":
                if prop_match:
                    # Remover propriedade
                    # Remover linha inteira incluindo quebra de linha anterior
                    start = prop_match.start()
                    # Encontrar início da linha
                    line_start = modified_block.rfind('\n', 0, start) + 1
                    # Encontrar fim da linha (incluindo ;)
                    line_end = modified_block.find(';', start) + 1
                    # Remover espaços em branco antes
                    while line_start > 0 and modified_block[line_start-1] in ' \t':
                        line_start -= 1
                    # Remover quebra de linha após se houver
                    if line_end < len(modified_block) and modified_block[line_end] == '\n':
                        line_end += 1
                    
                    modified_block = modified_block[:line_start] + modified_block[line_end:]
                    changes_applied.append({
                        "property": property_name,
                        "action": "removed"
                    })
                else:
                    errors.append(f"Propriedade não encontrada: {property_name}")
        
        # Reconstruir CSS
        modified = (
            modified[:match.start()] +
            f"{selector_text} {{\n{modified_block}\n}}" +
            modified[match.end():]
        )
        
        return modified, changes_applied, errors
    
    def validate_css(self, content: str) -> tuple:
        """
        Valida sintaxe CSS básica.
        
        Returns:
            (is_valid, errors)
        """
        try:
            # Validação básica: verificar se há chaves balanceadas
            open_braces = content.count('{')
            close_braces = content.count('}')
            
            if open_braces != close_braces:
                return False, [f"Chaves desbalanceadas: {open_braces} abertas, {close_braces} fechadas"]
            
            # Verificar se há seletores e propriedades básicas
            if not re.search(r'[^{}]+{[^}]+}', content):
                return False, ["Nenhuma regra CSS válida encontrada"]
            
            return True, []
        except Exception as e:
            return False, [str(e)]

