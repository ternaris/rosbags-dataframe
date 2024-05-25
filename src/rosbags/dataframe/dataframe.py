# Copyright 2020 - 2024 Ternaris
# SPDX-License-Identifier: Apache-2.0
"""Conversion of rosbag topics to dataframes."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pandas as pd

from rosbags.interfaces import Nodetype

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import TypeAlias

    from rosbags.highlevel import AnyReader

    AttrValue: TypeAlias = str | bool | int | float | object


class DataframeError(Exception):
    """Dataframe conversion error."""


def get_dataframe(reader: AnyReader, topicname: str, keys: Sequence[str]) -> pd.DataFrame:
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
        msg = 'RosbagReader needs to be opened before accessing messages.'
        raise DataframeError(msg)

    if topicname not in reader.topics:
        msg = f'Requested unknown topic {topicname!r}.'
        raise DataframeError(msg)

    topic = reader.topics[topicname]
    assert topic.msgtype

    msgdef = reader.typestore.get_msgdef(topic.msgtype)

    def create_plain_getter(key: str) -> Callable[[AttrValue], AttrValue]:
        """Create getter for plain attribute lookups."""

        def getter(msg: AttrValue) -> AttrValue:
            return cast('AttrValue', getattr(msg, key))

        return getter

    def create_nested_getter(keys: list[str]) -> Callable[[AttrValue], AttrValue]:
        """Create getter for nested lookups."""

        def getter(msg: AttrValue) -> AttrValue:
            value = msg
            for key in keys:
                value = cast('AttrValue', getattr(value, key))
            return value

        return getter

    getters: list[Callable[[AttrValue], AttrValue]] = []
    for key in keys:
        subkeys = key.split('.')
        subdef = msgdef
        for subkey in subkeys[:-1]:
            subfield = next((x for x in subdef.fields if x[0] == subkey), None)
            if not subfield:
                msg = f'Field {subkey!r} does not exist on {subdef.name!r}.'
                raise DataframeError(msg)

            if subfield[1][0] != Nodetype.NAME:
                msg = f'Field {subkey!r} of {subdef.name!r} is not a message.'
                raise DataframeError(msg)

            subdef = reader.typestore.get_msgdef(subfield[1][1])

        if subkeys[-1] not in {x[0] for x in subdef.fields}:
            msg = f'Field {subkeys[-1]!r} does not exist on {subdef.name!r}.'
            raise DataframeError(msg)

        if len(subkeys) == 1:
            getters.append(create_plain_getter(subkeys[0]))
        else:
            getters.append(create_nested_getter(subkeys))

    timestamps: list[int] = []
    data: list[list[AttrValue]] = []
    for _, timestamp, rawdata in reader.messages(connections=topic.connections):
        dmsg = reader.deserialize(rawdata, topic.msgtype)
        timestamps.append(timestamp)
        data.append([x(dmsg) for x in getters])

    index = pd.to_datetime(timestamps)  # pyright: ignore[reportUnknownMemberType]
    return pd.DataFrame(data, columns=tuple(keys), index=index)
