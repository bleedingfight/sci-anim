# sci-anim

基于 Manim 的科学动画框架，提供分镜编排、自动布局、交互式放置等功能。

## 项目结构

```
sci-anim/
├── framework.py          # 核心框架：分镜编排 + 布局引擎 + 交互式 UI
├── mobjects/              # 可复用的自定义 mobject
│   ├── __init__.py
│   └── text_grid.py       # TextGrid 文本网格组件
├── scenes/                # 分镜实现
│   ├── __init__.py
│   ├── scene_a.py
│   ├── scene_b.py
│   └── scene_c.py
├── examples/              # 可视化 demo
│   ├── layout_demo.py
│   ├── layout_ui_demo.py
│   ├── overlap_guard_demo.py
│   └── text_grid_demo.py
├── workflow.py             # 流水线组装
└── elegent.py              # 旧版示例
```

## 核心概念

### 分镜编排

通过 `SceneSegment` 定义分镜，`Pipeline` 链式组装：

```python
from framework import Pipeline, SceneSegment
from manim import Scene

class MySegment(SceneSegment):
    def play(self):
        # 创建 mobject 并播放动画
        pass

class MyVideo(Scene):
    def construct(self):
        Pipeline(self) \
            .add(MySegment()) \
            .add(AnotherSegment()) \
            .run()
```

分镜之间通过 `SceneContext` 共享状态：

```python
class SceneA(SceneSegment):
    def play(self):
        grid = TextGrid(3, 4, texts=[...])
        self.ctx.put("grid", grid)
        self.scene.play(FadeIn(grid))

class SceneB(SceneSegment):
    def play(self):
        grid = self.ctx.get("grid")
        # 继续操作
```

通过 `InteractionManager` 联动动画：

```python
class SceneB(SceneSegment):
    def play(self):
        self.im.register("highlight", [obj_a, obj_b])
        # 后续通过 trigger 触发所有注册对象的动画
        self.im.trigger("highlight", anim_func=lambda obj: Indicate(obj))
```

### 自动布局

通过 `Pipeline.place()` 以相对位置添加对象，系统自动保证无重叠、不越界：

```python
pipeline = self.im.pipeline

# 放到画面中心
pipeline.place(a)

# 放到 a 右侧，自动加入 a 的水平行
pipeline.place(b, ref=a, direction=RIGHT)

# 放到 a 下方，自动加入 a 的垂直列
pipeline.place(c, ref=a, direction=DOWN)
```

**布局规则：**

- 水平方向放置（LEFT/RIGHT）→ 加入参考对象的水平行，行内均匀重排
- 垂直方向放置（UP/DOWN）→ 加入参考对象的垂直列，列内均匀重排
- 跨行重叠时，被侵入的行整体平移让路，最多 5 轮迭代消解
- 越界时所有对象整体居中；居中后仍越界或仍有重叠则拒绝添加

**禁用布局引擎：**

```python
Pipeline(scene, overlap_buff=None)  # 禁用，退化为手动布局
```

### 交互式放置

当自动布局失败时（空间不足），弹出 tkinter 窗口让用户手动放置：

```python
Pipeline(scene, interactive=True)   # 默认启用
Pipeline(scene, interactive=False)   # 禁用，失败时直接警告拒绝
```

**交互操作：**

| 操作 | 说明 |
|------|------|
| 点击 | 选中对象 |
| Shift+点击 | 多选/取消选中 |
| 拖拽 | 移动选中对象，多选时保持相对位置 |
| 滚轮 | 缩放选中对象（0.2x ~ 3x） |
| 绿色边框 | 所有对象位置合法，可确认 |
| 红色边框 | 存在重叠或越界，确认按钮禁用 |

**UI 方块颜色与标签：**

UI 中每个矩形代表一个 mobject，按类型统一着色和标注：

| 类型 | 颜色 | 标签 |
|------|------|------|
| Square | 深绿 `#2d7d46` | SQR |
| Rectangle | 深绿 `#2d7d46` | REC |
| Circle | 深紫 `#7d2d6e` | CIR |
| Arc | 深紫 `#7d2d6e` | Arc |
| Text | 深蓝 `#2d5a7d` | Text |
| Tex | 深蓝 `#2d5a7d` | Tex |
| MathTex | 深蓝 `#2d5a7d` | MTX |
| Paragraph | 深蓝 `#2d5a7d` | PGR |
| Line | 暗黄 `#6e6e2d` | Line |
| Arrow | 暗黄 `#6e6e2d` | ARR |
| VGroup / Group | 灰色 `#5a5a5a` | GRP |
| Dot / Cross / Star | 暗红 `#7d2d2d` | Dot / CRO / Star |
| Polygon / Triangle | 青色 `#2d7d6e` | POL / TRI |
| RegularPolygon | 青色 `#2d7d6e` | RPOL |
| ImageMobject | 棕色 `#7d6e2d` | IMG |
| 其他 | 默认灰 `#4a4a5a` | 类名缩写（大写字母） |

新放置对象：绿色虚线边框 + 白色菱形标记 + 标签 `N`。

## TextGrid 组件

可配置的文本网格，支持逐格着色、行列批量着色、文字自适应。

```python
from mobjects import TextGrid

grid = TextGrid(3, 4, cell_size=0.8, texts=[
    ["1", "2", "3", "4"],
    ["5", "6", "7", "8"],
    ["9", "10", "11", "12"],
])

# 稀疏填充
grid = TextGrid(3, 4, texts={(0, 0): "A", (2, 3): "Z"})

# 背景色
grid.set_cell_color(0, 0, RED)
grid.set_row_color(1, BLUE)
grid.set_col_color(2, GREEN)
grid.set_cells_color([(0,0), (1,1)], YELLOW)

# 文字色
grid.set_text_color(0, 0, WHITE)
grid.set_row_text_color(1, YELLOW)
grid.set_col_text_color(2, ORANGE)

# 透明度和线宽
grid.set_fill_opacity(0.5)
grid.set_cell_fill_opacity(1, 2, 0.8)
grid.set_stroke_width(3)
grid.set_cell_stroke_width(0, 0, 0.5)

# 访问子对象
cell = grid.get_cell(1, 2)
label = grid.get_label(1, 2)
```

构造参数 `fill_opacity`（默认 1.0）和 `stroke_width`（默认 1.0）控制默认透明度和线宽。
