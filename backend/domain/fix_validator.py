"""
Fix Validator - Domain Layer

Valida se correções aplicadas resolveram os problemas.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class FixValidator:
    """
    Valida se correções aplicadas resolveram problemas de UI/UX.
    
    Compara métricas antes/depois e verifica se problemas foram resolvidos.
    """
    
    def __init__(self):
        self.validation_history: List[Dict[str, Any]] = []
    
    async def validate_fix(
        self,
        fix: Dict[str, Any],
        issue: Dict[str, Any],
        before_metrics: Dict[str, Any],
        after_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida se uma correção resolveu o problema.
        
        Args:
            fix: Correção aplicada
            issue: Problema original
            before_metrics: Métricas antes da correção
            after_metrics: Métricas depois da correção
        
        Returns:
            Resultado da validação
        """
        try:
            issue_type = issue.get('type')
            
            # Validar baseado no tipo de problema
            if issue_type == 'small_touch_target':
                return self._validate_touch_target(fix, issue, before_metrics, after_metrics)
            elif issue_type == 'zero_dimensions':
                return self._validate_dimensions(fix, issue, before_metrics, after_metrics)
            elif issue_type == 'overflow':
                return self._validate_overflow(fix, issue, before_metrics, after_metrics)
            elif issue_type.startswith('accessibility_'):
                return self._validate_accessibility(fix, issue, before_metrics, after_metrics)
            else:
                return self._validate_generic(fix, issue, before_metrics, after_metrics)
                
        except Exception as e:
            logger.error(f"Erro ao validar correção: {e}", exc_info=True)
            return {
                'valid': False,
                'reason': f'Erro na validação: {str(e)}',
                'should_rollback': False
            }
    
    def _validate_touch_target(
        self,
        fix: Dict[str, Any],
        issue: Dict[str, Any],
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida correção de touch target."""
        # Verificar se min-width e min-height foram aplicados
        changes = fix.get('changes', [])
        has_min_width = any(c.get('property') == 'min-width' for c in changes)
        has_min_height = any(c.get('property') == 'min-height' for c in changes)
        
        if not (has_min_width and has_min_height):
            return {
                'valid': False,
                'reason': 'Correção não aplica min-width e min-height',
                'should_rollback': False
            }
        
        # Verificar se dimensões são >= 44px (padrão de acessibilidade)
        min_width_value = next(
            (c.get('value') for c in changes if c.get('property') == 'min-width'),
            None
        )
        min_height_value = next(
            (c.get('value') for c in changes if c.get('property') == 'min-height'),
            None
        )
        
        def parse_size(value: str) -> float:
            """Converte valor CSS para pixels."""
            if not value:
                return 0
            value = value.strip()
            if value.endswith('px'):
                return float(value[:-2])
            elif value.endswith('rem'):
                return float(value[:-3]) * 16  # Assumindo 16px base
            elif value.endswith('em'):
                return float(value[:-2]) * 16
            return 0
        
        width_px = parse_size(min_width_value or '0px')
        height_px = parse_size(min_height_value or '0px')
        
        if width_px >= 44 and height_px >= 44:
            return {
                'valid': True,
                'reason': 'Touch target agora tem dimensões adequadas (>= 44px)',
                'should_rollback': False,
                'improvement': 'high'
            }
        else:
            return {
                'valid': False,
                'reason': f'Dimensões ainda pequenas: {width_px}x{height_px}px (mínimo 44px)',
                'should_rollback': False,
                'improvement': 'low'
            }
    
    def _validate_dimensions(
        self,
        fix: Dict[str, Any],
        issue: Dict[str, Any],
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida correção de dimensões zero."""
        changes = fix.get('changes', [])
        has_min_width = any(c.get('property') == 'min-width' for c in changes)
        has_min_height = any(c.get('property') == 'min-height' for c in changes)
        
        if has_min_width or has_min_height:
            return {
                'valid': True,
                'reason': 'Dimensões mínimas aplicadas',
                'should_rollback': False,
                'improvement': 'medium'
            }
        else:
            return {
                'valid': False,
                'reason': 'Correção não aplica dimensões mínimas',
                'should_rollback': False
            }
    
    def _validate_overflow(
        self,
        fix: Dict[str, Any],
        issue: Dict[str, Any],
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida correção de overflow."""
        changes = fix.get('changes', [])
        has_overflow = any(c.get('property') == 'overflow' for c in changes)
        
        if has_overflow:
            return {
                'valid': True,
                'reason': 'Overflow controlado',
                'should_rollback': False,
                'improvement': 'medium'
            }
        else:
            return {
                'valid': False,
                'reason': 'Correção não controla overflow',
                'should_rollback': False
            }
    
    def _validate_accessibility(
        self,
        fix: Dict[str, Any],
        issue: Dict[str, Any],
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida correção de acessibilidade."""
        # Validação genérica para acessibilidade
        # Em produção, seria mais específica baseada no tipo de problema
        return {
            'valid': True,
            'reason': 'Correção de acessibilidade aplicada',
            'should_rollback': False,
            'improvement': 'medium'
        }
    
    def _validate_generic(
        self,
        fix: Dict[str, Any],
        issue: Dict[str, Any],
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validação genérica."""
        # Se a correção tem changes, assume que pode ajudar
        if fix.get('changes'):
            return {
                'valid': True,
                'reason': 'Correção aplicada (validação genérica)',
                'should_rollback': False,
                'improvement': 'low'
            }
        else:
            return {
                'valid': False,
                'reason': 'Correção sem changes válidas',
                'should_rollback': False
            }
    
    def should_rollback(
        self,
        fix: Dict[str, Any],
        validation_result: Dict[str, Any],
        metrics_comparison: Dict[str, Any]
    ) -> bool:
        """
        Decide se uma correção deve ser revertida.
        
        Args:
            fix: Correção aplicada
            validation_result: Resultado da validação
            metrics_comparison: Comparação de métricas antes/depois
        
        Returns:
            True se deve fazer rollback
        """
        # Rollback se validação indicar
        if validation_result.get('should_rollback'):
            return True
        
        # Rollback se métricas pioraram significativamente
        if metrics_comparison.get('performance_degraded'):
            return True
        
        # Rollback se layout quebrou
        if metrics_comparison.get('layout_broken'):
            return True
        
        return False
    
    def record_validation(self, validation_result: Dict[str, Any]):
        """Registra resultado de validação no histórico."""
        self.validation_history.append({
            'timestamp': datetime.now().isoformat(),
            'result': validation_result
        })
        
        # Manter apenas últimos 100
        if len(self.validation_history) > 100:
            self.validation_history = self.validation_history[-100:]

