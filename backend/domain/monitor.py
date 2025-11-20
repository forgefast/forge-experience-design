"""
Monitor - Domain Layer

Monitoramento contínuo de problemas de UI/UX e geração automática de correções.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import os

from ..infrastructure.forge_logs_client import ForgeLogsClient
from .fix_engine import FixEngine
from .fix_validator import FixValidator
from ..infrastructure.storage.fix_repository import FixRepository

logger = logging.getLogger(__name__)


class Monitor:
    """
    Monitora problemas de UI/UX continuamente e gera correções automaticamente.
    """
    
    def __init__(
        self,
        forge_logs_client: ForgeLogsClient,
        fix_engine: FixEngine,
        fix_validator: FixValidator,
        fix_repository: FixRepository,
        application_id: str = 'forgetest-studio',
        interval_seconds: int = 60
    ):
        self.forge_logs_client = forge_logs_client
        self.fix_engine = fix_engine
        self.fix_validator = fix_validator
        self.fix_repository = fix_repository
        self.application_id = application_id
        self.interval_seconds = interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Adiciona callback para notificações de novos problemas/correções."""
        self._callbacks.append(callback)
    
    async def start(self):
        """Inicia monitoramento contínuo."""
        if self._running:
            logger.warning("Monitor já está rodando")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Monitor iniciado para aplicação: {self.application_id}")
    
    async def stop(self):
        """Para monitoramento."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Monitor parado")
    
    async def _monitor_loop(self):
        """Loop principal de monitoramento."""
        while self._running:
            try:
                await self._check_and_fix()
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}", exc_info=True)
                await asyncio.sleep(self.interval_seconds)
    
    async def _check_and_fix(self):
        """Verifica problemas e gera correções."""
        try:
            logger.debug(f"Verificando problemas para {self.application_id}")
            
            # Obter problemas de UI do ForgeLogs
            ui_issues = await self.forge_logs_client.get_ui_issues(
                application_id=self.application_id,
                severity='high',
                limit=50
            )
            
            if not ui_issues:
                logger.debug("Nenhum problema de UI encontrado")
                return
            
            logger.info(f"Encontrados {len(ui_issues)} problemas de UI")
            
            # Gerar correções
            fixes = await self.fix_engine.analyze_and_generate_fixes(
                application_id=self.application_id,
                limit=50
            )
            
            if not fixes:
                logger.debug("Nenhuma correção gerada")
                return
            
            logger.info(f"Geradas {len(fixes)} correções")
            
            # Salvar correções
            for fix in fixes:
                fix_id = await self.fix_repository.save_fix(fix)
                fix['id'] = fix_id
                
                # Notificar callbacks
                for callback in self._callbacks:
                    try:
                        callback({
                            'type': 'fix_generated',
                            'fix_id': fix_id,
                            'fix': fix,
                            'timestamp': datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.error(f"Erro em callback: {e}")
            
        except Exception as e:
            logger.error(f"Erro ao verificar e corrigir: {e}", exc_info=True)
    
    async def validate_applied_fixes(self):
        """Valida correções aplicadas."""
        try:
            # Obter correções aplicadas
            applied_fixes = await self.fix_repository.list_fixes(
                status='applied',
                limit=20
            )
            
            for fix in applied_fixes:
                # Obter métricas antes/depois (simplificado)
                before_metrics = {'issue_count': 1}  # Placeholder
                after_metrics = {'issue_count': 0}  # Placeholder
                
                # Validar
                validation_result = await self.fix_validator.validate_fix(
                    fix=fix,
                    issue=fix.get('issue', {}),
                    before_metrics=before_metrics,
                    after_metrics=after_metrics
                )
                
                # Salvar validação
                await self.fix_repository.save_validation(
                    fix_id=fix['id'],
                    validation_result=validation_result,
                    metrics_before=before_metrics,
                    metrics_after=after_metrics
                )
                
                # Rollback se necessário
                if self.fix_validator.should_rollback(fix, validation_result, {}):
                    await self.fix_repository.update_fix_status(fix['id'], 'rolled_back')
                    logger.info(f"Correção {fix['id']} revertida após validação")
                    
                    # Notificar callbacks
                    for callback in self._callbacks:
                        try:
                            callback({
                                'type': 'fix_rolled_back',
                                'fix_id': fix['id'],
                                'reason': validation_result.get('reason'),
                                'timestamp': datetime.now().isoformat()
                            })
                        except Exception as e:
                            logger.error(f"Erro em callback: {e}")
                            
        except Exception as e:
            logger.error(f"Erro ao validar correções: {e}", exc_info=True)
    
    def is_running(self) -> bool:
        """Verifica se monitor está rodando."""
        return self._running

