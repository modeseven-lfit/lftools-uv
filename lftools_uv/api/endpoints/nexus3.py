# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2019 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################

"""Nexus3 REST API interface."""

__author__ = "DW Talton"

import json
import logging

import lftools_uv.api.client as client
from lftools_uv import config, helpers

log = logging.getLogger(__name__)


class Nexus3(client.RestApi):
    """API endpoint wrapper for Nexus3."""

    def __init__(self, **params):
        """Initialize the class."""
        self.params = params
        self.fqdn = self.params["fqdn"]
        if "creds" not in self.params:
            creds = {
                "authtype": "basic",
                "username": config.get_setting(self.fqdn, "username"),
                "password": config.get_setting(self.fqdn, "password"),
                "endpoint": config.get_setting(self.fqdn, "endpoint"),
            }
            params["creds"] = creds

        super().__init__(**params)

    def create_role(self, name, description, privileges, roles):
        """Create a new role.

        :param name: the role name
        :param description: the role description
        :param privileges: privileges assigned to this role
        :param roles: other roles attached to this role
        """
        list_of_privileges = privileges.split(",")
        list_of_roles = roles.split(",")

        data = {
            "id": name,
            "name": name,
            "description": description,
            "privileges": list_of_privileges,
            "roles": list_of_roles,
        }

        json_data = json.dumps(data, indent=4)
        response = self.post("service/rest/beta/security/roles", data=json_data)

        if isinstance(response, tuple):
            if response[0].status_code == 200:
                return f"Role {name} created"
            else:
                return "Failed to create role"
        else:
            response.raise_for_status()
            return "Failed to create role"

    def create_script(self, name, content):
        """Create a new script.

        :param name: script name
        :param content: content of the script (groovy code)
        """
        data = {"name": name, "content": content, "type": "groovy"}

        json_data = json.dumps(data)
        response = self.post("service/rest/v1/script", data=json_data)

        if isinstance(response, tuple):
            if response[0].status_code == 204:
                return f"Script {name} successfully added."
            else:
                return f"Failed to create script {name}"
        else:
            if response.status_code == 204:
                return f"Script {name} successfully added."
            else:
                response.raise_for_status()
                return f"Failed to create script {name}"

    def create_tag(self, name, attributes):
        """Create a new tag.

        :param name: the tag name
        :param attributes: the tag's attributes
        """
        data = {
            "name": name,
        }

        if attributes is not None:
            data["attributes"] = attributes

        json_data = json.dumps(data)
        response = self.post("service/rest/v1/tags", data=json_data)

        if isinstance(response, tuple):
            if response[0].status_code == 200:
                return f"Tag {name} successfully added."
            else:
                return f"Failed to create tag {name}"
        else:
            if response.status_code == 200:
                return f"Tag {name} successfully added."
            else:
                response.raise_for_status()
                return f"Failed to create tag {name}"

    def create_user(self, username, first_name, last_name, email_address, roles, password=None):
        """Create a new user.

        @param username:
        @param first_name:
        @param last_name:
        @param email:
        @param status:
        @param roles:
        @param password:
        """
        list_of_roles = roles.split(",")
        data = {
            "userId": username,
            "firstName": first_name,
            "lastName": last_name,
            "emailAddress": email_address,
            "status": "active",
            "roles": list_of_roles,
        }

        if password:
            data["password"] = password
        else:
            data["password"] = helpers.generate_password()

        json_data = json.dumps(data)
        response = self.post("service/rest/beta/security/users", data=json_data)

        if isinstance(response, tuple):
            if response[0].status_code == 200:
                return "User {} successfully created with password {}".format(username, data["password"])
            else:
                log.error(f"Failed to create user {username}")
        else:
            if response.status_code == 200:
                return "User {} successfully created with password {}".format(username, data["password"])
            else:
                response.raise_for_status()
                log.error(f"Failed to create user {username}")

    def delete_script(self, name):
        """Delete a script from the server.

        :param name: the script name
        """
        response = self.delete(f"service/rest/v1/script/{name}")

        if isinstance(response, tuple):
            if response[0].status_code == 204:
                return f"Successfully deleted {name}"
            else:
                return f"Failed to delete script {name}"
        else:
            if response.status_code == 204:
                return f"Successfully deleted {name}"
            else:
                response.raise_for_status()
                return f"Failed to delete script {name}"

    def delete_tag(self, name):
        """Delete a tag from the server.

        :param name: the tag's name
        """
        response = self.delete(f"service/rest/v1/tags/{name}")

        if isinstance(response, tuple):
            if response[0].status_code == 204:
                return f"Tag {name} successfully deleted."
            else:
                return f"Failed to delete tag {name}."
        else:
            if response.status_code == 204:
                return f"Tag {name} successfully deleted."
            else:
                response.raise_for_status()
                return f"Failed to delete tag {name}."

    def delete_user(self, username):
        """Delete a user.

        @param username:
        """
        response = self.delete(f"service/rest/beta/security/users/{username}")

        if isinstance(response, tuple):
            if response[0].status_code == 204:
                return f"Successfully deleted user {username}"
            else:
                return f"Failed to delete user {username} with error: {response[1]}"
        else:
            if response.status_code == 204:
                return f"Successfully deleted user {username}"
            else:
                response.raise_for_status()
                return f"Failed to delete user {username}"

    def list_assets(self, repository, **kwargs):
        """List the assets of a given repo.

        :param repository: repo name
        """
        response = self.get(f"service/rest/v1/assets?repository={repository}")
        if isinstance(response, tuple):
            result = response[1]["items"]
            if not result:
                return "This repository has no assets"
            else:
                item_list = []
                for item in result:
                    item_list.append(item["path"])
                return item_list
        else:
            response.raise_for_status()
            return "This repository has no assets"

    def list_blobstores(self, **kwargs):
        """List server blobstores."""
        response = self.get("service/rest/beta/blobstores")
        if isinstance(response, tuple):
            result = response[1]
            list_of_blobstores = []
            for blob in result:
                list_of_blobstores.append(blob["name"])
            return list_of_blobstores
        else:
            response.raise_for_status()
            return []

    def list_components(self, repository, **kwargs):
        """List components from a repo.

        :param repository: the repo name
        """
        response = self.get(f"service/rest/v1/components?repository={repository}")
        if isinstance(response, tuple):
            result = response[1]["items"]
            if not result:
                return "This repository has no components"
            else:
                return result
        else:
            response.raise_for_status()
            return "This repository has no components"

    def list_privileges(self, **kwargs):
        """List server-configured privileges."""
        response = self.get("service/rest/beta/security/privileges")
        if isinstance(response, tuple):
            result = response[1]
            list_of_privileges = []
            for privilege in result:
                list_of_privileges.append(
                    [
                        privilege["type"],
                        privilege["name"],
                        privilege["description"],
                        privilege["readOnly"],
                    ]
                )
            return list_of_privileges
        else:
            response.raise_for_status()
            return []

    def list_repositories(self, **kwargs):
        """List server repositories."""
        response = self.get("service/rest/v1/repositories")
        if isinstance(response, tuple):
            result = response[1]
            list_of_repositories = []
            for repository in result:
                list_of_repositories.append(repository["name"])
            return list_of_repositories
        else:
            response.raise_for_status()
            return []

    def list_roles(self, **kwargs):
        """List server roles."""
        response = self.get("service/rest/beta/security/roles")
        if isinstance(response, tuple):
            result = response[1]
            list_of_roles = []
            for role in result:
                list_of_roles.append([role["name"]])
            return list_of_roles
        else:
            response.raise_for_status()
            return []

    def list_scripts(self, **kwargs):
        """List server scripts."""
        response = self.get("service/rest/v1/script")
        if isinstance(response, tuple):
            result = response[1]
            list_of_scripts = []
            for script in result:
                list_of_scripts.append(script["name"])
            return list_of_scripts
        else:
            response.raise_for_status()
            return []

    def show_tag(self, name):
        """Get tag details.

        :param name: tag name
        :return:
        """
        response = self.get(f"service/rest/v1/tags/{name}")
        if isinstance(response, tuple):
            return response[1]
        else:
            response.raise_for_status()
            return {}

    def list_tags(self):
        """List all tag."""
        response = self.get("service/rest/v1/tags")
        if isinstance(response, tuple):
            result = response[1]
            list_of_tags = []
            token = result["continuationToken"]
            if token is not None:
                while token is not None:
                    for tag in result["items"]:
                        list_of_tags.append(tag["name"])
                    next_response = self.get(
                        "service/rest/v1/tags?continuationToken={}".format(result["continuationToken"])
                    )
                    if isinstance(next_response, tuple):
                        result = next_response[1]
                        token = result["continuationToken"]
                    else:
                        break
            else:
                for tag in result["items"]:
                    list_of_tags.append(tag["name"])

            if list_of_tags:
                return list_of_tags
            else:
                return "There are no tags"
        else:
            response.raise_for_status()
            return "There are no tags"

    def list_tasks(self, **kwargs):
        """List all tasks."""
        response = self.get("service/rest/v1/tasks")
        if isinstance(response, tuple):
            result = response[1]["items"]
            list_of_tasks = []
            for task in result:
                list_of_tasks.append(
                    [
                        task["name"],
                        task["message"],
                        task["currentState"],
                        task["lastRunResult"],
                    ]
                )
            return list_of_tasks
        else:
            response.raise_for_status()
            return []

    def list_user(self, username, **kwargs):
        """Show user details.

        :param username: the user's username
        """
        response = self.get(f"service/rest/beta/security/users?userId={username}")
        if isinstance(response, tuple):
            result = response[1]
            user_info = []
            for user in result:
                user_info.append(
                    [
                        user["userId"],
                        user["firstName"],
                        user["lastName"],
                        user["emailAddress"],
                        user["status"],
                        user["roles"],
                    ]
                )
            return user_info
        else:
            response.raise_for_status()
            return []

    def list_users(self, **kwargs):
        """List all users."""
        response = self.get("service/rest/beta/security/users")
        if isinstance(response, tuple):
            result = response[1]
            list_of_users = []
            for user in result:
                list_of_users.append(
                    [
                        user["userId"],
                        user["firstName"],
                        user["lastName"],
                        user["emailAddress"],
                        user["status"],
                        user["roles"],
                    ]
                )
            return list_of_users
        else:
            response.raise_for_status()
            return []

    def staging_promotion(self, destination_repo, tag):
        """Promote repo assets to a new location.

        :param destination_repo: the repo to promote into
        :param tag: the tag used to identify the assets
        """
        data = {"tag": tag}
        json_data = json.dumps(data)
        response = self.post(f"service/rest/v1/staging/move/{destination_repo}", data=json_data)
        return response

    def read_script(self, name):
        """Get the contents of a script.

        :param name: the script name
        """
        response = self.get(f"service/rest/v1/script/{name}")

        if isinstance(response, tuple):
            if response[0].status_code == 200:
                return response[1]
            else:
                return f"Failed to read script {name}"
        else:
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
                return f"Failed to read script {name}"

    def run_script(self, name):
        """Run a script on the server.

        :param name: the script name
        """
        response = self.post(f"service/rest/v1/script/{name}/run")

        if isinstance(response, tuple):
            if response[0].status_code == 200:
                return response[1]
            else:
                return f"Failed to execute script {name}"
        else:
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()
                return f"Failed to execute script {name}"

    def search_asset(self, query, repository, details=False):
        """Search for an asset.

        :param query: querystring to use, eg myjar-1 to find myjar-1.2.3.jar
        :param repository: the repo to search in
        :param details: returns a fully-detailed json dump
        """
        data = {
            "q": query,
            "repository": repository,
        }
        json_data = json.dumps(data)
        response = self.get(
            f"service/rest/v1/search/assets?q={query}&repository={repository}",
            data=json_data,
        )

        if isinstance(response, tuple):
            result = response[1]["items"]
            list_of_assets = []

            if details:
                return json.dumps(result, indent=4)

            for item in result:
                list_of_assets.append(item["path"])

            return list_of_assets
        else:
            response.raise_for_status()
            return []

    def update_script(self, name, content):
        """Update an existing script on the server.

        :param name: script name
        :param content: new content for the script (groovy code)
        """
        data = {"name": name, "content": content, "type": "groovy"}

        json_data = json.dumps(data)

        response = self.put(f"service/rest/v1/script/{name}", data=json_data)

        if isinstance(response, tuple):
            if response[0].status_code == 204:
                return f"Successfully updated {name}"
            else:
                return f"Failed to update script {name}"
        else:
            if response.status_code == 204:
                return f"Successfully updated {name}"
            else:
                response.raise_for_status()
                return f"Failed to update script {name}"
