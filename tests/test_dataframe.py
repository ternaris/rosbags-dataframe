# Copyright 2020 - 2024 Ternaris
# SPDX-License-Identifier: Apache-2.0
"""Rosbags dataframe tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd  # type: ignore[import-untyped]
import pytest

from rosbags.dataframe import DataframeError, get_dataframe
from rosbags.highlevel import AnyReader
from rosbags.rosbag1 import Writer
from rosbags.typesys import Stores, get_typestore
from rosbags.typesys.stores.latest import (
    builtin_interfaces__msg__Time as Time,
    sensor_msgs__msg__NavSatFix as NavSatFix,
    sensor_msgs__msg__NavSatStatus as NavSatStatus,
    std_msgs__msg__Header as Header,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_get_dataframe(tmp_path: Path) -> None:
    """Test get_dataframe function."""
    store = get_typestore(Stores.LATEST)

    path = tmp_path / 'test.bag'
    with Writer(path) as writer:
        gps = writer.add_connection('/gps', NavSatFix.__msgtype__, typestore=store)

        msg = NavSatFix(
            header=Header(stamp=Time(sec=0, nanosec=0), frame_id='/base'),
            status=NavSatStatus(status=0, service=1),
            latitude=43.8476,
            longitude=18.3564,
            altitude=0,
            position_covariance=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.float64),
            position_covariance_type=0,
        )

        writer.write(gps, 42, store.serialize_ros1(msg, NavSatFix.__msgtype__))

        msg.latitude = 48.1255
        msg.longitude = 11.5428

        writer.write(gps, 666, store.serialize_ros1(msg, NavSatFix.__msgtype__))

    with pytest.raises(DataframeError, match='opened before'):
        get_dataframe(AnyReader([path]), '/gps', ['status.status', 'latitude', 'longitude'])

    with AnyReader([path]) as reader, pytest.raises(DataframeError, match='unknown topic'):
        get_dataframe(reader, '/badtopic', ['status.status', 'latitude', 'longitude'])

    with AnyReader([path]) as reader, pytest.raises(DataframeError, match='not exist'):
        get_dataframe(reader, '/gps', ['badfield'])

    with AnyReader([path]) as reader, pytest.raises(DataframeError, match='does not exist on'):
        get_dataframe(reader, '/gps', ['badfield.stamp'])

    with AnyReader([path]) as reader, pytest.raises(DataframeError, match='is not a message'):
        get_dataframe(reader, '/gps', ['latitude.badfield'])

    reference = pd.DataFrame(
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
        index=pd.to_datetime([42, 666]),
    )
    with AnyReader([path]) as reader:
        dataframe = get_dataframe(reader, '/gps', ['status.status', 'latitude', 'longitude'])
        assert dataframe.equals(reference)
