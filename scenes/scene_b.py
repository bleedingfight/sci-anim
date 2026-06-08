from framework import SceneSegment
from manim import (
    Square, Circle, VGroup,
    ORIGIN, RIGHT, DOWN, UP, LEFT,
    WHITE, PURPLE, YELLOW, RED,
    FadeOut, FadeIn, Indicate,
)


class SceneB_Interaction(SceneSegment):
    """场景 B：承接旧场景，创建网格并注册同步联动"""

    def enter(self):
        old_frame = self.ctx.get("frame")
        if old_frame:
            self.scene.play(FadeOut(old_frame))
            self.ctx.remove("frame")

    def play(self):
        old_group = self.ctx.get("group")

        if old_group:
            self.scene.play(old_group.animate.scale(0.6).to_edge(LEFT))

        grid = (
            VGroup(
                *[
                    VGroup(*[Square(side_length=0.6) for _ in range(3)]).arrange(
                        RIGHT, buff=0.1
                    )
                    for _ in range(3)
                ]
            )
            .arrange(DOWN, buff=0.1)
            .move_to(ORIGIN)
        )

        circle_2 = Circle(radius=0.4, color=PURPLE).next_to(grid, RIGHT, buff=1)

        self.scene.play(FadeIn(grid), FadeIn(circle_2))

        self.im.register("link_1", [old_group, grid[0]])
        self.im.register("link_2", [circle_2, grid[1]])
        self.im.register("link_3", [grid[2]])

        self.im.trigger("link_1", anim_func=lambda obj: Indicate(obj, color=YELLOW))
        self.scene.wait(0.3)

        self.im.trigger(
            "link_2",
            anim_func=lambda obj: obj.animate.scale(1.2).set_color(PURPLE),
            run_time=0.8,
        )
        self.im.trigger(
            "link_2",
            anim_func=lambda obj: obj.animate.scale(1 / 1.2).set_color(
                WHITE if isinstance(obj, VGroup) else PURPLE
            ),
        )
        self.scene.wait(0.3)

        self.im.trigger("link_3", anim_func=lambda obj: Indicate(obj, color=RED))
