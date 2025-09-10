.. SPDX-FileCopyrightText: 2025 The Linux Foundation
..
.. SPDX-License-Identifier: EPL-1.0

*********
openstack
*********

Requires a `pip install lftools-uv[openstack]` to activate this command.
Requires `qemu-img` binary to upload images

.. program-output:: lftools-uv openstack --help

Commands
========



image
-----

.. program-output:: lftools-uv openstack --os-cloud docs image --help

cleanup
^^^^^^^

The intent of this command is to automatically cleanup old images in the cloud.
The OpenDaylight project has 2 clouds, a Private Cloud and a Public cloud which
needs the `--clouds` option to automatically remove the same images from
more than one cloud simultaneously.

.. program-output:: lftools-uv openstack --os-cloud docs image cleanup --help

list
^^^^

.. program-output:: lftools-uv openstack --os-cloud docs image list --help

object
------

Command for managing objects.

.. program-output:: lftools-uv openstack --os-cloud docs object --help

list-containers
^^^^^^^^^^^^^^^

.. program-output:: lftools-uv openstack --os-cloud docs object list-containers --help

stack
-----

Command for managing stacks.

.. program-output:: lftools-uv openstack --os-cloud docs stack --help

create
^^^^^^

Create a new stack.

.. program-output:: lftools-uv openstack --os-cloud docs stack create --help

The create command requires a parameters file in the following format to
build out the stack:

.. code-block: yaml
   :caption: parameter_file

   parameters:
     job_name: JOB_NAME
     silo: SILO
     vm_0_count: 1
     vm_0_flavor: odl-highcpu-4
     vm_0_image: ZZCI - CentOS 7 - builder - 20180802-220823.782
     vm_1_count: 1
     vm_1_flavor: odl-standard-4
     vm_1_image: ZZCI - CentOS 7 - devstack-pike - 20171208-1649


delete
^^^^^^

Delete existing stack.

.. program-output:: lftools-uv openstack --os-cloud docs stack delete --help


cost
^^^^

Get total cost of existing stack.

.. program-output:: lftools-uv openstack --os-cloud docs stack cost --help

Return sum of costs for each member of the running stack.
