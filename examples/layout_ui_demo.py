import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *
from framework import Pipeline, SceneSegment
from framework.strategies import FreeLayout


class FillScene(SceneSegment):
    """用大量方块填满场景，迫使下一个对象放不下"""

    def play(self):
        for i in range(20):
            s = Square(
                side_length=0.8,
                fill_opacity=1,
                fill_color=interpolate_color(RED, BLUE, i / 19),
                stroke_color=WHITE,
            )
            self.im.pipeline.place(
                s,
                direction=RIGHT if i > 0 else None,
                ref=self.ctx.get("last") if i > 0 else None,
            )
            self.ctx.put("last", s)

        self.scene.play(*[FadeIn(m) for m in self.scene.mobjects])


class OverflowScene(SceneSegment):
    """再添加一个方块，自动布局必然失败，触发交互 UI"""

    def play(self):
        extra = Square(
            side_length=0.8, fill_opacity=1, fill_color=YELLOW, stroke_color=WHITE
        )
        self.im.pipeline.place(extra)
        self.scene.play(FadeIn(extra))


class LayoutUIDemo(Scene):
    def construct(self):
        Pipeline(self, interactive=True).add(FillScene()).add(OverflowScene()).run()


class CenterFillSegment(SceneSegment):
    """演示重叠检测 → GUI 交互式放置

    流程拆解：
    1. 使用 FreeLayout — 不自动排列，place() 只注册不移动对象
    2. track(guard=False) 将前3个方块直接加入场景，跳过重叠验证
       - 这些方块不会被注册到策略的对齐行(_line_map)中
       - guard.validate() 消解重叠时，group_for() 对它们返回 None
       - 消解循环遇到 group_for=None 会 continue 跳过，无法自动消解
    3. place(yellow) 触发 guard.validate()：
       - 检测到 yellow 与前3个方块全部重叠
       - 5轮消解全部 skip → still_overlaps=True
       - pipeline.interactive=True → 返回 need_ui=True
       - 弹出 tkinter 窗口让用户手动拖拽
    4. GUI 中将4个方块拖到无重叠、无越界的位置 → "确认放置"亮起
       - 确认后应用位置到 manim 场景
    """

    layout = FreeLayout

    def play(self):
        # 前3个方块：全部放到中心，跳过验证
        # track(guard=False) = scene.add() + guard._accept()，不触发策略和守卫
        colors = [RED, BLUE, GREEN]
        for c in colors:
            s = Square(side_length=1, fill_opacity=1, fill_color=c, stroke_color=WHITE)
            s.move_to(ORIGIN)
            self.im.pipeline.track(s, guard=False)

        # 第4个方块：同样放到中心，但走完整的 place() 流程
        # place() → strategy.place() → guard.validate() → 检测到重叠 → need_ui=True → 弹出 GUI
        yellow = Square(side_length=1, fill_opacity=1, fill_color=YELLOW, stroke_color=WHITE)
        yellow.move_to(ORIGIN)
        self.im.pipeline.place(yellow)


class OverflowDemo(Scene):
    """触发交互式放置 UI 的演示

    运行后会弹出 tkinter 窗口：
    - 4个方块初始全部重叠在中心（红/蓝/绿叠在底层，黄色菱形标记在顶层）
    - 拖拽各方块到不重叠的位置
    - 全部无冲突时边框变绿，"确认放置"按钮亮起
    - 点击确认后位置写回 manim 场景，继续渲染
    """

    def construct(self):
        Pipeline(self, interactive=True).add(CenterFillSegment()).run()
