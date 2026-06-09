import warnings
from manim import Scene, UP, DOWN, LEFT, RIGHT, ORIGIN, config, VGroup

from framework.context import SceneContext
from framework.interaction import InteractionManager
from framework.segment import SceneSegment
from framework.layout import _AlignLine, _bb_overlaps, _out_of_bounds, _center_layout, H_DIRS, V_DIRS
from framework.strategies import LayoutStrategy, BaseLayoutStrategy, RowLayout
from framework.guard import OverlapGuard, GuardResult
from framework.transitions import Transition, CutTransition, FadeTransition


class Pipeline:
    """链式场景编排器 + 可插拔布局引擎

    每个子场景通过 layout 类属性声明布局策略（默认 RowLayout）。
    转场通过 transition 类属性声明（默认 CutTransition 硬切）。
    Pipeline 编排策略定位、重叠检测和转场，自身不含细节。

    Parameters
    ----------
    overlap_buff : float | None
        对象间最小间距。设为 None 则禁用布局引擎，默认 0.1。
    interactive : bool
        自动布局失败时是否弹出交互式放置 UI，默认 True。
    """

    def __init__(
        self, scene: Scene, overlap_buff: float | None = 0.1, interactive: bool = True
    ):
        self.scene = scene
        self._segments = []
        self.ctx = SceneContext()
        self.im = InteractionManager(scene)
        self.im.pipeline = self
        self._overlap_buff = overlap_buff

        self._active_strategy: LayoutStrategy | None = None
        self._guard = OverlapGuard(self, interactive=interactive)

    def add(self, segment: SceneSegment):
        self._segments.append(segment)
        return self

    def run(self):
        prev = None
        for segment in self._segments:
            segment.scene = self.scene
            segment.im = self.im
            segment.ctx = self.ctx
            segment.pipeline = self

            strategy = segment.layout()
            strategy.bind(self)
            segment._strategy = strategy
            self._active_strategy = strategy

            # 转场：两段之间的桥
            if prev is not None:
                tr = segment.transition
                if tr is None:
                    tr = CutTransition()
                elif isinstance(tr, type):
                    tr = tr()
                tr(self.scene, self.ctx, prev, segment)

            segment.play()
            prev = segment
            self.scene.wait(1)

    # ------------------------------------------------------------------
    # 布局引擎
    # ------------------------------------------------------------------

    def track(self, obj, guard=True):
        """注册已定位的对象，让重叠检测生效。

        适合 FreeLayout 场景中子场景自行完成位置编排后调用。
        guard=False 时跳过重叠/越界检测（允许有意重叠）。

        如果 obj 是 VGroup，将其作为原子单位注册：
        子对象从重叠检测中排除，只检测 VGroup 整体包围盒。
        """
        if isinstance(obj, VGroup):
            self._guard.register_atomic(obj)

        if not guard:
            self._guard._accept(obj)
            return self

        return self.place(obj)

    def place(self, obj, ref=None, direction=RIGHT, buff=None):
        """将 obj 放到 ref 的 direction 方向，通过布局策略定位后验证。

        Returns self for chaining.
        """
        if self._overlap_buff is None:
            if ref is not None:
                obj.next_to(ref, direction, buff=buff or 0.1)
            else:
                obj.move_to(ORIGIN)
            self._guard._accept(obj)
            return self

        buff = buff if buff is not None else self._overlap_buff

        # 策略定位
        self._active_strategy.place(obj, ref=ref, direction=direction, buff=buff)

        # 原子 VGroup 注册
        if isinstance(obj, VGroup):
            self._guard.register_atomic(obj)

        # Guard 验证
        result = self._guard.validate(obj, buff)

        if result.ok:
            self._guard._accept(obj)
        elif result.need_ui:
            result = self._guard.interactive_place(obj, buff)
            if not result.ok:
                pass  # warning already issued inside interactive_place
        else:
            warnings.warn(
                f"Pipeline.place: rejected {obj} — "
                f"overlap or out of bounds could not be resolved",
                stacklevel=2,
            )

        return self


class PipelineScene(Scene):
    """向后兼容的流水线场景：通过 scenes_flow 类属性声明子场景"""

    scenes_flow = []

    def construct(self):
        p = Pipeline(self)
        for segment in self.scenes_flow:
            p.add(segment)
        p.run()
