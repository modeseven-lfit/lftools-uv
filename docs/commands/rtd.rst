.. SPDX-FileCopyrightText: 2025 The Linux Foundation
..
.. SPDX-License-Identifier: EPL-1.0

***********
ReadTheDocs
***********

.. program-output:: lftools-uv rtd --help

Commands
========

project-list
------------

.. program-output:: lftools-uv rtd project-list --help

project-details
---------------

.. program-output:: lftools-uv rtd project-details --help



project-version-list
--------------------

.. program-output:: lftools-uv rtd project-version-list --help



project-version-details
-----------------------

.. program-output:: lftools-uv rtd project-version-details --help



project-version-update
----------------------

.. program-output:: lftools-uv rtd project-version-update --help



project-create
--------------

.. program-output:: lftools-uv rtd project-create --help



project-build-list
------------------

.. program-output:: lftools-uv rtd project-build-list --help



project-build-details
---------------------

.. program-output:: lftools-uv rtd project-build-details --help



project-build-trigger
---------------------

.. program-output:: lftools-uv rtd project-build-trigger --help




API requires a [rtd] section in ~/.config/lftools/lftools.ini:

.. code-block:: bash

   [rtd]
   token = REDACTED
   endpoint = https://readthedocs.org/api/v3/
