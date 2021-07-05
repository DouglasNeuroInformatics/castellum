.. _2fa:

Two-Factor-Authentication
=========================

To further protect subjects' personal data against compromised or weak
passwords, Castellum can *and should* be used with two-factor authentication
(2FA).

If enabled, a successful login requires an additional code or passphrase before
Castellum can be used (similar to a TAN for online banking).

Currently we support any generic TOTP application or FIDO2 hardware security
tokens.

Smartphone apps (TOTP)
----------------------

We recommend to use a 2FA application on your phone. Just search for "TOTP" in
the app store of your choice.

Most TOTP apps work the same:

1.  Install an authenticator app on a phone
2.  Register that phone on the website (Castellum) by scanning a QR code with
    the authenticator app
3.  The app will now generate TOTP authentication codes for you that can be
    used to log in

Hardware Keys (FIDO2)
---------------------

If you do not want to use your phone and TOTP, you can also chose to use
FIDO2-based hardware keys (tokens). In that case we recommend `Yubico FIDO2
tokens <https://www.yubico.com/de/product/security-key-nfc-by-yubico/>`_, but
any FIDO2-compatible token should work.

The tokens are connected to your device with USB and, when registered
successfully, usually just require a tap / key press when prompted on login.

For additional details about supported hardware tokens or Authenticator apps,
contact your local IT department or security officer.
