from manim import Scene


class InteractionManager:
    """联动管理器：负责注册对象关系，并统一分发、执行同步动画"""

    def __init__(self, scene: Scene):
        self.scene = scene
        self.registry = {}
        self.pipeline = None

    def register(self, trigger_id: str, mobjects: list):
        self.registry[trigger_id] = mobjects

    def unregister(self, trigger_id: str):
        self.registry.pop(trigger_id, None)

    def trigger(
        self, trigger_id: str, anim_func=None, anim_map: dict | None = None, **kwargs
    ):
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
