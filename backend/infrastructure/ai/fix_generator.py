"""
Fix Generator - Infrastructure Layer

Gera correções inteligentes usando IA baseadas em contexto.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from .llm_service import LLMService
from .html_analyzer import HTMLAnalyzer

logger = logging.getLogger(__name__)


class FixGenerator:
    """
    Gera correções inteligentes usando IA.
    
    Analisa problemas de UI e gera correções CSS/JavaScript
    baseadas em contexto HTML e histórico.
    """
    
    def __init__(self, llm_service: LLMService, html_analyzer: HTMLAnalyzer):
        self.llm_service = llm_service
        self.html_analyzer = html_analyzer
    
    async def generate_fix(
        self,
        issue: Dict[str, Any],
        html_context: Optional[str] = None,
        fix_history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Gera uma correção para um problema de UI usando IA.
        
        Args:
            issue: Dados do problema detectado
            html_context: HTML do elemento ou página
            fix_history: Histórico de correções similares
        
        Returns:
            Dicionário com correção gerada ou None
        """
        try:
            # Preparar contexto para a IA
            context = self._prepare_context(issue, html_context, fix_history)
            
            # Gerar prompt para a IA
            prompt = self._generate_prompt(issue, context)
            
            # Obter resposta da IA
            ai_response = await self.llm_service.generate(prompt, context)
            
            # Parsear resposta da IA
            fix = self._parse_ai_response(ai_response, issue)
            
            if fix:
                logger.info(f"Correção gerada pela IA para problema: {issue.get('type')}")
                return fix
            else:
                logger.warning(f"IA não retornou correção válida para: {issue.get('type')}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao gerar correção com IA: {e}", exc_info=True)
            return None
    
    def _prepare_context(
        self,
        issue: Dict[str, Any],
        html_context: Optional[str],
        fix_history: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Prepara contexto para a IA."""
        context = {
            "issue_type": issue.get('type'),
            "issue_message": issue.get('message'),
            "issue_severity": issue.get('severity'),
            "element": issue.get('element'),
            "issue_details": issue.get('details', {})
        }
        
        # Adicionar contexto HTML se disponível
        if html_context:
            analyzed_html = self.html_analyzer.analyze_html(html_context)
            context["html_analysis"] = analyzed_html
            
            # Se tiver seletor, obter contexto específico do elemento
            element_selector = issue.get('element')
            if element_selector:
                element_context = self.html_analyzer.get_element_context(html_context, element_selector)
                if element_context:
                    context["element_context"] = element_context
        
        # Adicionar histórico de correções similares
        if fix_history:
            similar_fixes = [
                fix for fix in fix_history
                if fix.get('issue_type') == issue.get('type')
            ][:5]  # Últimas 5 correções similares
            context["similar_fixes"] = similar_fixes
        
        return context
    
    def _generate_prompt(self, issue: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Gera prompt para a IA."""
        issue_type = issue.get('type', 'unknown')
        issue_message = issue.get('message', '')
        element = issue.get('element', '')
        
        prompt = f"""Você é um especialista em UI/UX que corrige problemas de interface automaticamente.

PROBLEMA DETECTADO:
- Tipo: {issue_type}
- Mensagem: {issue_message}
- Elemento: {element}
- Severidade: {issue.get('severity', 'medium')}

CONTEXTO:
"""
        
        if context.get('html_analysis'):
            prompt += f"- Análise HTML: {len(context['html_analysis'].get('elements', []))} elementos interativos encontrados\n"
        
        if context.get('element_context'):
            prompt += f"- Contexto do elemento: {json.dumps(context['element_context'], indent=2)}\n"
        
        if context.get('similar_fixes'):
            prompt += f"- Correções similares anteriores: {len(context['similar_fixes'])} encontradas\n"
        
        prompt += """
TAREFA:
Gere uma correção CSS válida para resolver este problema. A correção deve:
1. Ser específica para o elemento afetado
2. Resolver o problema sem quebrar o layout
3. Seguir melhores práticas de CSS
4. Usar !important apenas quando necessário

FORMATO DE RESPOSTA (JSON):
{
  "type": "css",
  "target_element": "seletor CSS do elemento",
  "target_selector": "seletor CSS mais específico (opcional)",
  "changes": [
    {
      "property": "nome-da-propriedade-css",
      "value": "valor da propriedade",
      "reason": "explicação do porquê esta correção resolve o problema"
    }
  ],
  "confidence": 0.0-1.0
}

IMPORTANTE:
- Retorne APENAS o JSON, sem markdown ou texto adicional
- Use seletores CSS válidos
- Valores CSS devem ser válidos
- Se não conseguir gerar uma correção válida, retorne null
"""
        
        return prompt
    
    def _parse_ai_response(self, ai_response: str, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parseia resposta da IA e valida."""
        try:
            # Tentar extrair JSON da resposta
            # A IA pode retornar JSON dentro de markdown ou texto
            json_str = ai_response.strip()
            
            # Remover markdown code blocks se houver
            if json_str.startswith('```'):
                lines = json_str.split('\n')
                json_str = '\n'.join(lines[1:-1]) if lines[-1].strip() == '```' else json_str
            
            # Parsear JSON
            fix_data = json.loads(json_str)
            
            # Validar estrutura
            if not isinstance(fix_data, dict):
                return None
            
            if fix_data.get('type') != 'css':
                logger.warning(f"Tipo de correção não suportado: {fix_data.get('type')}")
                return None
            
            if not fix_data.get('target_element'):
                logger.warning("Correção sem target_element")
                return None
            
            if not fix_data.get('changes') or not isinstance(fix_data['changes'], list):
                logger.warning("Correção sem changes válidas")
                return None
            
            # Validar cada change
            valid_changes = []
            for change in fix_data['changes']:
                if isinstance(change, dict) and change.get('property') and change.get('value'):
                    valid_changes.append({
                        'property': change['property'],
                        'value': change['value'],
                        'reason': change.get('reason', 'Correção gerada por IA')
                    })
            
            if not valid_changes:
                logger.warning("Nenhuma change válida na correção")
                return None
            
            # Retornar correção validada
            return {
                'type': 'css',
                'target_element': fix_data['target_element'],
                'target_selector': fix_data.get('target_selector'),
                'changes': valid_changes,
                'confidence': fix_data.get('confidence', 0.7),
                'generated_by': 'ai',
                'issue_type': issue.get('type')
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao parsear JSON da IA: {e}. Resposta: {ai_response[:200]}")
            return None
        except Exception as e:
            logger.error(f"Erro ao validar resposta da IA: {e}", exc_info=True)
            return None

