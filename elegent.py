from manim import *

# ==============================================================================
# 一、核心框架层（基础设施，写一次永久复用）
# ==============================================================================


class SceneContext:
    """子场景间共享状态的类型安全容器"""

    def __init__(self):
        self._store = {}

    def put(self, key: str, mobject):
        self._store[key] = mobject

    def get(self, key: str):
        return self._store.get(key)

    def remove(self, key: str):
        self._store.pop(key, None)


class InteractionManager:
    """联动管理器：负责注册对象关系，并统一分发、执行同步动画"""

    def __init__(self, scene: Scene):
        self.scene = scene
        self.registry = {}

    def register(self, trigger_id: str, mobjects: list):
        self.registry[trigger_id] = mobjects

    def unregister(self, trigger_id: str):
        self.registry.pop(trigger_id, None)

    def trigger(self,
                trigger_id: str,
                anim_func=None,
                anim_map: dict | None = None,
                **kwargs):
        """触发联动

        anim_func: 统一动画函数，对所有注册对象施加相同逻辑
        anim_map:  每个对象各自不同的 Animation 实例，优先级高于 anim_func
        """
        mobjects = self.registry.get(trigger_id, [])
        if not mobjects:
            return
        if anim_map:
            animations = [anim_map[obj] for obj in mobjects if obj in anim_map]
        elif anim_func:
            animations = [anim_func(obj) for obj in mobjects]
        else:
            return
        self.scene.play(*animations, **kwargs)


class SceneSegment:
    """所有独立小场景片段的基类"""

    def __init__(self):
        self.scene = None
        self.im = None
        self.ctx = None

    def enter(self):
        """进入场景时的转场动画（可选覆写）"""
        pass

    def play(self):
        """子类必须实现此方法，编写自己的动画逻辑"""
        raise NotImplementedError

    def exit(self):
        """退出场景时的转场动画（可选覆写）"""
        pass


class PipelineScene(Scene):
    """通用的流水线指挥官：负责按顺序、自动化播放场景"""

    scenes_flow = []

    def construct(self):
        ctx = SceneContext()
        im = InteractionManager(self)

        for segment in self.scenes_flow:
            segment.scene = self
            segment.im = im
            segment.ctx = ctx

            segment.enter()
            segment.play()
            segment.exit()

            self.wait(1)


# ==============================================================================
# 二、业务实现层（你日常编写、调整动画的地方）
# ==============================================================================


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

        grid = (VGroup(*[
            VGroup(*[Square(side_length=0.6)
                     for _ in range(3)]).arrange(RIGHT, buff=0.1)
            for _ in range(3)
        ]).arrange(DOWN, buff=0.1).move_to(ORIGIN))

        circle_2 = Circle(radius=0.4, color=PURPLE).next_to(grid,
                                                            RIGHT,
                                                            buff=1)

        self.scene.play(FadeIn(grid), FadeIn(circle_2))

        self.im.register("link_1", [old_group, grid[0]])
        self.im.register("link_2", [circle_2, grid[1]])
        self.im.register("link_3", [grid[2]])

        self.im.trigger("link_1",
                        anim_func=lambda obj: Indicate(obj, color=YELLOW))
        self.scene.wait(0.3)

        self.im.trigger(
            "link_2",
            anim_func=lambda obj: obj.animate.scale(1.2).set_color(PURPLE),
            run_time=0.8,
        )
        self.im.trigger(
            "link_2",
            anim_func=lambda obj: obj.animate.scale(1 / 1.2).set_color(
                WHITE if isinstance(obj, VGroup) else PURPLE),
        )
        self.scene.wait(0.3)

        self.im.trigger("link_3",
                        anim_func=lambda obj: Indicate(obj, color=RED))


class SceneC_End(SceneSegment):
    """场景 C：收尾场景，清空舞台"""

    def play(self):
        self.scene.play(*[FadeOut(mobj) for mobj in self.scene.mobjects])

        thanks = Text("谢谢观看", font="Sans").scale(1.2)
        self.scene.play(Write(thanks))


# ==============================================================================
# 三、装配与运行（最外层没有任何逻辑，只负责声明流程）
# ==============================================================================


class CombinedWorkflow(PipelineScene):
    scenes_flow = [
        SceneA_Layout(),
        SceneB_Interaction(),
        SceneC_End(),
    ]
