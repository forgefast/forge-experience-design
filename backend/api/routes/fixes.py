"""
Fix Routes
"""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...domain.fix_engine import FixEngine
from ...domain.diff_generator import DiffGenerator
from ...infrastructure.forge_logs_client import ForgeLogsClient
from ...infrastructure.storage.fix_repository import FixRepository
from ...infrastructure.ai.fix_generator import FixGenerator
from ...infrastructure.ai.llm_service import MockLLMService
from ...infrastructure.ai.html_analyzer import HTMLAnalyzer
from ...infrastructure.source.patch_applier import PatchApplier
from ...infrastructure.source.file_locator import FileLocator
from ...config.project_config import project_manager

router = APIRouter(prefix="/api/fixes", tags=["fixes"])

# Cliente ForgeLogs
forge_logs_url = os.getenv('FORGELOGS_URL', 'http://localhost:8002')
forge_logs_client = ForgeLogsClient(base_url=forge_logs_url)

# Repositório
db_path = os.getenv('DATABASE_PATH', 'data/fixes.db')
fix_repository = FixRepository(db_path=db_path)

# IA (opcional)
llm_service = None
fix_generator = None
try:
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        from ...infrastructure.ai.llm_service import OpenAILLMService
        llm_service = OpenAILLMService(api_key=openai_key)
        html_analyzer = HTMLAnalyzer()
        fix_generator = FixGenerator(llm_service, html_analyzer)
    else:
        # Usar mock se não tiver chave
        llm_service = MockLLMService()
        html_analyzer = HTMLAnalyzer()
        fix_generator = FixGenerator(llm_service, html_analyzer)
except Exception as e:
    import logging
    logging.getLogger(__name__).warning(f"IA não disponível: {e}")
    llm_service = MockLLMService()
    html_analyzer = HTMLAnalyzer()
    fix_generator = FixGenerator(llm_service, html_analyzer)

# Motor de correção
fix_engine = FixEngine(
    forge_logs_client=forge_logs_client,
    fix_generator=fix_generator,
    fix_repository=fix_repository
)

# Gerador de diff
diff_generator = DiffGenerator()

# Aplicador de patches (lazy initialization)
_patch_applier = None
_file_locator = None

def get_patch_applier(project_id: str = "forgetest-studio"):
    """Obtém PatchApplier para projeto."""
    global _patch_applier
    project_config = project_manager.get_project(project_id)
    if project_config:
        _patch_applier = PatchApplier(project_config)
    return _patch_applier

def get_file_locator(project_id: str = "forgetest-studio"):
    """Obtém FileLocator para projeto."""
    global _file_locator
    project_config = project_manager.get_project(project_id)
    if project_config:
        _file_locator = FileLocator(project_config)
    return _file_locator


class FixResponse(BaseModel):
    """Fix response"""
    id: str
    type: str
    target_element: str
    target_selector: Optional[str] = None
    changes: List[dict]
    priority: int
    status: str = 'pending'


