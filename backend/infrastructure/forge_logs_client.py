"""
ForgeLogs API Client
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ForgeLogsClient:
    """Cliente para API do ForgeLogs"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_ui_issues(
        self,
        application_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Obtém problemas de UI do ForgeLogs"""
        try:
            params = {
                'limit': limit,
                'offset': offset,
                'log_type': 'ui_issue',
                'category': 'ui'
            }
            
            if application_id:
                params['application_id'] = application_id
            if severity:
                params['severity'] = severity
            
            response = await self.client.get(
                f"{self.base_url}/api/logs",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"ForgeLogs HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"ForgeLogs connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting UI issues: {e}", exc_info=True)
            raise
    
    async def get_logs(
        self,
        application_id: Optional[str] = None,
        log_type: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Obtém logs do ForgeLogs"""
        try:
            params = {
                'limit': limit,
                'offset': offset
            }
            
            if application_id:
                params['application_id'] = application_id
            if log_type:
                params['log_type'] = log_type
            if severity:
                params['severity'] = severity
            if category:
                params['category'] = category
            
            response = await self.client.get(
                f"{self.base_url}/api/logs",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"ForgeLogs HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"ForgeLogs connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting logs: {e}", exc_info=True)
            raise
    
    async def get_ai_analysis(
        self,
        application_id: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Obtém análise com IA do ForgeLogs"""
        try:
            params = {'limit': limit}
            
            if application_id:
                params['application_id'] = application_id
            
            response = await self.client.get(
                f"{self.base_url}/api/analytics/ai-analysis",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"ForgeLogs HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"ForgeLogs connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting AI analysis: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Fecha cliente"""
        await self.client.aclose()

