from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from manim import VGroup, UP, DOWN, LEFT, RIGHT, config

from framework.layout import _bb_overlaps, _out_of_bounds, _center_layout
from framework.placement_ui import _PlacementUI


@dataclass
class GuardResult:
    """validate() 的返回值。"""
    ok: bool = False
    need_ui: bool = False


class OverlapGuard:
    """重叠/越界检测与消解，与布局策略完全解耦。

    职责：
    - 检测对象间重叠和越界
    - 通过策略接口消解跨组重叠（最多 5 轮）
    - 越界修正（全局居中）
    - 交互 UI 回退
    - 回滚策略注册

    不负责：决定对象放在哪里（那是策略的事）。
    """

    def __init__(self, pipeline, interactive: bool = True):
        self._pipeline = pipeline
        self._interactive = interactive
        self._mobj_by_id: dict[int, object] = {}
        self._atomic_groups: dict[int, VGroup] = {}
        self._excluded_mobj_ids: set[int] = set()

    def register_atomic(self, obj: VGroup):
        """将 VGroup 注册为原子单位，子对象排除出重叠检测。"""
        self._atomic_groups[id(obj)] = obj
        for sub in obj.submobjects:
            self._excluded_mobj_ids.add(id(sub))

    def _checkable(self, mobjects: list) -> list:
        return [m for m in mobjects if id(m) not in self._excluded_mobj_ids]

    # ------------------------------------------------------------------
    # 核心接口
    # ------------------------------------------------------------------

    def validate(self, obj, buff: float) -> GuardResult:
        """定位完成后调用：消解重叠、修正越界、给出最终判定。

        Returns GuardResult:
        - ok=True       → 对象合法，可以加入场景
        - ok=False, need_ui=True  → 需要弹交互 UI
        - ok=False, need_ui=False → 直接拒绝
        """
        strategy = self._pipeline._active_strategy
        scene = self._pipeline.scene
        hw = config.frame_width / 2
        hh = config.frame_height / 2

        # 步骤3：跨组冲突消解（最多5轮）
        for _ in range(5):
            overlaps = []
            all_mobjs = list(scene.mobjects) + [obj]
            check = self._checkable(all_mobjs)

            for i in range(len(check)):
                for j in range(i + 1, len(check)):
                    if _bb_overlaps(check[i], check[j]):
                        overlaps.append((check[i], check[j]))

            if not overlaps:
                break

            for a, b in overlaps:
                line_a = strategy.group_for(a)
                line_b = strategy.group_for(b)
                if line_a is None or line_b is None or line_a is line_b:
                    continue
                self._resolve_overlap(a, b, line_a, line_b, buff, strategy)

        # 步骤4：越界修正
        all_mobjs = list(scene.mobjects) + [obj]
        check = self._checkable(all_mobjs)
        any_oob = any(_out_of_bounds(m, hw, hh) for m in check)

        if any_oob:
            _center_layout(check)
            any_oob = any(_out_of_bounds(m, hw, hh) for m in check)

        # 步骤5：最终判定
        still_overlaps = any(
            _bb_overlaps(obj, m)
            for m in scene.mobjects
            if id(m) not in self._excluded_mobj_ids
        )

        if still_overlaps or any_oob:
            strategy.remove(obj)
            if self._interactive:
                return GuardResult(ok=False, need_ui=True)
            return GuardResult(ok=False, need_ui=False)

        return GuardResult(ok=True)

    def interactive_place(self, obj, buff: float) -> GuardResult:
        """弹出交互 UI 让用户手动放置对象。"""
        scene = self._pipeline.scene
        try:
            ui = _PlacementUI(
                scene.mobjects, obj,
                config.frame_width, config.frame_height, buff,
                atomic_groups=self._atomic_groups,
                excluded_ids=self._excluded_mobj_ids,
            )
            result = ui.result
        except Exception:
            result = None

        if result is None or result[0] != "placed":
            warnings.warn(
                f"Pipeline.place: rejected {obj} — could not be resolved",
                stacklevel=3,
            )
            return GuardResult(ok=False, need_ui=False)

        _, cx, cy, scale, existing_results = result
        for mid, (ex, ey, esf) in existing_results.items():
            m = self._mobj_by_id.get(mid)
            if m is not None and esf != 1.0:
                m.scale(esf)
            if m is not None:
                m.move_to(ex * RIGHT + ey * UP)
        if scale != 1.0:
            obj.scale(scale)
        obj.move_to(cx * RIGHT + cy * UP)
        self._accept(obj)
        return GuardResult(ok=True)

    def _accept(self, obj):
        """将对象标记为已接受（加入场景和跟踪表）。"""
        self._pipeline.scene.add(obj)
        self._mobj_by_id[id(obj)] = obj

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_overlap(a, b, line_a, line_b, buff, strategy):
        if line_a.axis == "h" and line_b.axis == "v":
            y_ov = min(a.get_top()[1], b.get_top()[1]) - max(
                a.get_bottom()[1], b.get_bottom()[1]
            )
            sign = 1 if b.get_center()[1] >= a.get_center()[1] else -1
            shift = sign * (y_ov + buff) * UP
            strategy.shift_group(line_b, shift)
            strategy.redistribute_group(line_b, buff)
        elif line_a.axis == "v" and line_b.axis == "h":
            x_ov = min(a.get_right()[0], b.get_right()[0]) - max(
                a.get_left()[0], b.get_left()[0]
            )
            sign = 1 if b.get_center()[0] >= a.get_center()[0] else -1
            shift = sign * (x_ov + buff) * RIGHT
            strategy.shift_group(line_b, shift)
            strategy.redistribute_group(line_b, buff)
        else:
            if line_a.axis == "h":
                y_ov = min(a.get_top()[1], b.get_top()[1]) - max(
                    a.get_bottom()[1], b.get_bottom()[1]
                )
                sign = 1 if b.get_center()[1] >= a.get_center()[1] else -1
                shift = sign * (y_ov + buff) * UP
            else:
                x_ov = min(a.get_right()[0], b.get_right()[0]) - max(
                    a.get_left()[0], b.get_left()[0]
                )
                sign = 1 if b.get_center()[0] >= a.get_center()[0] else -1
                shift = sign * (x_ov + buff) * RIGHT
            strategy.shift_group(line_b, shift)
            strategy.redistribute_group(line_b, buff)
