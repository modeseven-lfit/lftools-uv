.. SPDX-FileCopyrightText: 2025 The Linux Foundation
..
.. SPDX-License-Identifier: EPL-1.0

########
Commands
########

lftools-uv is a collection of scripts written directly in python or externally via
bash.

It supports the following commands:

.. toctree::
    :maxdepth: 2

    config
    deploy
    dco
    gerrit
    github
    infofile
    lfidapi
    license
    nexus
    nexus2
    nexus3
    openstack
    rtd
    schema
    sign
    version

Enable debugging via ``lftools-uv --debug`` preceding any commands or via
environment variable ``DEBUG=True``, this will print extra information if
available.
