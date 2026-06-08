from framework import SceneSegment
from manim import Square, VGroup, ORIGIN, RED, BLUE, GREEN, YELLOW, WHITE, FadeIn, Create, SurroundingRectangle


class SceneA_Layout(SceneSegment):
    """场景 A：创建组件、编排相对位置、整体居中加框"""

    def play(self):
        a = Square(color=RED, side_length=0.6)
        b = Square(color=BLUE, side_length=0.6)
        c = Square(color=GREEN, side_length=0.6)
        d = Square(color=YELLOW, side_length=0.6)

        b.next_to(c, UP, buff=0.2)
        a.next_to(c, LEFT, buff=0.2)
        d.next_to(c, RIGHT, buff=0.2)

        group = VGroup(a, b, c, d).move_to(ORIGIN)
        frame = SurroundingRectangle(group, color=WHITE, buff=0.3)

        self.scene.play(FadeIn(group))
        self.scene.play(Create(frame))

        self.ctx.put("frame", frame)
        self.ctx.put("group", group)
