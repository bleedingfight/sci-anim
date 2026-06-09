"""sci-anim framework: chain-style scene orchestration with pluggable layout."""

from framework.context import SceneContext
from framework.interaction import InteractionManager
from framework.segment import SceneSegment
from framework.pipeline import Pipeline, PipelineScene
from framework.layout import H_DIRS, V_DIRS
from framework.strategies import LayoutStrategy, BaseLayoutStrategy, RowLayout, ColumnLayout, FreeLayout
from framework.guard import OverlapGuard, GuardResult
from framework.transitions import Transition, CutTransition, FadeTransition

__all__ = [
    "SceneContext",
    "InteractionManager",
    "SceneSegment",
    "Pipeline",
    "PipelineScene",
    "H_DIRS",
    "V_DIRS",
    "LayoutStrategy",
    "BaseLayoutStrategy",
    "RowLayout",
    "ColumnLayout",
    "FreeLayout",
    "OverlapGuard",
    "GuardResult",
    "Transition",
    "CutTransition",
    "FadeTransition",
]
