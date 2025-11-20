"""
Fix Engine
"""

from typing import List, Dict, Any, Optional
from .fix_rule import FixRule, FIX_RULES
from ..infrastructure.forge_logs_client import ForgeLogsClient
from ..infrastructure.ai.fix_generator import FixGenerator
from ..infrastructure.storage.fix_repository import FixRepository


class FixEngine:
    """Motor de correção"""
    
    def __init__(
        self,
        forge_logs_client: ForgeLogsClient,
        fix_generator: Optional[FixGenerator] = None,
        fix_repository: Optional[FixRepository] = None
    ):
        self.forge_logs_client = forge_logs_client
        self.rules = FIX_RULES
        self.fix_generator = fix_generator
        self.fix_repository = fix_repository
    
    async def analyze_and_generate_fixes(
        self,
        application_id: str,
        limit: int = 100,
        use_ai: bool = False
    ) -> List[Dict[str, Any]]:
        """Analisa logs e gera correções"""
        # Obter problemas de UI
        ui_issues = await self.forge_logs_client.get_ui_issues(
            application_id=application_id,
            severity='high',
            limit=limit
        )
        
        fixes = []
        
        # Obter histórico de correções se disponível
        fix_history = []
        if self.fix_repository:
            try:
                fix_history = await self.fix_repository.list_fixes(limit=50)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Erro ao obter histórico: {e}")
        
        # Para cada problema, tentar aplicar regras ou IA
        for issue in ui_issues:
            issue_data = issue.get('data', {})
            issue_type = issue_data.get('type')
            
            if not issue_type:
                continue
            
            fix = None
            
            # Tentar usar IA primeiro se disponível e habilitado
            if use_ai and self.fix_generator:
                try:
                    html_context = issue_data.get('html') or issue_data.get('element_html')
                    fix = await self.fix_generator.generate_fix(
                        issue=issue_data,
                        html_context=html_context,
                        fix_history=fix_history
                    )
                    if fix:
                        fix['generated_by'] = 'ai'
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).warning(f"Erro ao gerar correção com IA: {e}")
            
            # Se IA não gerou, tentar regras fixas
            if not fix:
                for rule in self.rules:
                    if not rule.enabled:
                        continue
                    
                    if rule.matches({'type': issue_type}):
                        fix = rule.generate_fix(issue_data)
                        if fix:
                            fix['generated_by'] = 'rule'
                        break
            
            if fix:
                fix['log_entry_id'] = issue.get('id')
                fix['issue'] = issue_data
                fix['issue_type'] = issue_type
                if 'priority' not in fix:
                    fix['priority'] = 5  # Prioridade padrão
                fixes.append(fix)
        
        # Ordenar por prioridade
        fixes.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return fixes
    
    def get_rules(self) -> List[FixRule]:
        """Obtém todas as regras"""
        return self.rules
    
    def enable_rule(self, rule_id: str):
        """Habilita regra"""
        for rule in self.rules:
            if rule.id == rule_id:
                rule.enabled = True
                break
    
    def disable_rule(self, rule_id: str):
        """Desabilita regra"""
        for rule in self.rules:
            if rule.id == rule_id:
                rule.enabled = False
                break

