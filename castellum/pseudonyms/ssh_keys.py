# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


def generate_ssh_keypair():
    """Generate an Ed25519 SSH key pair in OpenSSH format.

    Returns:
        tuple: (public_key_openssh, private_key_pem)
    """
    private_key = ed25519.Ed25519PrivateKey.generate()

    public_key_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return (
        public_key_bytes.decode('utf-8'),
        private_key_bytes.decode('utf-8'),
    )
