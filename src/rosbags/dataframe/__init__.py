# Copyright 2020 - 2024 Ternaris
# SPDX-License-Identifier: Apache-2.0
"""Rosbags dataframe support.

Tools to interact with rosbag data in the form of pandas dataframes.

"""

from .dataframe import DataframeError, get_dataframe

__all__ = [
    'DataframeError',
    'get_dataframe',
]
