"""
LLM Service - Infrastructure Layer

Serviço para integração com LLM (OpenAI, Anthropic, etc.).
"""

import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMService(ABC):
    """Interface para serviços de LLM."""
    
    @abstractmethod
    async def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Gera resposta do LLM."""
        pass
    
    @abstractmethod
    async def generate_streaming(self, prompt: str, context: Optional[Dict[str, Any]] = None):
        """Gera resposta do LLM em streaming."""
        pass


class OpenAILLMService(LLMService):
    """Implementação usando OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Inicializa serviço OpenAI.
        
        Args:
            api_key: Chave da API OpenAI (ou usar variável de ambiente)
            model: Modelo a usar (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Obtém cliente OpenAI (lazy loading)."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package não instalado. Instale com: pip install openai")
        return self._client
    
    async def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Gera resposta do LLM."""
        try:
            client = self._get_client()
            
            messages = [{"role": "user", "content": prompt}]
            
            if context:
                # Adicionar contexto como mensagem do sistema
                context_str = self._format_context(context)
                messages.insert(0, {"role": "system", "content": context_str})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar resposta do LLM: {e}", exc_info=True)
            raise
    
    async def generate_streaming(self, prompt: str, context: Optional[Dict[str, Any]] = None):
        """Gera resposta do LLM em streaming."""
        try:
            client = self._get_client()
            
            messages = [{"role": "user", "content": prompt}]
            
            if context:
                context_str = self._format_context(context)
                messages.insert(0, {"role": "system", "content": context_str})
            
            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Erro ao gerar resposta do LLM (streaming): {e}", exc_info=True)
            raise
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Formata contexto para prompt."""
        parts = []
        for key, value in context.items():
            if isinstance(value, (dict, list)):
                import json
                parts.append(f"{key}: {json.dumps(value, indent=2)}")
            else:
                parts.append(f"{key}: {value}")
        return "\n".join(parts)


class MockLLMService(LLMService):
    """Mock LLM Service para testes."""
    
    async def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Gera resposta mock."""
        logger.debug(f"Mock LLM: prompt={prompt[:100]}...")
        return '{"type": "css", "target_element": "button", "changes": [{"property": "min-width", "value": "44px", "reason": "Mock fix"}]}'
    
    async def generate_streaming(self, prompt: str, context: Optional[Dict[str, Any]] = None):
        """Gera resposta mock em streaming."""
        response = await self.generate(prompt, context)
        for char in response:
            yield char

