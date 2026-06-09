import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *
from mobjects import TextGrid


class TextGridDemo(Scene):
    """展示 TextGrid 的基本功能：构造、填充文本、行列着色、单格高亮"""

    def construct(self):
        grid = TextGrid(
            rows=3,
            cols=4,
            cell_size=0.8,
            buff=0.1,
            texts=[
                ["1", "2", "3", "4"],
                ["5", "6", "7", "8"],
                ["9", "10", "11", "12"],
            ],
        )
        grid.set_row_color(0, DARK_GREY)
        grid.set_col_color(1, DARK_GREY)
        grid.set_cell_color(1, 2, RED)
        grid.set_row_text_color(0, YELLOW)
        grid.set_col_text_color(1, ORANGE)
        grid.set_text_color(1, 2, WHITE)

        self.play(FadeIn(grid))
        self.wait()


class TextGridSparseDemo(Scene):
    """展示字典方式稀疏填充文本"""

    def construct(self):
        grid = TextGrid(
            rows=4,
            cols=4,
            cell_size=0.7,
            texts={(0, 0): "A", (1, 1): "B", (2, 2): "C", (3, 3): "D"},
        )
        grid.set_cells_color([(0, 0), (1, 1), (2, 2), (3, 3)], BLUE_D)
        grid.set_col_text_color(0, YELLOW)
        grid.set_col_text_color(3, ORANGE)

        self.play(FadeIn(grid))
        self.wait()


class TextGridAnimDemo(Scene):
    """展示对 TextGrid 子对象的动画操作"""

    def construct(self):
        grid = TextGrid(
            3,
            3,
            cell_size=1.0,
            texts=[
                ["X", "O", "X"],
                ["O", "X", "O"],
                ["X", "O", "X"],
            ],
        )
        grid.set_cell_color(0, 0, BLUE_D)
        grid.set_cell_color(1, 1, BLUE_D)
        grid.set_cell_color(2, 2, BLUE_D)
        grid.set_text_color(0, 0, YELLOW)
        grid.set_text_color(1, 1, YELLOW)
        grid.set_text_color(2, 2, YELLOW)

        self.play(FadeIn(grid))

        # 逐格高亮对角线
        for r, c in [(0, 0), (1, 1), (2, 2)]:
            cell = grid.get_cell(r, c)
            self.play(
                cell.animate.set_fill(YELLOW),
                run_time=0.4,
            )
        self.wait()

        # 恢复原色
        for r, c in [(0, 0), (1, 1), (2, 2)]:
            cell = grid.get_cell(r, c)
            self.play(
                cell.animate.set_fill(BLUE_D),
                run_time=0.4,
            )
        self.wait()


class TextGridStyleDemo(Scene):
    """展示透明度和线宽控制"""

    def construct(self):
        # 半透明 + 细边框
        g1 = TextGrid(
            2,
            2,
            cell_size=0.9,
            fill_opacity=0.5,
            stroke_width=0.5,
            texts=[["A", "B"], ["C", "D"]],
        )
        g1.set_row_color(0, BLUE_D)
        g1.set_row_color(1, DARK_GREY)
        g1.shift(LEFT * 2.5)

        # 全不透明 + 粗边框
        g2 = TextGrid(
            2,
            2,
            cell_size=0.9,
            fill_opacity=1.0,
            stroke_width=3,
            texts=[["W", "X"], ["Y", "Z"]],
        )
        g2.set_row_color(0, RED_D)
        g2.set_row_color(1, DARK_GREY)
        g2.shift(RIGHT * 2.5)

        label1 = Text("opacity=0.5  width=0.5", font_size=18).next_to(
            g1, DOWN, buff=0.3
        )
        label2 = Text("opacity=1.0  width=3", font_size=18).next_to(g2, DOWN, buff=0.3)

        self.play(FadeIn(g1), FadeIn(g2))
        self.play(FadeIn(label1), FadeIn(label2))
        self.wait()

        # 动态修改：整个网格调整透明度和线宽
        self.play(g1.animate.set_fill_opacity(1.0), g1.animate.set_stroke_width(3))
        self.play(
            label1.animate.become(
                Text("opacity=1.0  width=3", font_size=18).next_to(g1, DOWN, buff=0.3)
            )
        )
        self.wait()
