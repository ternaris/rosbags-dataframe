Dataframe
=========

The :py:mod:`rosbags.dataframe` package provides pandas integration for rosbags.

Read topics into dataframes
---------------------------
The function :py:func:`get_dataframe <rosbags.dataframe.get_dataframe>` reads a topic from an opened ``AnyReader`` and extracts requested keys from each message into a pandas dataframe:

.. code-block:: python

   from pathlib import Path

   from rosbags.dataframe import get_dataframe
   from rosbags.highlevel import AnyReader

   with AnyReader([Path('test1.bag'), Path('test2.bag')]) as reader:
       dataframe = get_dataframe(reader, '/gps', ['latitude', 'longitude'])

The keys are given as a list of strings and support a dotted syntax to extract values from nested messages.

.. code-block:: python

   from pathlib import Path

   from rosbags.dataframe import get_dataframe
   from rosbags.highlevel import AnyReader

   with AnyReader([Path('test1.bag'), Path('test2.bag')]) as reader:
       dataframe = get_dataframe(reader, '/pose', ['position.x', 'position.y'])
