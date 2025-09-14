# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2020 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################

"""Nexus3 REST API interface."""

from __future__ import annotations

import random
import string


def generate_password(length: int = 12) -> str:
    """Generate a password with guaranteed character variety.

    Ensures the password contains at least one character from each category:
    - Lowercase letters
    - Uppercase letters
    - Digits
    - Punctuation
    """
    if length < 4:
        # For very short passwords, just use random selection
        punctuation: str = "!#$%&()*+,-.:;<=>?@[]^_{|}~"
        password_characters: str = string.ascii_letters + string.digits + punctuation
        return "".join(random.choice(password_characters) for _ in range(length))

    # Character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    punctuation = "!#$%&()*+,-.:;<=>?@[]^_{|}~"

    # Ensure at least one character from each category
    password = [random.choice(lowercase), random.choice(uppercase), random.choice(digits), random.choice(punctuation)]

    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + punctuation
    for _ in range(length - 4):
        password.append(random.choice(all_chars))

    # Shuffle to avoid predictable patterns
    random.shuffle(password)

    return "".join(password)
