import numpy as np
from manim import UP, DOWN, LEFT, RIGHT
import tkinter as tk
from tkinter import ttk


class _PlacementUI:
    """当自动布局失败时，弹出 tkinter 窗口让用户手动放置对象。

    支持功能：
    - 拖拽移动所有对象（已有 + 新增）
    - Shift+点击多选，拖拽时保持组内相对位置
    - 滚轮缩放选中对象
    - 不同形状/大小的对象等比例映射
    - 实时冲突检测：绿色边框=合法，红色边框=冲突/越界
    - 原子组合对象（如矩形+文字）作为一个整体检测重叠
    """

    CANVAS_PADDING = 40

    def __init__(self, scene_mobjects, new_mobj, frame_w, frame_h, buff,
                 atomic_groups=None, excluded_ids=None):
        self.frame_w = frame_w
        self.frame_h = frame_h
        self.buff = buff
        self.result = None  # ("placed", results_dict) or ("rejected",)

        max_dim = max(frame_w, frame_h)
        self.canvas_px = 720
        self.scale = self.canvas_px / max_dim

        # 原子组：组合对象应作为整体参与重叠检测
        self._atomic_groups = atomic_groups or {}   # id(vgroup) -> vgroup
        self._excluded_ids = excluded_ids or set()   # 子对象 id 集合

        # 所有对象数据：已有 + 新增（零尺寸对象不展示）
        self.items = []
        for m in scene_mobjects:
            if id(m) in self._excluded_ids:
                continue
            if m.get_width() > 0 and m.get_height() > 0:
                self.items.append(self._make_item(m, is_new=False))
        if new_mobj.get_width() > 0 and new_mobj.get_height() > 0:
            self.items.append(self._make_item(new_mobj, is_new=True))

        self.selection = set()  # 选中的 item 索引

        self._run()

    # ------------------------------------------------------------------
    # 类型→颜色 & 类型缩写
    # ------------------------------------------------------------------

    # 颜色按类别分组：几何体=绿、曲线=紫、文本=蓝、线条/箭头=黄、
    # 组合=灰、点/标记=红、多边形=青、3D=棕、图/表=橙、坐标系=靛、工具=暗灰
    _TYPE_PALETTE = {
        # --- 几何体 ---
        "Square": "#2d7d46",
        "Rectangle": "#2d7d46",
        "RoundedRectangle": "#2d7d46",
        "FullScreenRectangle": "#2d7d46",
        "ScreenRectangle": "#2d7d46",
        "BackgroundRectangle": "#2d7d46",
        "SurroundingRectangle": "#2d7d46",
        "Circle": "#7d2d6e",
        "Annulus": "#7d2d6e",
        "AnnularSector": "#7d2d6e",
        "Sector": "#7d2d6e",
        "Ellipse": "#7d2d6e",
        "Dot": "#7d2d2d",
        "AnnotationDot": "#7d2d2d",
        "LabeledDot": "#7d2d2d",
        "PointCloudDot": "#7d2d2d",
        "Dot3D": "#7d2d2d",
        "Star": "#7d2d2d",
        "Cross": "#7d2d2d",
        # --- 多边形 ---
        "Polygon": "#2d7d6e",
        "Triangle": "#2d7d6e",
        "RegularPolygon": "#2d7d6e",
        "RegularPolygram": "#2d7d6e",
        "Polygram": "#2d7d6e",
        "Polyhedron": "#2d7d6e",
        "Tetrahedron": "#2d7d6e",
        "Octahedron": "#2d7d6e",
        "Dodecahedron": "#2d7d6e",
        "Icosahedron": "#2d7d6e",
        "ConvexHull": "#2d7d6e",
        "ConvexHull3D": "#2d7d6e",
        # --- 曲线/弧 ---
        "Arc": "#6e2d7d",
        "ArcBetweenPoints": "#6e2d7d",
        "ArcPolygon": "#6e2d7d",
        "ArcPolygonFromArcs": "#6e2d7d",
        "ArcBrace": "#6e2d7d",
        "RightAngle": "#6e2d7d",
        "Angle": "#6e2d7d",
        "CubicBezier": "#6e2d7d",
        "ParametricFunction": "#6e2d7d",
        "FunctionGraph": "#6e2d7d",
        "ImplicitFunction": "#6e2d7d",
        "Cutout": "#6e2d7d",
        "TangentialArc": "#6e2d7d",
        "Difference": "#6e2d7d",
        "Exclusion": "#6e2d7d",
        "Intersection": "#6e2d7d",
        "Union": "#6e2d7d",
        # --- 线条/箭头 ---
        "Line": "#6e6e2d",
        "DashedLine": "#6e6e2d",
        "TangentLine": "#6e6e2d",
        "Elbow": "#6e6e2d",
        "Arrow": "#6e6e2d",
        "DoubleArrow": "#6e6e2d",
        "CurvedArrow": "#6e6e2d",
        "CurvedDoubleArrow": "#6e6e2d",
        "LabeledArrow": "#6e6e2d",
        "LabeledLine": "#6e6e2d",
        "Vector": "#6e6e2d",
        "Arrow3D": "#6e6e2d",
        "Line3D": "#6e6e2d",
        "ArrowCircleFilledTip": "#6e6e2d",
        "ArrowCircleTip": "#6e6e2d",
        "ArrowSquareFilledTip": "#6e6e2d",
        "ArrowSquareTip": "#6e6e2d",
        "ArrowTriangleFilledTip": "#6e6e2d",
        "ArrowTriangleTip": "#6e6e2d",
        "StealthTip": "#6e6e2d",
        "ArrowTip": "#6e6e2d",
        "Underline": "#6e6e2d",
        # --- 文本/数学 ---
        "Text": "#2d5a7d",
        "MarkupText": "#2d5a7d",
        "MathTex": "#2d5a7d",
        "Tex": "#2d5a7d",
        "SingleStringMathTex": "#2d5a7d",
        "Paragraph": "#2d5a7d",
        "BulletedList": "#2d5a7d",
        "Title": "#2d5a7d",
        "Code": "#2d5a7d",
        "Label": "#2d5a7d",
        "Brace": "#2d5a7d",
        "BraceBetweenPoints": "#2d5a7d",
        "BraceLabel": "#2d5a7d",
        "BraceText": "#2d5a7d",
        # --- 表格/矩阵 ---
        "Table": "#7d5a2d",
        "MathTable": "#7d5a2d",
        "MobjectTable": "#7d5a2d",
        "IntegerTable": "#7d5a2d",
        "DecimalTable": "#7d5a2d",
        "Matrix": "#7d5a2d",
        "IntegerMatrix": "#7d5a2d",
        "DecimalMatrix": "#7d5a2d",
        "MobjectMatrix": "#7d5a2d",
        "Integer": "#7d5a2d",
        "DecimalNumber": "#7d5a2d",
        # --- 图 ---
        "Graph": "#7d6e2d",
        "DiGraph": "#7d6e2d",
        "BarChart": "#7d6e2d",
        # --- 组合 ---
        "VGroup": "#5a5a5a",
        "Group": "#5a5a5a",
        "VDict": "#5a5a5a",
        "PGroup": "#5a5a5a",
        "CurvesAsSubmobjects": "#5a5a5a",
        "DashedVMobject": "#5a5a5a",
        "VMobjectFromSVGPath": "#5a5a5a",
        "SVGMobject": "#5a5a5a",
        "LabeledPolygram": "#5a5a5a",
        "AnimatedBoundary": "#5a5a5a",
        "ManimBanner": "#5a5a5a",
        # --- 3D 体 ---
        "Sphere": "#7d6e2d",
        "Cube": "#7d6e2d",
        "Cylinder": "#7d6e2d",
        "Cone": "#7d6e2d",
        "Torus": "#7d6e2d",
        "Prism": "#7d6e2d",
        "Surface": "#7d6e2d",
        # --- 坐标系 ---
        "Axes": "#2d4a6e",
        "ThreeDAxes": "#2d4a6e",
        "NumberLine": "#2d4a6e",
        "NumberPlane": "#2d4a6e",
        "PolarPlane": "#2d4a6e",
        "ComplexPlane": "#2d4a6e",
        "UnitInterval": "#2d4a6e",
        # --- 图像/其他 ---
        "ImageMobject": "#6e5a2d",
        "ImageMobjectFromCamera": "#6e5a2d",
        # --- SVG 内部类型 ---
        "VMobjectFromSVGPath": "#5a5a5a",
        # --- 自定义 mobject ---
        "TextGrid": "#2d7d6e",
        "SampleSpace": "#5a5a5a",
        "StreamLines": "#6e6e2d",
        "VectorField": "#6e6e2d",
        "ArrowVectorField": "#6e6e2d",
        "TracedPath": "#6e6e2d",
    }
    _DEFAULT_UI_COLOR = "#4a4a5a"

    # 按类别分组的缩写映射，同类同前缀便于识别
    _TYPE_ABBR = {
        # 几何体
        "Square": "SQR",
        "Rectangle": "REC",
        "RoundedRectangle": "RREC",
        "FullScreenRectangle": "FSR",
        "ScreenRectangle": "SCR",
        "BackgroundRectangle": "BGR",
        "SurroundingRectangle": "SUR",
        "Circle": "CIR",
        "Annulus": "ANN",
        "AnnularSector": "ASCT",
        "Sector": "SCT",
        "Ellipse": "ELP",
        "Dot": "Dot",
        "AnnotationDot": "ADot",
        "LabeledDot": "LDot",
        "PointCloudDot": "PCD",
        "Dot3D": "D3D",
        "Star": "Star",
        "Cross": "Cro",
        # 多边形
        "Polygon": "POL",
        "Triangle": "TRI",
        "RegularPolygon": "RPOL",
        "RegularPolygram": "RPGM",
        "Polygram": "PGM",
        "Polyhedron": "PHD",
        "Tetrahedron": "THD",
        "Octahedron": "OHD",
        "Dodecahedron": "DHD",
        "Icosahedron": "IHD",
        "ConvexHull": "CVH",
        "ConvexHull3D": "CV3",
        # 曲线/弧
        "Arc": "Arc",
        "ArcBetweenPoints": "AbP",
        "ArcPolygon": "APol",
        "ArcPolygonFromArcs": "APfA",
        "ArcBrace": "ABrc",
        "RightAngle": "RAng",
        "Angle": "Ang",
        "CubicBezier": "CBez",
        "ParametricFunction": "PFn",
        "FunctionGraph": "FGr",
        "ImplicitFunction": "IFn",
        "Cutout": "Cut",
        "TangentialArc": "TAr",
        "Difference": "Dif",
        "Exclusion": "Exc",
        "Intersection": "Int",
        "Union": "Uni",
        # 线条/箭头
        "Line": "Lin",
        "DashedLine": "DLin",
        "TangentLine": "TLin",
        "Elbow": "Elb",
        "Arrow": "Arr",
        "DoubleArrow": "DArr",
        "CurvedArrow": "CArr",
        "CurvedDoubleArrow": "CDAr",
        "LabeledArrow": "LArr",
        "LabeledLine": "LLin",
        "Vector": "Vec",
        "Arrow3D": "A3D",
        "Line3D": "L3D",
        "ArrowCircleFilledTip": "ACFT",
        "ArrowCircleTip": "ACTp",
        "ArrowSquareFilledTip": "ASFT",
        "ArrowSquareTip": "ASTp",
        "ArrowTriangleFilledTip": "ATFT",
        "ArrowTriangleTip": "ATTp",
        "StealthTip": "STip",
        "ArrowTip": "ATp",
        "Underline": "Udl",
        # 文本
        "Text": "Txt",
        "MarkupText": "MTxt",
        "MathTex": "MTX",
        "Tex": "TeX",
        "SingleStringMathTex": "SMTX",
        "Paragraph": "Pgr",
        "BulletedList": "BLst",
        "Title": "Ttl",
        "Code": "Code",
        "Label": "Lbl",
        "Brace": "Brc",
        "BraceBetweenPoints": "BbP",
        "BraceLabel": "BLbl",
        "BraceText": "BTxt",
        # 表格/矩阵/数值
        "Table": "Tab",
        "MathTable": "MTab",
        "MobjectTable": "MoTb",
        "IntegerTable": "ITab",
        "DecimalTable": "DTab",
        "Matrix": "Mat",
        "IntegerMatrix": "IMat",
        "DecimalMatrix": "DMat",
        "MobjectMatrix": "MoMx",
        "Integer": "Int",
        "DecimalNumber": "Dec",
        # 图
        "Graph": "Gph",
        "DiGraph": "DGph",
        "BarChart": "BChrt",
        # 组合
        "VGroup": "VGr",
        "Group": "Grp",
        "VDict": "VDct",
        "PGroup": "PGr",
        "CurvesAsSubmobjects": "Crvs",
        "DashedVMobject": "DVMo",
        "VMobjectFromSVGPath": "SVGp",
        "SVGMobject": "SVG",
        "LabeledPolygram": "LPgm",
        "AnimatedBoundary": "ABnd",
        "ManimBanner": "Bnnr",
        # 3D 体
        "Sphere": "Sph",
        "Cube": "Cube",
        "Cylinder": "Cyl",
        "Cone": "Cone",
        "Torus": "Tors",
        "Prism": "Prsm",
        "Surface": "Srf",
        # 坐标系
        "Axes": "Axes",
        "ThreeDAxes": "3Axs",
        "NumberLine": "NLine",
        "NumberPlane": "NPln",
        "PolarPlane": "PPln",
        "ComplexPlane": "CPln",
        "UnitInterval": "UItv",
        # 图像
        "ImageMobject": "Img",
        "ImageMobjectFromCamera": "ICam",
        # SVG 内部类型
        "VMobjectFromSVGPath": "SVGp",
        # 自定义 mobject
        "TextGrid": "TGr",
        # 工具类（无视觉面积，不会出现在 UI 中但保留缩写以防万一）
        "ValueTracker": "VT",
        "ComplexValueTracker": "CVT",
        "Variable": "Var",
        "VectorizedPoint": "VPT",
        "Point": "PT",
        # 其他
        "SampleSpace": "SplS",
        "StreamLines": "StrL",
        "VectorField": "VFd",
        "ArrowVectorField": "AVFd",
        "TracedPath": "TrP",
    }

    @classmethod
    def _type_abbr(cls, type_name):
        return cls._TYPE_ABBR.get(type_name, "M")

    def _make_item(self, m, is_new):
        type_name = type(m).__name__
        ui_color = self._TYPE_PALETTE.get(type_name, self._DEFAULT_UI_COLOR)
        label = "N" if is_new else self._type_abbr(type_name)
        is_atomic = id(m) in self._atomic_groups
        return {
            "mobj": m,
            "box": self._box_from_mobj(m),
            "ui_color": ui_color,
            "label": label,
            "rect_id": None,
            "label_id": None,
            "is_new": is_new,
            "scale_factor": 1.0,
            "base_w": m.get_width(),
            "base_h": m.get_height(),
            "is_atomic": is_atomic,
        }

    @staticmethod
    def _box_from_mobj(m):
        return {
            "left": m.get_left()[0],
            "right": m.get_right()[0],
            "bottom": m.get_bottom()[1],
            "top": m.get_top()[1],
        }

    def _to_canvas(self, x, y):
        px = (x + self.frame_w / 2) * self.scale + self.CANVAS_PADDING
        py = (-y + self.frame_h / 2) * self.scale + self.CANVAS_PADDING
        return px, py

    def _from_canvas(self, px, py):
        x = (px - self.CANVAS_PADDING) / self.scale - self.frame_w / 2
        y = -(py - self.CANVAS_PADDING) / self.scale + self.frame_h / 2
        return x, y

    def _box_canvas_rect(self, box):
        x1, y1 = self._to_canvas(box["left"], box["top"])
        x2, y2 = self._to_canvas(box["right"], box["bottom"])
        return x1, y1, x2 - x1, y2 - y1

    def _update_box_from_scale(self, item):
        cx = (item["box"]["left"] + item["box"]["right"]) / 2
        cy = (item["box"]["bottom"] + item["box"]["top"]) / 2
        w = item["base_w"] * item["scale_factor"]
        h = item["base_h"] * item["scale_factor"]
        item["box"] = {
            "left": cx - w / 2,
            "right": cx + w / 2,
            "bottom": cy - h / 2,
            "top": cy + h / 2,
        }

    def _boxes_overlap(self, a, b):
        return (
            a["left"] < b["right"]
            and b["left"] < a["right"]
            and a["bottom"] < b["top"]
            and b["bottom"] < a["top"]
        )

    def _box_oob(self, box):
        hw, hh = self.frame_w / 2, self.frame_h / 2
        return (
            box["left"] < -hw
            or box["right"] > hw
            or box["bottom"] < -hh
            or box["top"] > hh
        )

    def _check_global_conflict(self):
        """检查是否有任何一对对象重叠，或任何对象越界。"""
        for i in range(len(self.items)):
            for j in range(i + 1, len(self.items)):
                if self._boxes_overlap(self.items[i]["box"], self.items[j]["box"]):
                    return True
            if self._box_oob(self.items[i]["box"]):
                return True
        return False

    def _item_at(self, px, py):
        """返回画布像素坐标处最上层 item 的索引。"""
        for i in range(len(self.items) - 1, -1, -1):
            x1, y1, w, h = self._box_canvas_rect(self.items[i]["box"])
            if x1 <= px <= x1 + w and y1 <= py <= y1 + h:
                return i
        return None

    # ------------------------------------------------------------------
    # UI 搭建
    # ------------------------------------------------------------------

    def _run(self):
        self.root = tk.Tk()
        self.root.title("手动放置对象")
        self.root.resizable(False, False)

        cw = int(self.frame_w * self.scale) + 2 * self.CANVAS_PADDING
        ch = int(self.frame_h * self.scale) + 2 * self.CANVAS_PADDING

        # 顶部提示
        top = ttk.Frame(self.root)
        top.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(
            top,
            text=(
                "点击选中 | Shift+点击多选 | 拖拽移动 | "
                "滚轮缩放选中对象 | 绿框=全部合法 红框=存在冲突或越界"
            ),
            wraplength=cw - 16,
        ).pack()

        # 画布
        self.canvas = tk.Canvas(self.root, width=cw, height=ch, bg="#1a1a2e")
        self.canvas.pack(padx=8, pady=4)

        # 画面边框
        self.canvas.create_rectangle(
            self.CANVAS_PADDING,
            self.CANVAS_PADDING,
            self.CANVAS_PADDING + self.frame_w * self.scale,
            self.CANVAS_PADDING + self.frame_h * self.scale,
            outline="#444466",
            width=2,
            dash=(4, 4),
        )

        # 绘制所有对象矩形
        for i, item in enumerate(self.items):
            x, y, w, h = self._box_canvas_rect(item["box"])
            outline = "#888888" if not item["is_new"] else "#00ff00"
            width = 2 if item["is_new"] else 1
            item["rect_id"] = self.canvas.create_rectangle(
                x,
                y,
                x + w,
                y + h,
                fill=item["ui_color"],
                outline=outline,
                width=width,
            )
            # 新对象用虚线边框 + 菱形标识
            if item["is_new"]:
                self.canvas.itemconfig(item["rect_id"], dash=(6, 3))
                # 在矩形内部画菱形小标记
                cx_px, cy_px = x + w / 2, y + h / 2
                d = min(w, h) * 0.25
                item["diamond_id"] = self.canvas.create_polygon(
                    cx_px,
                    cy_px - d,
                    cx_px + d,
                    cy_px,
                    cx_px,
                    cy_px + d,
                    cx_px - d,
                    cy_px,
                    fill="#ffffff",
                    outline="#ffffff",
                    width=1,
                )
            item["label_id"] = self.canvas.create_text(
                x + w / 2,
                y + h / 2,
                text=item["label"],
                fill="white",
                font=("Consolas", 9, "bold"),
            )

        # 底部按钮
        bot = ttk.Frame(self.root)
        bot.pack(fill="x", padx=8, pady=(4, 8))
        self.confirm_btn = ttk.Button(bot, text="确认放置", command=self._confirm)
        self.confirm_btn.pack(side="left", padx=4)
        ttk.Button(bot, text="放弃添加", command=self._reject).pack(
            side="right", padx=4
        )

        # 交互绑定
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_scroll)
        self.canvas.bind("<Button-4>", lambda e: self._on_scroll_linux(1))
        self.canvas.bind("<Button-5>", lambda e: self._on_scroll_linux(-1))

        self._drag_start = None
        self._drag_offsets = {}  # 索引 → (dx0, dy0) 选中对象在拖拽开始时相对于鼠标的偏移

        self._refresh_all_outlines()

        self.root.mainloop()

    # ------------------------------------------------------------------
    # 选中与拖拽
    # ------------------------------------------------------------------

    def _on_press(self, event):
        idx = self._item_at(event.x, event.y)
        if idx is None:
            self.selection.clear()
            self._refresh_all_outlines()
            return

        shift = bool(event.state & 0x1)
        if shift:
            self.selection.symmetric_difference_update({idx})
        else:
            if idx not in self.selection:
                self.selection = {idx}

        self._refresh_all_outlines()

        # 记录拖拽偏移
        self._drag_start = (event.x, event.y)
        self._drag_offsets = {}
        for i in self.selection:
            coords = self.canvas.coords(self.items[i]["rect_id"])
            ix = coords[0] + (coords[2] - coords[0]) / 2
            iy = coords[1] + (coords[3] - coords[1]) / 2
            self._drag_offsets[i] = (event.x - ix, event.y - iy)

    def _on_drag(self, event):
        if self._drag_start is None or not self.selection:
            return
        for i in self.selection:
            ox, oy = self._drag_offsets[i]
            new_cx = event.x - ox
            new_cy = event.y - oy
            # 更新逻辑位置
            lx, ly = self._from_canvas(new_cx, new_cy)
            w = self.items[i]["base_w"] * self.items[i]["scale_factor"]
            h = self.items[i]["base_h"] * self.items[i]["scale_factor"]
            self.items[i]["box"] = {
                "left": lx - w / 2,
                "right": lx + w / 2,
                "bottom": ly - h / 2,
                "top": ly + h / 2,
            }
            # 更新画布
            x1, y1, cw, ch = self._box_canvas_rect(self.items[i]["box"])
            self.canvas.coords(self.items[i]["rect_id"], x1, y1, x1 + cw, y1 + ch)
            self.canvas.coords(self.items[i]["label_id"], x1 + cw / 2, y1 + ch / 2)
            if "diamond_id" in self.items[i]:
                d = min(cw, ch) * 0.25
                cx_px, cy_px = x1 + cw / 2, y1 + ch / 2
                self.canvas.coords(
                    self.items[i]["diamond_id"],
                    cx_px,
                    cy_px - d,
                    cx_px + d,
                    cy_px,
                    cx_px,
                    cy_px + d,
                    cx_px - d,
                    cy_px,
                )
        self._refresh_all_outlines()

    def _on_release(self, event):
        self._drag_start = None

    # ------------------------------------------------------------------
    # 缩放
    # ------------------------------------------------------------------

    def _on_scroll(self, event):
        factor = 0.95 if event.delta > 0 else 1.05
        self._apply_scale(factor)

    def _on_scroll_linux(self, direction):
        factor = 0.95 if direction > 0 else 1.05
        self._apply_scale(factor)

    def _apply_scale(self, factor):
        if not self.selection:
            return
        for i in self.selection:
            new_sf = self.items[i]["scale_factor"] * factor
            if new_sf < 0.2 or new_sf > 3.0:
                continue
            self.items[i]["scale_factor"] = new_sf
            self._update_box_from_scale(self.items[i])
            x1, y1, cw, ch = self._box_canvas_rect(self.items[i]["box"])
            self.canvas.coords(self.items[i]["rect_id"], x1, y1, x1 + cw, y1 + ch)
            self.canvas.coords(self.items[i]["label_id"], x1 + cw / 2, y1 + ch / 2)
            if "diamond_id" in self.items[i]:
                d = min(cw, ch) * 0.25
                cx_px, cy_px = x1 + cw / 2, y1 + ch / 2
                self.canvas.coords(
                    self.items[i]["diamond_id"],
                    cx_px,
                    cy_px - d,
                    cx_px + d,
                    cy_px,
                    cx_px,
                    cy_px + d,
                    cx_px - d,
                    cy_px,
                )
        self._refresh_all_outlines()

    # ------------------------------------------------------------------
    # 边框刷新与确认
    # ------------------------------------------------------------------

    def _refresh_all_outlines(self):
        has_conflict = self._check_global_conflict()
        for i, item in enumerate(self.items):
            if has_conflict or self._box_oob(item["box"]):
                outline = "#ff4444"
            elif i in self.selection:
                outline = "#44aaff"
            elif item["is_new"]:
                outline = "#00ff88"
            else:
                outline = "#888888"
            w = 3 if (i in self.selection or item["is_new"]) else 1
            self.canvas.itemconfig(item["rect_id"], outline=outline, width=w)
            # 选中对象取消虚线
            if item["is_new"]:
                if i in self.selection:
                    self.canvas.itemconfig(item["rect_id"], dash=())
                else:
                    self.canvas.itemconfig(item["rect_id"], dash=(6, 3))

        self.confirm_btn.state(["!disabled"] if not has_conflict else ["disabled"])

    def _confirm(self):
        if self._check_global_conflict():
            return
        # 收集所有已有对象的位移结果
        existing_results = {}
        for i, item in enumerate(self.items):
            if not item["is_new"]:
                cx = (item["box"]["left"] + item["box"]["right"]) / 2
                cy = (item["box"]["bottom"] + item["box"]["top"]) / 2
                existing_results[id(item["mobj"])] = (cx, cy, item["scale_factor"])
        # 新对象
        new_item = next(item for item in self.items if item["is_new"])
        cx = (new_item["box"]["left"] + new_item["box"]["right"]) / 2
        cy = (new_item["box"]["bottom"] + new_item["box"]["top"]) / 2
        self.result = ("placed", cx, cy, new_item["scale_factor"], existing_results)
        self.root.destroy()

    def _reject(self):
        self.result = ("rejected",)
        self.root.destroy()
