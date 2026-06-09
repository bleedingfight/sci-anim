import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from framework import SceneSegment
from manim import Text, FadeOut, Write


class SceneC_End(SceneSegment):
    """场景 C：收尾场景，清空舞台"""

    def play(self):
        self.scene.play(*[FadeOut(mobj) for mobj in self.scene.mobjects])

        thanks = Text("谢谢观看", font="Sans").scale(1.2)
        self.scene.play(Write(thanks))
