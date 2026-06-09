import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *
from framework import Pipeline, SceneSegment


class OverlapDemo_Absolute(SceneSegment):
    """绝对定位：三个方块放在同一点(ORIGIN)，Pipeline 自动推开已有对象"""

    def play(self):
        a = Square(side_length=0.8, fill_opacity=1, fill_color=RED, stroke_color=WHITE)
        b = Square(side_length=0.8, fill_opacity=1, fill_color=BLUE, stroke_color=WHITE)
        c = Square(side_length=0.8, fill_opacity=1, fill_color=GREEN, stroke_color=WHITE)

        a.move_to(ORIGIN)
        b.move_to(ORIGIN)
        c.move_to(ORIGIN)

        # b 添加时推开 a，c 添加时推开 a 和 b
        self.scene.play(FadeIn(a))
        self.scene.play(FadeIn(b))
        self.scene.play(FadeIn(c))

        self.ctx.put("a", a)
        self.ctx.put("b", b)
        self.ctx.put("c", c)


class OverlapDemo_Relative(SceneSegment):
    """相对定位：文字放在方块旁边，与方块重叠时自动推开方块"""

    def play(self):
        a = self.ctx.get("a")
        b = self.ctx.get("b")
        c = self.ctx.get("c")

        # 文字故意放在方块中心——会重叠，Pipeline 推开方块
        ta = Text("Red", font_size=20).move_to(a)
        tb = Text("Blue", font_size=20).move_to(b)
        tc = Text("Green", font_size=20).move_to(c)

        self.scene.play(FadeIn(ta), FadeIn(tb), FadeIn(tc))


class OverlapDemo_Bounds(SceneSegment):
    """越界修正：在右侧边缘添加方块，整体布局自动居中"""

    def play(self):
        d = Square(side_length=0.8, fill_opacity=1, fill_color=YELLOW, stroke_color=WHITE)
        d.move_to(RIGHT * 6.5)  # 接近右边界

        self.scene.play(FadeIn(d))


class OverlapGuardDemo(Scene):
    def construct(self):
        Pipeline(self) \
            .add(OverlapDemo_Absolute()) \
            .add(OverlapDemo_Relative()) \
            .add(OverlapDemo_Bounds()) \
            .run()
