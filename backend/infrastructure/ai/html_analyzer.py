"""
HTML Analyzer - Infrastructure Layer

Analisa HTML para extrair contexto de elementos e problemas de UI.
"""

import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HTMLAnalyzer:
    """
    Analisa HTML e extrai informações relevantes para correções de UI/UX.
    """
    
    def __init__(self):
        pass
    
    def analyze_html(self, html_content: str) -> Dict[str, Any]:
        """
        Analisa o conteúdo HTML e retorna uma estrutura de dados com elementos interativos.
        """
        if not html_content:
            return {"elements": []}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            elements = []
            
            # Extrair botões
            for button in soup.find_all(['button', 'a', 'input'], type=['submit', 'button', 'reset', None]):
                element_info = self._extract_element_info(button, "button")
                if element_info:
                    elements.append(element_info)
            
            # Extrair campos de input
            for input_field in soup.find_all(['input', 'textarea', 'select']):
                element_info = self._extract_element_info(input_field, "input")
                if element_info:
                    elements.append(element_info)
            
            # Extrair links
            for link in soup.find_all('a', href=True):
                element_info = self._extract_element_info(link, "link")
                if element_info:
                    elements.append(element_info)
            
            # Extrair elementos com problemas potenciais
            problematic_elements = self._find_problematic_elements(soup)
            
            logger.debug(f"HTML analisado. Encontrados {len(elements)} elementos interativos e {len(problematic_elements)} elementos problemáticos.")
            
            return {
                "elements": elements,
                "problematic_elements": problematic_elements
            }
        except Exception as e:
            logger.error(f"Erro ao analisar HTML: {e}", exc_info=True)
            return {"elements": [], "problematic_elements": []}
    
    def _extract_element_info(self, tag, element_type: str) -> Optional[Dict[str, Any]]:
        """Extrai informações de um elemento HTML."""
        info = {
            "type": element_type,
            "tag": tag.name,
            "text": tag.get_text(strip=True),
            "id": tag.get('id'),
            "name": tag.get('name'),
            "class": tag.get('class'),
            "placeholder": tag.get('placeholder'),
            "aria_label": tag.get('aria-label'),
            "role": tag.get('role'),
            "value": tag.get('value'),
            "href": tag.get('href') if tag.name == 'a' else None,
        }
        
        # Remover None values e listas vazias
        return {k: v for k, v in info.items() if v is not None and v != []}
    
    def _find_problematic_elements(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Encontra elementos com problemas potenciais de UI/UX."""
        problematic = []
        
        # Elementos sem texto mas clicáveis
        for element in soup.find_all(['button', 'a']):
            text = element.get_text(strip=True)
            aria_label = element.get('aria-label')
            if not text and not aria_label:
                problematic.append({
                    "type": "missing_label",
                    "element": str(element),
                    "tag": element.name,
                    "selector": self._generate_selector(element)
                })
        
        # Botões muito pequenos (detectado via estilo inline ou classe)
        for button in soup.find_all(['button', 'a', 'input'], type=['submit', 'button']):
            style = button.get('style', '')
            if 'width' in style or 'height' in style:
                # Verificar se tem dimensões pequenas (análise básica)
                if 'width: 20px' in style or 'height: 20px' in style:
                    problematic.append({
                        "type": "small_touch_target",
                        "element": str(button),
                        "tag": button.name,
                        "selector": self._generate_selector(button)
                    })
        
        # Elementos com overflow potencial
        for element in soup.find_all(attrs={'style': lambda x: x and 'overflow' in x}):
            problematic.append({
                "type": "overflow_issue",
                "element": str(element),
                "tag": element.name,
                "selector": self._generate_selector(element)
            })
        
        return problematic
    
    def _generate_selector(self, element) -> str:
        """Gera seletor CSS básico para um elemento."""
        selector_parts = []
        
        if element.get('id'):
            return f"#{element.get('id')}"
        
        if element.get('class'):
            classes = element.get('class')
            if isinstance(classes, list):
                classes = ' '.join(classes)
            return f".{classes.split()[0]}"
        
        return element.name
    
    def get_element_context(self, html_content: str, selector: str) -> Optional[Dict[str, Any]]:
        """
        Obtém contexto de um elemento específico pelo seletor.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            element = soup.select_one(selector)
            
            if not element:
                return None
            
            # Obter elemento pai e irmãos
            parent = element.parent if element.parent else None
            siblings = list(element.find_previous_siblings()) + list(element.find_next_siblings())
            
            context = {
                "element": self._extract_element_info(element, "unknown"),
                "parent": self._extract_element_info(parent, "parent") if parent else None,
                "siblings_count": len(siblings),
                "html_snippet": str(element)[:500]  # Primeiros 500 chars
            }
            
            return context
        except Exception as e:
            logger.error(f"Erro ao obter contexto do elemento: {e}", exc_info=True)
            return None

