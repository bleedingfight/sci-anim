import numpy as np
from manim import UP, DOWN, LEFT, RIGHT

H_DIRS = {id(LEFT), id(RIGHT)}
V_DIRS = {id(UP), id(DOWN)}


class _AlignLine:
    """一行或一列对齐对象的容器"""

    def __init__(self, axis, members):
        self.axis = axis  # "h" or "v"
        self.members = list(members)

    def redistribute(self, buff):
        if len(self.members) < 2:
            return

        if self.axis == "h":
            key = lambda m: m.get_center()[0]
            widths = [m.get_width() for m in self.members]
            positions = [m.get_center()[0] for m in self.members]
        else:
            key = lambda m: m.get_center()[1]
            widths = [m.get_height() for m in self.members]
            positions = [m.get_center()[1] for m in self.members]

        self.members.sort(key=key)

        n = len(self.members)
        total = sum(widths) + (n - 1) * buff
        anchor = np.mean(positions)
        start = anchor - total / 2

        offset = start + widths[0] / 2
        for i, m in enumerate(self.members):
            if self.axis == "h":
                m.move_to(offset * RIGHT + m.get_center()[1] * UP)
            else:
                m.move_to(m.get_center()[0] * RIGHT + offset * UP)
            offset += widths[i] / 2 + buff
            if i < n - 1:
                offset += widths[i + 1] / 2


def _bb_overlaps(a, b):
    al, ar = a.get_left()[0], a.get_right()[0]
    ab, at = a.get_bottom()[1], a.get_top()[1]
    bl, br = b.get_left()[0], b.get_right()[0]
    bb, bt = b.get_bottom()[1], b.get_top()[1]
    return al < br and bl < ar and ab < bt and bb < at


def _out_of_bounds(mobj, hw, hh):
    return (
        mobj.get_left()[0] < -hw
        or mobj.get_right()[0] > hw
        or mobj.get_bottom()[1] < -hh
        or mobj.get_top()[1] > hh
    )


def _center_layout(mobjects):
    if not mobjects:
        return
    left = min(m.get_left()[0] for m in mobjects)
    right = max(m.get_right()[0] for m in mobjects)
    bottom = min(m.get_bottom()[1] for m in mobjects)
    top = max(m.get_top()[1] for m in mobjects)
    cx, cy = (left + right) / 2, (bottom + top) / 2
    shift = -cx * RIGHT - cy * UP
    for m in mobjects:
        m.shift(shift)
