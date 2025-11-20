"""
Source Code Infrastructure

Componentes para análise e modificação de código-fonte.
"""

from .source_analyzer import SourceAnalyzer
from .file_locator import FileLocator
from .css_modifier import CSSModifier
from .patch_applier import PatchApplier

__all__ = [
    "SourceAnalyzer",
    "FileLocator",
    "CSSModifier",
    "PatchApplier"
]

