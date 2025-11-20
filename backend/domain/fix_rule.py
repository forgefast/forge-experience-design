"""
Fix Rules
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class FixRule:
    """Regra de correção"""
    id: str
    name: str
    description: str
    issue_type: str  # Tipo de problema que a regra corrige
    priority: int  # Prioridade (1-10, maior = mais importante)
    enabled: bool = True  # Deve ser o último campo com valor padrão
    
    def matches(self, issue: Dict[str, Any]) -> bool:
        """Verifica se a regra se aplica ao problema"""
        return issue.get('type') == self.issue_type
    
    def generate_fix(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Gera correção para o problema"""
        raise NotImplementedError


@dataclass
class CSSFixRule(FixRule):
    """Regra de correção CSS"""
    target_selector: str = ''
    css_properties: Dict[str, str] = field(default_factory=dict)  # property -> value
    
    def generate_fix(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Gera correção CSS"""
        # Tentar obter elemento do issue
        element = issue.get('element', '') or issue.get('target_element', '')
        
        # Se não tiver elemento específico, usar seletor genérico
        if not element and self.target_selector:
            element = self.target_selector
        
        if not element:
            return None
        
        return {
            'type': 'css',
            'target_element': element,
            'target_selector': self.target_selector,
            'changes': [
                {
                    'property': prop,
                    'value': value,
                    'reason': f'Corrigir {self.issue_type}'
                }
                for prop, value in self.css_properties.items()
            ]
        }


# Regras predefinidas
FIX_RULES: List[FixRule] = [
    # Regras existentes
    CSSFixRule(
        id='small_touch_target',
        name='Aumentar tamanho de botões',
        description='Aumenta tamanho de botões abaixo de 44x44px',
        issue_type='small_touch_target',
        priority=9,
        target_selector='button, [role="button"]',
        css_properties={
            'min-width': '44px',
            'min-height': '44px',
            'padding': '12px 16px'
        }
    ),
    CSSFixRule(
        id='zero_dimensions',
        name='Corrigir dimensões zero',
        description='Corrige elementos com dimensões zero',
        issue_type='zero_dimensions',
        priority=8,
        target_selector='*',
        css_properties={
            'min-width': '1px',
            'min-height': '1px'
        }
    ),
    CSSFixRule(
        id='overflow',
        name='Corrigir overflow',
        description='Adiciona overflow hidden para evitar conteúdo saindo',
        issue_type='overflow',
        priority=7,
        target_selector='*',
        css_properties={
            'overflow': 'hidden'
        }
    ),
    
    # Acessibilidade
    CSSFixRule(
        id='low_contrast',
        name='Melhorar contraste de texto',
        description='Aumenta contraste de texto para melhorar legibilidade',
        issue_type='accessibility_low_contrast',
        priority=9,
        target_selector='*',
        css_properties={
            'color': '#000000',
            'background-color': '#ffffff'
        }
    ),
    CSSFixRule(
        id='missing_focus_indicator',
        name='Adicionar indicador de foco',
        description='Adiciona outline visível para elementos focáveis',
        issue_type='accessibility_missing_focus',
        priority=8,
        target_selector='a, button, input, select, textarea, [tabindex]',
        css_properties={
            'outline': '2px solid #0066cc',
            'outline-offset': '2px'
        }
    ),
    CSSFixRule(
        id='small_text',
        name='Aumentar tamanho de texto pequeno',
        description='Aumenta tamanho mínimo de texto para legibilidade',
        issue_type='accessibility_small_text',
        priority=7,
        target_selector='p, span, div, li',
        css_properties={
            'font-size': '16px',
            'line-height': '1.5'
        }
    ),
    CSSFixRule(
        id='missing_aria_label',
        name='Adicionar aria-label para elementos interativos',
        description='Melhora acessibilidade para leitores de tela',
        issue_type='accessibility_missing_aria_label',
        priority=6,
        target_selector='button, a, input',
        css_properties={
            'aria-label': 'Elemento interativo'
        }
    ),
    
    # Responsividade
    CSSFixRule(
        id='fixed_width',
        name='Tornar largura responsiva',
        description='Substitui largura fixa por max-width para responsividade',
        issue_type='responsive_fixed_width',
        priority=8,
        target_selector='*',
        css_properties={
            'max-width': '100%',
            'width': 'auto'
        }
    ),
    CSSFixRule(
        id='missing_viewport_meta',
        name='Adicionar viewport responsivo',
        description='Garante que página seja responsiva',
        issue_type='responsive_missing_viewport',
        priority=7,
        target_selector='body',
        css_properties={
            'min-width': '320px'
        }
    ),
    CSSFixRule(
        id='overflow_mobile',
        name='Corrigir overflow em mobile',
        description='Previne overflow horizontal em dispositivos móveis',
        issue_type='responsive_overflow',
        priority=8,
        target_selector='body, main, .container',
        css_properties={
            'overflow-x': 'hidden',
            'max-width': '100vw'
        }
    ),
    
    # Visual/Design
    CSSFixRule(
        id='poor_spacing',
        name='Melhorar espaçamento',
        description='Adiciona espaçamento adequado entre elementos',
        issue_type='visual_poor_spacing',
        priority=6,
        target_selector='p, div, section',
        css_properties={
            'margin-bottom': '1rem',
            'padding': '0.5rem'
        }
    ),
    CSSFixRule(
        id='misaligned_elements',
        name='Alinhar elementos',
        description='Corrige alinhamento de elementos',
        issue_type='visual_misalignment',
        priority=5,
        target_selector='*',
        css_properties={
            'box-sizing': 'border-box'
        }
    ),
    CSSFixRule(
        id='poor_typography',
        name='Melhorar tipografia',
        description='Ajusta hierarquia tipográfica',
        issue_type='visual_poor_typography',
        priority=6,
        target_selector='h1, h2, h3, h4, h5, h6',
        css_properties={
            'font-weight': 'bold',
            'line-height': '1.2',
            'margin-top': '1.5rem',
            'margin-bottom': '0.5rem'
        }
    ),
    CSSFixRule(
        id='broken_images',
        name='Corrigir imagens quebradas',
        description='Adiciona fallback para imagens quebradas',
        issue_type='visual_broken_image',
        priority=7,
        target_selector='img',
        css_properties={
            'object-fit': 'cover',
            'max-width': '100%',
            'height': 'auto'
        }
    ),
    CSSFixRule(
        id='poor_button_styling',
        name='Melhorar estilo de botões',
        description='Aplica estilos consistentes a botões',
        issue_type='visual_poor_button_styling',
        priority=6,
        target_selector='button, .btn, [type="submit"]',
        css_properties={
            'cursor': 'pointer',
            'border-radius': '4px',
            'transition': 'all 0.2s ease'
        }
    ),
    CSSFixRule(
        id='z_index_issues',
        name='Corrigir sobreposição de elementos',
        description='Ajusta z-index para evitar sobreposição incorreta',
        issue_type='visual_z_index',
        priority=7,
        target_selector='*',
        css_properties={
            'position': 'relative',
            'z-index': '1'
        }
    ),
]

