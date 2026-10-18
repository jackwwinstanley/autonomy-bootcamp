"""SimCamera: YOUR Part 2 assignment.

A camera that makes up its own frames. Read ``src/fixed.py`` and its tests
first, then make ``tests/test_sim_camera.py`` pass:

    warg run camera test

``SimCamera(width=64, height=48)`` hands back a ``(height, width, 3)``
``uint8`` frame every time you ask, for as long as it's on, with ``index``
counting up from 0. Same rules as every camera
(``src/abstract_camera.py``), plus one:

A frame's pixels depend only on its index. Frame 2 always looks the same,
here or in any SimCamera built with the same size, and frames with different
indexes look different. Fill values, gradients, and
``numpy.random.default_rng(index)`` all work.
"""

import time

import numpy

from .abstract_camera import AbstractCamera
from .frame import CameraFrame


class SimCamera(AbstractCamera):
    """Fake camera that makes up its own frames.

    The docstring at the top of this file says what it has to do, and
    ``tests/test_sim_camera.py`` checks all of it.
    """

    def __init__(self, width: int = 64, height: int = 48) -> None:
        """Save the settings and set up whatever state you need.

        Args:
            width: Frame width in pixels.
            height: Frame height in pixels.
        """
        # TODO(bootcamper): save the arguments and set up your state
        # (FixedCamera.__init__ shows you what that looks like).
        if not width or not height:
            raise ValueError("width and/or height must not be empty")

        self.frame_width = width
        self.frame_height = height
        self.camera_on = False
        self.captures = 0
        self.index = 0
        self.last_timestamp = float("-inf")



    def initialize_camera(self) -> bool:
        """Turn the fake camera on and start counting from index 0."""
        # TODO(bootcamper): implement.
        self.camera_on = True
        self.captures = 0
        return True


    def capture_frame(self) -> CameraFrame:
        if not self.camera_on:
            raise RuntimeError(
                "capture_frame() called on a camera that is not initialized; "
                "call initialize_camera() first"
            )
        rgb = numpy.random.default_rng(self.captures).integers(
            0,
            256,
            size=(self.frame_height, self.frame_width, 3),
            dtype=numpy.uint8,
        )

        frame = CameraFrame(
        rgb = rgb.copy(),
        timestamp = self._next_timestamp(),
        index= self.captures,
        )
        self.captures += 1
        return frame
        

    def stop(self) -> None:
        """Turn the fake camera off. Safe to call more than once."""
        self.camera_on = False


    def _next_timestamp(self) -> float:
        timestamp = time.monotonic()
        if timestamp <= self.last_timestamp:
            timestamp = self.last_timestamp + 1e-6
        self.last_timestamp = timestamp
        return timestamp
