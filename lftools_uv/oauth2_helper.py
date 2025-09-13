# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2019, 2023 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
"""Helper script to get access_token for lfid api."""

from __future__ import annotations

import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from lftools_uv import config


def oauth_helper() -> tuple[str, str]:
    """Helper script to get access_token for lfid api using google-auth refresh token flow."""
    logging.getLogger("google.auth").setLevel(logging.ERROR)
    client_id = str(config.get_setting("lfid", "clientid"))
    client_secret = str(config.get_setting("lfid", "client_secret"))
    refresh_token = str(config.get_setting("lfid", "refresh_token"))
    token_uri = str(config.get_setting("lfid", "token_uri"))
    url = str(config.get_setting("lfid", "url"))

    credentials = Credentials(
        token=None,  # Access token will be populated by refresh()
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=None,  # Existing refresh token already encodes scopes
    )
    # Perform the refresh to obtain a new access token
    credentials.refresh(Request())
    access_token = credentials.token
    return access_token, url
