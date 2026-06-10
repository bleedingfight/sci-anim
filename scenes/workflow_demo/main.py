import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from framework import Pipeline
from segments import IntroSegment, OutroSegment
from manim import Scene

from interaction import InteractionSegment


class WorkflowDemo(Scene):
    def construct(self):
        Pipeline(self) \
            .add(IntroSegment("分镜编排演示", subtitle="Pipeline + SceneSegment")) \
            .add(InteractionSegment()) \
            .add(OutroSegment()) \
            .run()
