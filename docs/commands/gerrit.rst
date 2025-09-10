.. SPDX-FileCopyrightText: 2025 The Linux Foundation
..
.. SPDX-License-Identifier: EPL-1.0

******
Gerrit
******

.. program-output:: lftools-uv gerrit --help

Commands
========

list-project-permissions
------------------------

.. program-output:: lftools-uv gerrit list-project-permissions --help


list-project-inherits-from
--------------------------

.. program-output:: lftools-uv gerrit list-project-inherits-from --help


abandonchanges
--------------

.. program-output:: lftools-uv gerrit abandonchanges --help

addgitreview
------------

.. program-output:: lftools-uv gerrit addgitreview --help


addgithubrights
---------------

.. program-output:: lftools-uv gerrit addgithubrights --help


addfile
-------

.. program-output:: lftools-uv gerrit addfile --help


createproject
-------------

.. program-output:: lftools-uv gerrit createproject --help


create-saml-group
-----------------

.. program-output:: lftools-uv gerrit create-saml-group --help


addinfojob
----------
.. program-output:: lftools-uv gerrit addinfojob --help


.. note::

        Gerrit API methods require configuration in lftools-uv.ini
        in a global [gerrit] section.
        support for [gerrit.umbrella.tld] exists as well
        signed_off_by required to push changes.
        Projects that do not allow self merge will require
        as project.example.org.second section for submission
        of their .gitreview on project creation.


.. code-block:: none

     [gerrit.example.org]
     username = lfid
     password = password
     signed_off_by = Your Name <your@email.org>

     [gerrit.example.org.second]
     username = lfid2
     password = password2
     signed_off_by = Your Name <your@email.org>

addmavenconfig
--------------
.. program-output:: lftools-uv gerrit addmavenconfig --help


An example of the lftools-uv.ini entry for a Gerrit server making use of a full
configuration:

.. code-block:: none

     [gerrit.example.org]
     username = lfid
     password = password
     signed_off_by = Your Name <your@email.org>
     endpoint = https://gerrit.example.org/
     default_servers = releases,snapshots,staging,site
     nexus3 = nexus3.example.org
     nexus3_ports = 10001,10002,10003,10004
     additional_credentials = {"docker.io": "dockerhub-cred", "nexus-iq": "nexus-iq-cred"}
