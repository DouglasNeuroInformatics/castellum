.. _2fa:

Two factor authentication
=========================

To further protect subjects' personal data against compromised or weak
passwords, Castellum can *and should* be used with two-factor authentication
(2FA).

If enabled, you need to enter an additional code before you can log in to
Castellum (similar to a TAN for online banking).

Currently we support any generic TOTP application or FIDO2 hardware security
tokens.

Smartphone apps (TOTP)
----------------------

We recommend to use a 2FA application on your phone. Just ask your local IT on
suggestions for appropriate apps to be used at your institution.

.. admonition:: Example

    By the time of writing (June 2021) the MPI for Human Development recommends
    its Castellum users to install `Google Authenticator
    <https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2>`_
    for Android or `Microsoft Authenticator
    <https://apps.apple.com/de/app/microsoft-authenticator/id983156458>`_ on iOS.

TOTP stands for “Time-based One-Time Password”. As the name suggests, each TOTP
code can only be used once.

Most TOTP apps work the same:

1.  Install an authenticator app on a phone

2.  Register that phone on Castellum with the authenticator app,
    by scanning a QR Code.

    .. figure:: /_images/google_auth.jpg
        :alt: Example from Google Authenticator
        :figclass: screenshot

        Example from **Google Authenticator**

3.  The app will now generate a new **6-digit numeric code** every 30 seconds

    Whenever you want to log in to Castellum, you will need to input
    this numeric code, along with your private password.

4.  The code depends on the current time, so make sure that the phone has the
    correct time set


Hardware Keys (FIDO2)
---------------------

You can also chose to use FIDO2-based hardware keys (tokens). In that case we
recommend `Yubico FIDO2 tokens
<https://www.yubico.com/de/product/security-key-nfc-by-yubico/>`_, but any
FIDO2-compatible token should work.

The tokens are connected to your device with USB and, when registered
successfully, usually just require a tap / key press when prompted on login.

To register your **FIDO2 hardware key**:

1.  Insert your hardware key in any USB port.
2.  When prompted by Castellum, click "Register security key".
3.  When prompted by Castellum, press your hardware key to complete its
    registration.


Blocking lost or stolen devices
-------------------------------

If your phone or hardware key has been lost or stolen, you should remove that
key from Castellum so it can no longer be used to log in. You can either do
that yourself by using another key that you have registered (e.g. a recovery
code), or by contacing your local IT department.
