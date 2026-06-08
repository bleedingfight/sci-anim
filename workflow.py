from scenes.scene_a import SceneA_Layout
from scenes.scene_b import SceneB_Interaction
from scenes.scene_c import SceneC_End
from framework import PipelineScene


class CombinedWorkflow(PipelineScene):
    scenes_flow = [
        SceneA_Layout(),
        SceneB_Interaction(),
        SceneC_End(),
    ]
