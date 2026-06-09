import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *
from framework import Pipeline, SceneSegment


class Layout_Row(SceneSegment):
    """同行放置：3 个方块放在同一行，自动均匀排布"""

    def play(self):
        a = Square(side_length=0.8, fill_opacity=1, fill_color=RED, stroke_color=WHITE)
        b = Square(side_length=0.8, fill_opacity=1, fill_color=BLUE, stroke_color=WHITE)
        c = Square(side_length=0.8, fill_opacity=1, fill_color=GREEN, stroke_color=WHITE)

        self.im.pipeline.place(a)
        self.im.pipeline.place(b, ref=a, direction=RIGHT)
        self.im.pipeline.place(c, ref=a, direction=RIGHT)

        self.scene.play(FadeIn(a), FadeIn(b), FadeIn(c))

        self.ctx.put("a", a)
        self.ctx.put("b", b)
        self.ctx.put("c", c)


class Layout_Col(SceneSegment):
    """同列放置：在 a 下方再放 2 个方块，形成十字形布局"""

    def play(self):
        a = self.ctx.get("a")

        d = Square(side_length=0.8, fill_opacity=1, fill_color=YELLOW, stroke_color=WHITE)
        e = Square(side_length=0.8, fill_opacity=1, fill_color=PURPLE, stroke_color=WHITE)

        self.im.pipeline.place(d, ref=a, direction=DOWN)
        self.im.pipeline.place(e, ref=d, direction=DOWN)

        self.scene.play(FadeIn(d), FadeIn(e))


class Layout_Bounds(SceneSegment):
    """越界修正：在右侧边缘放置方块，整体自动居中"""

    def play(self):
        f = Square(side_length=0.8, fill_opacity=1, fill_color=ORANGE, stroke_color=WHITE)
        self.im.pipeline.place(f, ref=self.ctx.get("b"), direction=RIGHT)
        self.im.pipeline.place(f, ref=self.ctx.get("b"), direction=RIGHT)
        self.im.pipeline.place(f, ref=self.ctx.get("b"), direction=RIGHT)

        self.scene.play(FadeIn(f))


class LayoutDemo(Scene):
    def construct(self):
        Pipeline(self) \
            .add(Layout_Row()) \
            .add(Layout_Col()) \
            .add(Layout_Bounds()) \
            .run()
