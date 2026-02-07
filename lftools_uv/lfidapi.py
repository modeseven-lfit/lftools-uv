# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Use the LFIDAPI to add, remove and list members as well as create groups."""

import logging
import sys
import urllib

import requests
import yaml
from email_validator import validate_email

from lftools_uv.github_helper import helper_list, helper_user_github
from lftools_uv.oauth2_helper import oauth_helper

log = logging.getLogger(__name__)

PARSE = urllib.parse.urljoin


def check_response_code(response):
    """Response Code Helper function."""
    if response.status_code != 200:
        raise requests.HTTPError(
            f"Authorization failed with the following error:\n{response.status_code}: {response.text}"
        )


def helper_check_group_exists(group):
    """Check group exists."""
    access_token, url = oauth_helper()
    url = PARSE(url, group)
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(url, headers=headers)
    status_code = response.status_code
    return status_code


def helper_search_members(group):
    """List members of a group."""
    response_code = helper_check_group_exists(group)
    if response_code != 200:
        log.error(f"Code: {response_code} Group {group} does not exists exiting...")
        sys.exit(1)
    else:
        access_token, url = oauth_helper()
        url = PARSE(url, group)
        headers = {"Authorization": "Bearer " + access_token}
        response = requests.get(url, headers=headers)
        try:
            check_response_code(response)
        except requests.HTTPError as e:
            log.error(e)
            exit(1)
        result = response.json()
        members = result["members"]
        # Avoid logging PII (member data) - use debug level only for non-sensitive metadata
        log.debug("Retrieved %d members from group", len(members))
        return members


def helper_user(user, group, delete):
    """Add and remove users from groups."""
    access_token, url = oauth_helper()
    url = PARSE(url, group)
    headers = {"Authorization": "Bearer " + access_token}
    data = {"username": user}
    if delete:
        # Use print() for user-facing output to avoid logging PII
        print(f"Deleting user from {group}")  # noqa: T201
        response = requests.delete(url, json=data, headers=headers)
    else:
        # Use print() for user-facing output to avoid logging PII
        print(f"Adding user to {group}")  # noqa: T201
        response = requests.put(url, json=data, headers=headers)
    try:
        check_response_code(response)
    except requests.HTTPError as e:
        log.error(e)
        exit(1)
    # Avoid logging PII - only log operation success
    log.debug("User operation completed successfully")


def helper_invite(email, group):
    """Email invitation to join group."""
    access_token, url = oauth_helper()
    prejoin = group + "/invite"
    url = PARSE(url, prejoin)
    headers = {"Authorization": "Bearer " + access_token}
    data = {"mail": email}
    # Use print() for user-facing output to avoid logging PII (email)
    print("Validating email address")  # noqa: T201
    if validate_email(email):
        print(f"Inviting user to join {group}")  # noqa: T201
        response = requests.post(url, json=data, headers=headers)
        try:
            check_response_code(response)
        except requests.HTTPError as e:
            log.error(e)
            exit(1)
        # Avoid logging PII - only log operation success
        log.debug("Invite operation completed successfully")
    else:
        # Avoid logging PII (email) in error messages
        log.error(f"Email address is not valid, not inviting to {group}")


def helper_create_group(group):
    """Create group."""
    response_code = helper_check_group_exists(group)
    if response_code == 200:
        log.error(f"Group {group} already exists. Exiting...")
    else:
        access_token, url = oauth_helper()
        url = f"{url}/"
        headers = {"Authorization": "Bearer " + access_token}
        data = {"title": group, "type": "group"}
        log.debug("Creating group with type: group")
        print(f"Creating group {group}")  # noqa: T201
        response = requests.post(url, json=data, headers=headers)
        try:
            check_response_code(response)
        except requests.HTTPError as e:
            log.error(e)
            exit(1)
        # Avoid logging potentially sensitive response data
        log.debug("Group creation completed successfully")


def helper_match_ldap_to_info(info_file, group, githuborg, noop):
    """Helper matches ldap or github group to users in an info file.

    Used in automation.
    """
    with open(info_file) as file:
        try:
            info_data = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)
    id = "id"
    if githuborg:
        id = "github_id"
        ldap_data = helper_list(
            ctx=False,
            organization=githuborg,
            repos=False,
            audit=False,
            full=False,
            teams=False,
            repofeatures=False,
            team=group,
        )
    else:
        ldap_data = helper_search_members(group)

    committer_info = info_data["committers"]

    info_committers = []
    for count, _item in enumerate(committer_info):
        committer = committer_info[count][id]
        info_committers.append(committer)

    ldap_committers = []
    if githuborg:
        for x in ldap_data:
            committer = x
            ldap_committers.append(committer)

    else:
        for count, _item in enumerate(ldap_data):
            committer = ldap_data[count]["username"]
            ldap_committers.append(committer)

    all_users = ldap_committers + info_committers

    if not githuborg:
        if "lfservices_releng" in all_users:
            all_users.remove("lfservices_releng")

    # Use print() for user-facing output to avoid logging PII (usernames)
    print("All users in org group:")  # noqa: T201
    all_users = sorted(set(all_users))
    for x in all_users:
        print(f"  {x}")  # noqa: T201

    for user in all_users:
        removed_by_patch = [item for item in ldap_committers if item not in info_committers]
        if user in removed_by_patch:
            # Use print() for user-facing output to avoid logging PII
            print(f"User found in group {group}, scheduled for removal")  # noqa: T201
            if noop is False:
                print(f"Removing user from group {group}")  # noqa: T201
                if githuborg:
                    helper_user_github(
                        ctx=False, organization=githuborg, user=user, team=group, delete=True, admin=False
                    )
                else:
                    helper_user(user, group, "--delete")

        added_by_patch = [item for item in info_committers if item not in ldap_committers]
        if user in added_by_patch:
            # Use print() for user-facing output to avoid logging PII
            print(f"User not found in group {group}, scheduled for addition")  # noqa: T201
            if noop is False:
                print(f"Adding user to group {group}")  # noqa: T201
                if githuborg:
                    helper_user_github(
                        ctx=False, organization=githuborg, user=user, team=group, delete=False, admin=False
                    )

                else:
                    helper_user(user, group, "")
