from manim import *


class TextGrid(VGroup):
    """可配置的文本网格，支持逐格着色、行列批量着色、文字自适应

    Parameters
    ----------
    rows : int
        行数
    cols : int
        列数
    cell_size : float
        格子边长
    buff : float
        格子间距
    fill_opacity : float
        格子填充透明度，默认 1.0
    stroke_width : float
        格子边框线宽，默认 1.0
    texts : list[list[str]] | dict[tuple[int,int], str] | None
        格子中的文本。2D列表中空字符串/None表示无文本；字典仅填充指定位置
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        cell_size: float = 0.8,
        buff: float = 0.1,
        fill_opacity: float = 1.0,
        stroke_width: float = 1.0,
        texts: list | dict | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._rows = rows
        self._cols = cols
        self._cell_size = cell_size
        self._buff = buff
        self._fill_opacity = fill_opacity
        self._stroke_width = stroke_width

        self._bgs = [[None] * cols for _ in range(rows)]
        self._labels = [[None] * cols for _ in range(rows)]

        for r in range(rows):
            for c in range(cols):
                bg = Square(
                    side_length=cell_size,
                    fill_opacity=fill_opacity,
                    fill_color=BLACK,
                    stroke_width=stroke_width,
                    stroke_color=WHITE,
                )
                self._bgs[r][c] = bg
                self.add(bg)

        self._layout()

        if texts is not None:
            if isinstance(texts, dict):
                for (r, c), text in texts.items():
                    self.set_cell_text(r, c, text)
            else:
                for r in range(min(len(texts), rows)):
                    for c in range(min(len(texts[r]), cols)):
                        if texts[r][c]:
                            self.set_cell_text(r, c, texts[r][c])

    def _layout(self):
        for r in range(self._rows):
            for c in range(self._cols):
                x = (c - (self._cols - 1) / 2) * (self._cell_size + self._buff)
                y = ((self._rows - 1) / 2 - r) * (self._cell_size + self._buff)
                self._bgs[r][c].move_to(x * RIGHT + y * UP)
                if self._labels[r][c] is not None:
                    self._labels[r][c].move_to(self._bgs[r][c])

    def _fit_text(self, text_str, color=WHITE):
        txt = Text(text_str, font_size=24, color=color)
        max_dim = self._cell_size * 0.65
        scale = min(max_dim / txt.width, max_dim / txt.height)
        txt.scale(scale)
        return txt

    # ---- 文本操作 ----

    def set_cell_text(self, r, c, text_str, color=WHITE):
        if self._labels[r][c] is not None:
            self.remove(self._labels[r][c])
        txt = self._fit_text(text_str, color)
        txt.move_to(self._bgs[r][c])
        self._labels[r][c] = txt
        self.add(txt)
        return self

    # ---- 背景色 ----

    def set_cell_color(self, r, c, color):
        self._bgs[r][c].set_fill(color)
        return self

    def set_cells_color(self, positions, color):
        for r, c in positions:
            self.set_cell_color(r, c, color)
        return self

    def set_row_color(self, row, color):
        for c in range(self._cols):
            self.set_cell_color(row, c, color)
        return self

    def set_col_color(self, col, color):
        for r in range(self._rows):
            self.set_cell_color(r, col, color)
        return self

    # ---- 透明度 ----

    def set_fill_opacity(self, opacity):
        self._fill_opacity = opacity
        for r in range(self._rows):
            for c in range(self._cols):
                self._bgs[r][c].set_fill(opacity=opacity)
        return self

    def set_cell_fill_opacity(self, r, c, opacity):
        self._bgs[r][c].set_fill(opacity=opacity)
        return self

    # ---- 线宽 ----

    def set_stroke_width(self, width):
        self._stroke_width = width
        for r in range(self._rows):
            for c in range(self._cols):
                self._bgs[r][c].set_stroke(width=width)
        return self

    def set_cell_stroke_width(self, r, c, width):
        self._bgs[r][c].set_stroke(width=width)
        return self

    # ---- 文字色 ----

    def set_text_color(self, r, c, color):
        if self._labels[r][c] is not None:
            self._labels[r][c].set_color(color)
        return self

    def set_row_text_color(self, row, color):
        for c in range(self._cols):
            self.set_text_color(row, c, color)
        return self

    def set_col_text_color(self, col, color):
        for r in range(self._rows):
            self.set_text_color(r, col, color)
        return self

    # ---- 访问器 ----

    def get_cell(self, r, c):
        return self._bgs[r][c]

    def get_label(self, r, c):
        return self._labels[r][c]
