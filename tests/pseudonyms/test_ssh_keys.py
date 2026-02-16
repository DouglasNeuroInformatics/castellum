# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from castellum.pseudonyms.ssh_keys import generate_ssh_keypair


def test_generate_ed25519_keypair():
    """Test Ed25519 key generation produces valid OpenSSH format keys."""
    public_key, private_key = generate_ssh_keypair()

    assert public_key.startswith('ssh-ed25519 ')
    assert '-----BEGIN OPENSSH PRIVATE KEY-----' in private_key
    assert '-----END OPENSSH PRIVATE KEY-----' in private_key


def test_generate_unique_keypairs():
    """Test that each call generates a unique key pair."""
    pub1, priv1 = generate_ssh_keypair()
    pub2, priv2 = generate_ssh_keypair()

    assert pub1 != pub2
    assert priv1 != priv2
