# Copyright 2019-2022  Ternaris.
# SPDX-License-Identifier: Apache-2.0
"""Conversion of rosbag topics to dataframes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas  # type: ignore
from rosbags.serde.messages import get_msgdef
from rosbags.serde.utils import Valtype

if TYPE_CHECKING:
    from typing import Callable, Sequence, Union

    from rosbags.highlevel import AnyReader

    AttrValue = Union[str, bool, int, float, object]


class DataframeError(Exception):
    """Dataframe conversion error."""


def get_dataframe(reader: AnyReader, topicname: str, keys: Sequence[str]) -> pandas.DataFrame:
    """Convert messages from a topic into a pandas dataframe.

    Read all messages from a topic and extract referenced keys into
    a pandas dataframe. The message timestamps are automatically added
    as the dataframe index.

    Keys support a dotted syntax to traverse nested messages.

    Args:
        reader: Opened rosbags reader.
        topicname: Topic name of messages to process.
        keys: Field names to get from each message.

    Raises:
        DataframeError: Reader not opened or topic or field name does not exist.

    Returns:
        Pandas dataframe.

    """
    # pylint: disable=too-many-locals
    if not reader.isopen:
        raise DataframeError('RosbagReader needs to be opened before accessing messages.')

    if topicname not in reader.topics:
        raise DataframeError(f'Requested unknown topic {topicname!r}.')

    topic = reader.topics[topicname]
    assert topic.msgtype

    msgdef = get_msgdef(topic.msgtype, reader.typestore)

    def create_plain_getter(key: str) -> Callable[[object], AttrValue]:
        """Create getter for plain attribute lookups."""

        def getter(msg: object) -> AttrValue:
            return getattr(msg, key)  # type: ignore

        return getter

    def create_nested_getter(keys: list[str]) -> Callable[[object], AttrValue]:
        """Create getter for nested lookups."""

        def getter(msg: object) -> AttrValue:
            value = msg
            for key in keys:
                value = getattr(value, key)
            return value

        return getter

    getters = []
    for key in keys:
        subkeys = key.split('.')
        subdef = msgdef
        for subkey in subkeys[:-1]:
            subfield = next((x for x in subdef.fields if x.name == subkey), None)
            if not subfield:
                raise DataframeError(f'Field {subkey!r} does not exist on {subdef.name!r}.')

            if subfield.descriptor.valtype != Valtype.MESSAGE:
                raise DataframeError(f'Field {subkey!r} of {subdef.name!r} is not a message.')

            subdef = subfield.descriptor.args

        if subkeys[-1] not in {x.name for x in subdef.fields}:
            raise DataframeError(f'Field {subkeys[-1]!r} does not exist on {subdef.name!r}.')

        if len(subkeys) == 1:
            getters.append(create_plain_getter(subkeys[0]))
        else:
            getters.append(create_nested_getter(subkeys))

    timestamps = []
    data = []
    for _, timestamp, rawdata in reader.messages(connections=topic.connections):
        msg = reader.deserialize(rawdata, topic.msgtype)
        timestamps.append(timestamp)
        data.append([x(msg) for x in getters])

    return pandas.DataFrame(data, columns=keys, index=pandas.to_datetime(timestamps))
