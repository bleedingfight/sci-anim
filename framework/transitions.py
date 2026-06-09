from __future__ import annotations

from manim import FadeOut, FadeIn


class Transition:
    """转场基类：定义两个相邻场景片段之间的过渡动画。

    子类实现 __call__，接收 scene、ctx、prev、next 四个参数。
    prev 为上一个片段（首个场景时为 None），next 为即将播放的片段。
    """

    def __call__(self, scene, ctx, prev, next):
        raise NotImplementedError


class CutTransition(Transition):
    """硬切：无任何转场动画，直接切换。"""

    def __call__(self, scene, ctx, prev, next):
        pass


class FadeTransition(Transition):
    """淡入淡出：先淡出上一个片段标记的对象，再淡入新片段。

    可通过 ctx 传递 key 来指定需要淡出的对象。
    如果未指定 fade_out_key，则不做淡出。
    """

    def __init__(self, fade_out_key=None):
        self.fade_out_key = fade_out_key

    def __call__(self, scene, ctx, prev, next):
        if self.fade_out_key:
            mobj = ctx.get(self.fade_out_key)
            if mobj:
                scene.play(FadeOut(mobj))
                ctx.remove(self.fade_out_key)
