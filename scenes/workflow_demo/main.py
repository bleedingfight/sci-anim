import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from framework import Pipeline
from manim import Scene

from intro import IntroSegment
from interaction import InteractionSegment
from end import EndSegment


class WorkflowDemo(Scene):
    def construct(self):
        Pipeline(self) \
            .add(IntroSegment()) \
            .add(InteractionSegment()) \
            .add(EndSegment()) \
            .run()
