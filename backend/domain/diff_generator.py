"""
Diff Generator

Gera diffs unificados para preview de mudanças.
"""

import logging
from typing import List, Dict, Optional
import difflib
from datetime import datetime

logger = logging.getLogger(__name__)


class DiffGenerator:
    """Gerador de diffs unificados."""
    
    def __init__(self):
        logger.info("DiffGenerator inicializado")
    
    def generate_unified_diff(
        self,
        original_content: str,
        modified_content: str,
        file_path: str,
        context_lines: int = 3
    ) -> str:
        """
        Gera diff unificado.
        
        Args:
            original_content: Conteúdo original
            modified_content: Conteúdo modificado
            file_path: Caminho do arquivo
            context_lines: Número de linhas de contexto
        
        Returns:
            Diff unificado (formato padrão)
        """
        original_lines = original_content.splitlines(keepends=True)
        modified_lines = modified_content.splitlines(keepends=True)
        
        # Gerar diff
        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm='',
            n=context_lines
        )
        
        return ''.join(diff)
    
    def generate_diff_for_fix(
        self,
        fix: Dict,
        original_content: str,
        modified_content: str,
        file_path: str
    ) -> Dict:
        """
        Gera diff para uma correção.
        
        Args:
            fix: Dict com informações da correção
            original_content: Conteúdo original
            modified_content: Conteúdo modificado
            file_path: Caminho do arquivo
        
        Returns:
            Dict com diff e metadados:
            {
                "diff": str,
                "file_path": str,
                "changes_summary": List[Dict],
                "line_count": int,
                "added_lines": int,
                "removed_lines": int
            }
        """
        diff_text = self.generate_unified_diff(
            original_content,
            modified_content,
            file_path
        )
        
        # Calcular estatísticas
        original_lines = original_content.splitlines()
        modified_lines = modified_content.splitlines()
        
        diff_lines = diff_text.splitlines()
        added = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        removed = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        # Resumo de mudanças
        changes_summary = []
        for change in fix.get("changes", []):
            changes_summary.append({
                "property": change.get("property"),
                "action": change.get("action", "modify"),
                "value": change.get("value")
            })
        
        return {
            "diff": diff_text,
            "file_path": file_path,
            "changes_summary": changes_summary,
            "line_count": len(modified_lines),
            "added_lines": added,
            "removed_lines": removed,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def format_diff_for_display(self, diff_text: str) -> List[Dict]:
        """
        Formata diff para exibição no frontend.
        
        Returns:
            Lista de linhas formatadas:
            [
                {
                    "line": int,
                    "type": "context" | "added" | "removed" | "header",
                    "content": str
                }
            ]
        """
        lines = diff_text.splitlines()
        formatted = []
        
        for i, line in enumerate(lines):
            if line.startswith('---') or line.startswith('+++'):
                formatted.append({
                    "line": i + 1,
                    "type": "header",
                    "content": line
                })
            elif line.startswith('@@'):
                formatted.append({
                    "line": i + 1,
                    "type": "header",
                    "content": line
                })
            elif line.startswith('+'):
                formatted.append({
                    "line": i + 1,
                    "type": "added",
                    "content": line[1:]  # Remover +
                })
            elif line.startswith('-'):
                formatted.append({
                    "line": i + 1,
                    "type": "removed",
                    "content": line[1:]  # Remover -
                })
            else:
                formatted.append({
                    "line": i + 1,
                    "type": "context",
                    "content": line
                })
        
        return formatted

