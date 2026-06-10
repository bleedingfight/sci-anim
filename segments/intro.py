import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from framework import SceneSegment, FadeTransition
from manim import Text, VGroup, ORIGIN, UP, WHITE, FadeIn, Write


class IntroSegment(SceneSegment):
    """片头：标题 + 副标题淡入"""

    transition = FadeTransition()

    def __init__(self, title, subtitle=None, title_scale=1.6, subtitle_scale=0.7):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.title_scale = title_scale
        self.subtitle_scale = subtitle_scale

    def play(self):
        title = Text(self.title, font="Sans").scale(self.title_scale)
        group = VGroup(title)

        if self.subtitle:
            sub = Text(self.subtitle, font="Sans").scale(self.subtitle_scale)
            sub.next_to(title, UP, buff=0.4)
            group.add(sub)

        group.move_to(ORIGIN)
        self.scene.play(Write(title), run_time=1.5)

        if self.subtitle:
            self.scene.play(FadeIn(sub, shift=UP), run_time=0.8)

        self.ctx.put("intro_title", title)
        if self.subtitle:
            self.ctx.put("intro_subtitle", sub)
