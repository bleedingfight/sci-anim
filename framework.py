from manim import Scene


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

    def trigger(self, trigger_id: str, anim_func=None, anim_map: dict | None = None, **kwargs):
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
