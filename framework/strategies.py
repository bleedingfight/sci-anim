from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from manim import RIGHT

from framework.layout import _AlignLine, H_DIRS, V_DIRS

if TYPE_CHECKING:
    from framework.pipeline import Pipeline


@runtime_checkable
class LayoutStrategy(Protocol):
    """布局策略接口：决定对象放在哪里。

    策略只负责位置计算，不调 scene.add()。
    重叠检测、越界修正、交互 UI 回退由 Pipeline 统一处理。
    """

    def bind(self, pipeline: Pipeline) -> None: ...
    def place(self, obj, ref=None, direction=RIGHT, buff=None) -> None: ...
    def group_for(self, obj) -> _AlignLine | None: ...
    def shift_group(self, group: _AlignLine, vector) -> None: ...
    def redistribute_group(self, group: _AlignLine, buff: float) -> None: ...
    def remove(self, obj) -> None: ...


class BaseLayoutStrategy:
    """布局策略基类，提供共享的行/列分组管理。"""

    def __init__(self):
        self._pipeline: Pipeline | None = None
        self._lines: list[_AlignLine] = []
        self._line_map: dict[int, _AlignLine] = {}

    def bind(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline

    def _find_line(self, mobj, axis):
        lid = id(mobj)
        if lid in self._line_map and self._line_map[lid].axis == axis:
            return self._line_map[lid]
        return None

    def _find_or_create_line(self, mobj, axis):
        line = self._find_line(mobj, axis)
        if line is not None:
            return line
        line = _AlignLine(axis, [mobj])
        self._lines.append(line)
        self._line_map[id(mobj)] = line
        return line

    def group_for(self, obj):
        return self._line_map.get(id(obj))

    def shift_group(self, group, vector):
        for m in group.members:
            m.shift(vector)

    def redistribute_group(self, group, buff):
        group.redistribute(buff)

    def remove(self, obj):
        if id(obj) in self._line_map:
            line = self._line_map.pop(id(obj))
            line.members = [m for m in line.members if id(m) != id(obj)]
            if not line.members and line in self._lines:
                self._lines.remove(line)


class RowLayout(BaseLayoutStrategy):
    """水平行优先布局：LEFT/RIGHT 方向加入水平行，UP/DOWN 方向加入垂直列。

    这是当前 Pipeline.place() 的默认行为。
    """

    def place(self, obj, ref=None, direction=RIGHT, buff=None):
        buff = buff if buff is not None else (self._pipeline._overlap_buff or 0.1)

        if ref is None:
            from manim import ORIGIN

            obj.move_to(ORIGIN)
            axis = "h" if id(direction) in H_DIRS else "v"
            self._find_or_create_line(obj, axis)
        elif id(direction) in H_DIRS:
            obj.next_to(ref, direction, buff=buff)
            line = self._find_or_create_line(ref, "h")
            if id(obj) not in [id(m) for m in line.members]:
                line.members.append(obj)
                self._line_map[id(obj)] = line
        else:
            obj.next_to(ref, direction, buff=buff)
            line = self._find_or_create_line(ref, "v")
            if id(obj) not in [id(m) for m in line.members]:
                line.members.append(obj)
                self._line_map[id(obj)] = line

        line = self.group_for(obj)
        if line:
            line.redistribute(buff)


class ColumnLayout(BaseLayoutStrategy):
    """垂直列优先布局：UP/DOWN 方向加入垂直列，LEFT/RIGHT 方向加入水平行。"""

    def place(self, obj, ref=None, direction=RIGHT, buff=None):
        buff = buff if buff is not None else (self._pipeline._overlap_buff or 0.1)

        if ref is None:
            from manim import ORIGIN

            obj.move_to(ORIGIN)
            axis = "v" if id(direction) in V_DIRS else "h"
            self._find_or_create_line(obj, axis)
        elif id(direction) in V_DIRS:
            obj.next_to(ref, direction, buff=buff)
            line = self._find_or_create_line(ref, "v")
            if id(obj) not in [id(m) for m in line.members]:
                line.members.append(obj)
                self._line_map[id(obj)] = line
        else:
            obj.next_to(ref, direction, buff=buff)
            line = self._find_or_create_line(ref, "h")
            if id(obj) not in [id(m) for m in line.members]:
                line.members.append(obj)
                self._line_map[id(obj)] = line

        line = self.group_for(obj)
        if line:
            line.redistribute(buff)


class FreeLayout(BaseLayoutStrategy):
    """自由布局：不自动定位，仅将对象注册进系统让重叠检测生效。

    适合子场景自行使用 manim 原生 API (next_to, arrange, to_edge 等)
    完成所有位置编排的场景。
    """

    def place(self, obj, ref=None, direction=RIGHT, buff=None):
        if self.group_for(obj) is None:
            self._find_or_create_line(obj, "h")
