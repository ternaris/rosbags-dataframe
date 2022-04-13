# Copyright 2020  Ternaris.
# SPDX-License-Identifier: AGPL-3.0-only
"""Rosbags dataframe tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy
import pandas  # type: ignore
import pytest
from rosbags.highlevel import AnyReader
from rosbags.rosbag1 import Writer
from rosbags.serde import cdr_to_ros1, serialize_cdr
from rosbags.typesys.types import builtin_interfaces__msg__Time as Time
from rosbags.typesys.types import sensor_msgs__msg__NavSatFix as NavSatFix
from rosbags.typesys.types import sensor_msgs__msg__NavSatStatus as NavSatStatus
from rosbags.typesys.types import std_msgs__msg__Header as Header

from rosbags.dataframe import DataframeError, get_dataframe

if TYPE_CHECKING:
    from pathlib import Path


def test_get_dataframe(tmp_path: Path) -> None:
    """Test get_dataframe function."""
    path = tmp_path / 'test.bag'
    with Writer(path) as writer:
        gps = writer.add_connection('/gps', NavSatFix.__msgtype__)

        msg = NavSatFix(
            header=Header(stamp=Time(sec=0, nanosec=0), frame_id='/base'),
            status=NavSatStatus(status=0, service=1),
            latitude=43.8476,
            longitude=18.3564,
            altitude=0,
            position_covariance=numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=numpy.float64),
            position_covariance_type=0,
        )

        writer.write(
            gps,
            42,
            cdr_to_ros1(serialize_cdr(msg, NavSatFix.__msgtype__), NavSatFix.__msgtype__),
        )

        msg.latitude = 48.1255
        msg.longitude = 11.5428

        writer.write(
            gps,
            666,
            cdr_to_ros1(serialize_cdr(msg, NavSatFix.__msgtype__), NavSatFix.__msgtype__),
        )

    with pytest.raises(DataframeError, match='opened before'):
        get_dataframe(AnyReader([path]), '/gps', ['status.status', 'latitude', 'longitude'])

    with AnyReader([path]) as reader, \
         pytest.raises(DataframeError, match='unknown topic'):
        get_dataframe(reader, '/badtopic', ['status.status', 'latitude', 'longitude'])

    with AnyReader([path]) as reader, \
         pytest.raises(DataframeError, match='not exist'):
        get_dataframe(reader, '/gps', ['badfield'])

    with AnyReader([path]) as reader, \
         pytest.raises(DataframeError, match='does not exist on'):
        get_dataframe(reader, '/gps', ['badfield.stamp'])

    with AnyReader([path]) as reader, \
         pytest.raises(DataframeError, match='is not a message'):
        get_dataframe(reader, '/gps', ['latitude.badfield'])

    reference = pandas.DataFrame(
        {
            'status.status': [0, 0],
            'latitude': [
                43.8476,
                48.1255,
            ],
            'longitude': [
                18.3564,
                11.5428,
            ],
        },
        index=pandas.to_datetime([42, 666]),
    )
    with AnyReader([path]) as reader:
        dataframe = get_dataframe(reader, '/gps', ['status.status', 'latitude', 'longitude'])
        assert dataframe.equals(reference)
