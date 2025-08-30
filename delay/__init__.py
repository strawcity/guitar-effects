"""
Guitar Delay Effects Package

This package contains the stereo delay effect implementation for the guitar effects project.
"""

from .base_delay import BaseDelay
from .stereo_delay import StereoDelay
from .distortion import DistortionEffect, CrossFeedbackDistortion, DistortionType

__all__ = [
    'BaseDelay',
    'StereoDelay',
    'DistortionEffect',
    'CrossFeedbackDistortion',
    'DistortionType'
]