@router.get("/generate", response_model=List[FixResponse])
async def generate_fixes(
    application_id: Optional[str] = None,
    limit: int = 100,
    use_ai: bool = False
):
    """Gera correções baseadas em logs do ForgeLogs"""
    app_id = application_id or os.getenv('APPLICATION_ID', 'forgetest-studio')
    
    try:
        fixes = await fix_engine.analyze_and_generate_fixes(
            application_id=app_id,
            limit=limit,
            use_ai=use_ai and fix_generator is not None
        )
        
        # Salvar correções no repositório
        saved_fixes = []
        for fix in fixes:
            fix_id = await fix_repository.save_fix(fix)
            saved_fixes.append({
                **fix,
                'id': fix_id
            })
        
        return [
            FixResponse(
                id=fix.get('id', f"fix-{i}"),
                type=fix.get('type', 'css'),
                target_element=fix.get('target_element', ''),
                target_selector=fix.get('target_selector'),
                changes=fix.get('changes', []),
                priority=fix.get('priority', 0),
                status=fix.get('status', 'pending')
            )
            for i, fix in enumerate(saved_fixes)
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules")
async def get_rules():
    """Obtém todas as regras de correção"""
    rules = fix_engine.get_rules()
    return [
        {
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'issue_type': rule.issue_type,
            'priority': rule.priority,
            'enabled': rule.enabled
        }
        for rule in rules
    ]


@router.post("/rules/{rule_id}/enable")
async def enable_rule(rule_id: str):
    """Habilita regra de correção"""
    fix_engine.enable_rule(rule_id)
    return {'message': f'Rule {rule_id} enabled'}


@router.post("/rules/{rule_id}/disable")
async def disable_rule(rule_id: str):
    """Desabilita regra de correção"""
    fix_engine.disable_rule(rule_id)
    return {'message': f'Rule {rule_id} disabled'}


@router.get("", response_model=List[FixResponse])
async def list_fixes(
    status: Optional[str] = None,
    issue_type: Optional[str] = None,
    limit: int = 100
):
    """Lista correções com filtros"""
    try:
        fixes = await fix_repository.list_fixes(
            status=status,
            issue_type=issue_type,
            limit=limit
        )
        
        return [
            FixResponse(
                id=fix.get('id', ''),
                type=fix.get('type', 'css'),
                target_element=fix.get('target_element', ''),
                target_selector=fix.get('target_selector'),
                changes=fix.get('changes', []),
                priority=fix.get('priority', 0),
                status=fix.get('status', 'pending')
            )
            for fix in fixes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{fix_id}", response_model=FixResponse)
async def get_fix(fix_id: str):
    """Obtém uma correção por ID"""
    try:
        fix = await fix_repository.get_fix(fix_id)
        if not fix:
            raise HTTPException(status_code=404, detail="Fix not found")
        
        return FixResponse(
            id=fix.get('id', ''),
            type=fix.get('type', 'css'),
            target_element=fix.get('target_element', ''),
            target_selector=fix.get('target_selector'),
            changes=fix.get('changes', []),
            priority=fix.get('priority', 0),
            status=fix.get('status', 'pending')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{fix_id}/apply")
async def apply_fix(fix_id: str):
    """Marca correção como aplicada"""
    try:
        await fix_repository.update_fix_status(fix_id, 'applied')
        return {'message': f'Fix {fix_id} marked as applied'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{fix_id}/rollback")
async def rollback_fix(fix_id: str):
    """Reverte uma correção"""
    try:
        await fix_repository.update_fix_status(fix_id, 'rolled_back')
        return {'message': f'Fix {fix_id} rolled back'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{fix_id}/preview")
async def preview_fix(fix_id: str, project_id: str = "forgetest-studio"):
    """Gera preview (diff) da correção sem aplicar"""
    try:
        fix = await fix_repository.get_fix(fix_id)
        if not fix:
            raise HTTPException(status_code=404, detail="Fix not found")
        
        file_locator = get_file_locator(project_id)
        if not file_locator:
            raise HTTPException(status_code=500, detail="Project not configured")
        
        # Localizar arquivo
        file_info = file_locator.locate_file_for_fix(fix)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found for selector")
        
        # Ler conteúdo original
        project_config = project_manager.get_project(project_id)
        if not project_config:
            raise HTTPException(status_code=500, detail="Project not configured")
        
        # Ler arquivo diretamente
        file_path = project_config.root_path / file_info["relative_path"]
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        original_content = file_path.read_text(encoding='utf-8')
        
        # Gerar conteúdo modificado
        from ...infrastructure.source.css_modifier import CSSModifier
        css_modifier = CSSModifier(project_config)
        
        selector = fix.get("target_selector") or fix.get("target_element", "")
        changes = fix.get("changes", [])
        
        result = css_modifier.modify_css_file(
            file_path=file_info["relative_path"],
            selector=selector,
            changes=changes
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail="Failed to generate preview")
        
        # Gerar diff
        diff_result = diff_generator.generate_diff_for_fix(
            fix=fix,
            original_content=original_content,
            modified_content=result["modified_content"],
            file_path=file_info["relative_path"]
        )
        
        return {
            "fix_id": fix_id,
            "file_path": file_info["relative_path"],
            "diff": diff_result["diff"],
            "formatted_diff": diff_generator.format_diff_for_display(diff_result["diff"]),
            "changes_summary": diff_result["changes_summary"],
            "statistics": {
                "added_lines": diff_result["added_lines"],
                "removed_lines": diff_result["removed_lines"],
                "line_count": diff_result["line_count"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{fix_id}/apply-source")
async def apply_fix_to_source(
    fix_id: str,
    create_backup: bool = True,
    project_id: str = "forgetest-studio"
):
    """Aplica correção nos arquivos fonte"""
    try:
        fix = await fix_repository.get_fix(fix_id)
        if not fix:
            raise HTTPException(status_code=404, detail="Fix not found")
        
        patch_applier = get_patch_applier(project_id)
        if not patch_applier:
            raise HTTPException(status_code=500, detail="Project not configured")
        
        # Aplicar correção
        result = patch_applier.apply_fix(fix, create_backup=create_backup)
        
        if result["success"]:
            # Atualizar status no banco
            await fix_repository.update_fix_status(fix_id, 'applied')
            
            # Atualizar fix com informações de source
            fix["target_file"] = result["file_path"]
            fix["backup_path"] = result.get("backup_path")
            await fix_repository.save_fix(fix)
        
        return {
            "success": result["success"],
            "fix_id": fix_id,
            "file_path": result.get("file_path"),
            "backup_path": result.get("backup_path"),
            "changes_applied": result.get("changes_applied", []),
            "errors": result.get("errors", [])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{fix_id}/rollback-source")
async def rollback_fix_source(
    fix_id: str,
    backup_path: str,
    project_id: str = "forgetest-studio"
):
    """Reverte correção usando backup"""
    try:
        fix = await fix_repository.get_fix(fix_id)
        if not fix:
            raise HTTPException(status_code=404, detail="Fix not found")
        
        patch_applier = get_patch_applier(project_id)
        if not patch_applier:
            raise HTTPException(status_code=500, detail="Project not configured")
        
        # Reverter correção
        result = patch_applier.rollback_fix(fix, backup_path)
        
        if result["success"]:
            # Atualizar status no banco
            await fix_repository.update_fix_status(fix_id, 'rolled_back')
        
        return {
            "success": result["success"],
            "fix_id": fix_id,
            "file_path": result.get("file_path"),
            "errors": result.get("errors", [])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backups")
async def list_backups(project_id: str = "forgetest-studio"):
    """Lista backups disponíveis"""
    try:
        patch_applier = get_patch_applier(project_id)
        if not patch_applier:
            raise HTTPException(status_code=500, detail="Project not configured")
        
        backups = patch_applier.list_backups()
        return {"backups": backups}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

