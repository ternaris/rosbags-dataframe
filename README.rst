.. image:: https://gitlab.com/ternaris/rosbags-dataframe/badges/master/pipeline.svg
   :target: https://gitlab.com/ternaris/rosbags-dataframe/-/commits/master
   :alt: pipeline status

.. image:: https://gitlab.com/ternaris/rosbags-dataframe/badges/master/coverage.svg
   :target: https://gitlab.com/ternaris/rosbags-dataframe/-/commits/master
   :alt: coverage report


=================
Rosbags-dataframe
=================

Rosbags-dataframe a python library to ease the create of pandas dataframes from rosbag messages. It is part of the larger `Rosbags <https://gitlab.com/ternaris/rosbags>`_ ecosystem.

Rosbags-dataframe does not have any dependencies on the ROS software stacks and can be used on its own or alongside ROS1 or ROS2.


Getting started
===============

Rosbags-dataframe is published on PyPI and does not have any special dependencies. Simply install with pip::

   pip install rosbags-dataframe


Get a dataframe from a rosbag:

.. code-block:: python

   from pathlib import Path

   from rosbags.dataframe import get_dataframe
   from rosbags.highlevel import AnyReader

   with AnyReader([Path('test1.bag'), Path('test2.bag')]) as reader:
       dataframe = get_dataframe(reader, '/gps', ['latitude', 'longitude'])


Documentation
=============

Read the `documentation <https://ternaris.gitlab.io/rosbags-dataframe/>`_ for further information.

.. end documentation


Contributing
============

Thank you for considering to contribute to rosbags-dataframe.

To submit issues or create merge requests please follow the instructions provided in the `contribution guide <https://gitlab.com/ternaris/rosbags-dataframe/-/blob/master/CONTRIBUTING.rst>`_.

By contributing to rosbags-dataframe you accept and agree to the terms and conditions laid out in there.


Development
===========

Clone the repository and setup your local checkout::

   git clone https://gitlab.com/ternaris/rosbags-dataframe.git

   cd rosbags-dataframe
   python -m venv venv
   . venv/bin/activate

   pip install -r requirements-dev.txt
   pip install -e .


This creates a new virtual environment with the necessary python dependencies and installs rosbags-dataframe in editable mode. The rosbags-dataframe code base uses pytest as its test runner, run the test suite by simply invoking::

   pytest


To build the documentation from its source run sphinx-build::

   sphinx-build -a docs public


The entry point to the local documentation build should be available under ``public/index.html``.


Support
=======

Professional support is available from `Ternaris <https://ternaris.com>`_.
