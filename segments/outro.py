import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from framework import SceneSegment
from manim import Text, FadeOut, Write


class OutroSegment(SceneSegment):
    """片尾：清场 + 结束语"""

    def __init__(self, closing_text="谢谢观看", text_scale=1.2):
        super().__init__()
        self.closing_text = closing_text
        self.text_scale = text_scale

    def play(self):
        self.scene.play(*[FadeOut(mobj) for mobj in self.scene.mobjects])

        text = Text(self.closing_text, font="Sans").scale(self.text_scale)
        self.scene.play(Write(text), run_time=1.5)
