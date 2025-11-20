"""
Fix Repository - Infrastructure Layer

Persistência de correções, histórico e métricas usando SQLite.
"""

import logging
import aiosqlite
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class FixRepository:
    """Repositório para persistência de correções."""
    
    def __init__(self, db_path: str = "data/fixes.db"):
        self.db_path = db_path
        self._ensure_db_dir()
    
    def _ensure_db_dir(self):
        """Garante que o diretório do banco existe."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Inicializa banco de dados."""
        async with aiosqlite.connect(self.db_path) as db:
            # Tabela de correções
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fixes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    target_element TEXT NOT NULL,
                    target_selector TEXT,
                    changes TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    issue_type TEXT,
                    issue_data TEXT,
                    generated_by TEXT,
                    confidence REAL,
                    created_at TEXT NOT NULL,
                    applied_at TEXT,
                    validated_at TEXT
                )
            """)
            
            # Tabela de histórico de validações
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fix_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fix_id TEXT NOT NULL,
                    validation_result TEXT NOT NULL,
                    metrics_before TEXT,
                    metrics_after TEXT,
                    should_rollback INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (fix_id) REFERENCES fixes(id)
                )
            """)
            
            # Tabela de métricas
            await db.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id TEXT,
                    metric_type TEXT NOT NULL,
                    metric_value REAL,
                    timestamp TEXT NOT NULL
                )
            """)
            
            await db.commit()
            logger.info("Banco de dados inicializado")
    
    async def save_fix(self, fix: Dict[str, Any]) -> str:
        """Salva uma correção."""
        import json
        
        fix_id = fix.get('id') or f"fix-{datetime.now().timestamp()}"
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO fixes 
                (id, type, target_element, target_selector, changes, priority, status, 
                 issue_type, issue_data, generated_by, confidence, created_at, applied_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fix_id,
                fix.get('type', 'css'),
                fix.get('target_element', ''),
                fix.get('target_selector'),
                json.dumps(fix.get('changes', [])),
                fix.get('priority', 0),
                fix.get('status', 'pending'),
                fix.get('issue_type'),
                json.dumps(fix.get('issue', {})),
                fix.get('generated_by', 'rule'),
                fix.get('confidence', 0.0),
                datetime.now().isoformat(),
                datetime.now().isoformat() if fix.get('status') == 'applied' else None
            ))
            await db.commit()
        
        logger.debug(f"Correção salva: {fix_id}")
        return fix_id
    
    async def get_fix(self, fix_id: str) -> Optional[Dict[str, Any]]:
        """Obtém uma correção por ID."""
        import json
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM fixes WHERE id = ?",
                (fix_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None
                
                return {
                    'id': row['id'],
                    'type': row['type'],
                    'target_element': row['target_element'],
                    'target_selector': row['target_selector'],
                    'changes': json.loads(row['changes']),
                    'priority': row['priority'],
                    'status': row['status'],
                    'issue_type': row['issue_type'],
                    'issue': json.loads(row['issue_data']) if row['issue_data'] else {},
                    'generated_by': row['generated_by'],
                    'confidence': row['confidence'],
                    'created_at': row['created_at'],
                    'applied_at': row['applied_at']
                }
    
    async def list_fixes(
        self,
        status: Optional[str] = None,
        issue_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Lista correções com filtros."""
        import json
        
        query = "SELECT * FROM fixes WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if issue_type:
            query += " AND issue_type = ?"
            params.append(issue_type)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                
                fixes = []
                for row in rows:
                    fixes.append({
                        'id': row['id'],
                        'type': row['type'],
                        'target_element': row['target_element'],
                        'target_selector': row['target_selector'],
                        'changes': json.loads(row['changes']),
                        'priority': row['priority'],
                        'status': row['status'],
                        'issue_type': row['issue_type'],
                        'issue': json.loads(row['issue_data']) if row['issue_data'] else {},
                        'generated_by': row['generated_by'],
                        'confidence': row['confidence'],
                        'created_at': row['created_at'],
                        'applied_at': row['applied_at']
                    })
                
                return fixes
    
    async def update_fix_status(self, fix_id: str, status: str):
        """Atualiza status de uma correção."""
        async with aiosqlite.connect(self.db_path) as db:
            applied_at = datetime.now().isoformat() if status == 'applied' else None
            await db.execute(
                "UPDATE fixes SET status = ?, applied_at = ? WHERE id = ?",
                (status, applied_at, fix_id)
            )
            await db.commit()
    
    async def save_validation(
        self,
        fix_id: str,
        validation_result: Dict[str, Any],
        metrics_before: Optional[Dict[str, Any]] = None,
        metrics_after: Optional[Dict[str, Any]] = None
    ):
        """Salva resultado de validação."""
        import json
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO fix_history 
                (fix_id, validation_result, metrics_before, metrics_after, should_rollback, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                fix_id,
                json.dumps(validation_result),
                json.dumps(metrics_before) if metrics_before else None,
                json.dumps(metrics_after) if metrics_after else None,
                1 if validation_result.get('should_rollback') else 0,
                datetime.now().isoformat()
            ))
            await db.commit()
    
    async def save_metric(
        self,
        application_id: str,
        metric_type: str,
        metric_value: float
    ):
        """Salva uma métrica."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO metrics (application_id, metric_type, metric_value, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                application_id,
                metric_type,
                metric_value,
                datetime.now().isoformat()
            ))
            await db.commit()
    
    async def get_metrics(
        self,
        application_id: str,
        metric_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtém métricas."""
        query = "SELECT * FROM metrics WHERE application_id = ?"
        params = [application_id]
        
        if metric_type:
            query += " AND metric_type = ?"
            params.append(metric_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                
                return [
                    {
                        'id': row['id'],
                        'application_id': row['application_id'],
                        'metric_type': row['metric_type'],
                        'metric_value': row['metric_value'],
                        'timestamp': row['timestamp']
                    }
                    for row in rows
                ]

