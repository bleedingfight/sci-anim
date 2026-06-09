import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scene_a import SceneA_Layout
from scene_b import SceneB_Interaction
from scene_c import SceneC_End
from framework import Pipeline, PipelineScene
from manim import Scene


# 链式构建（新方式）
class ChainedWorkflow(Scene):
    def construct(self):
        Pipeline(self) \
            .add(SceneA_Layout()) \
            .add(SceneB_Interaction()) \
            .add(SceneC_End()) \
            .run()


# 类属性声明（旧方式，仍然可用）
class CombinedWorkflow(PipelineScene):
    scenes_flow = [
        SceneA_Layout(),
        SceneB_Interaction(),
        SceneC_End(),
    ]
