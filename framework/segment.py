from framework.strategies import RowLayout


class SceneSegment:
    """所有独立小场景片段的基类"""

    layout = RowLayout
    transition = None

    def __init__(self):
        self.scene = None
        self.im = None
        self.ctx = None
        self.pipeline = None

    def play(self):
        """子类必须实现此方法，编写自己的动画逻辑"""
        raise NotImplementedError
