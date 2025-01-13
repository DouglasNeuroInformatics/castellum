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
    its Castellum users to install either `Google Authenticator
    <https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2>`_
    or `andOTP <https://f-droid.org/packages/org.shadowice.flocke.andotp/>`_ for
    Android or `Microsoft Authenticator
    <https://apps.apple.com/de/app/microsoft-authenticator/id983156458>`_ on iOS.

TOTP stands for “Time-based One-Time Password”. As the name suggests, each TOTP
code can only be used once.

Most TOTP apps work the same:

1.  Install an authenticator app on a phone

    a.  For **Android** phone users:

        1.  Open `Google Play Store <https://play.google.com/>`_ on your phone.
        2.  Type in the search bar: "Google Authenticator", "andOTP" or any
            other authenticator app you can trust.
        3.  Press the "Install" button.

    b.  For **iOS** phone users:

        1.  Open `App Store <https://www.apple.com/app-store/>`_ on your phone.
        2.  Type in the search bar: "Microsoft Authenticator" or any other
            authenticator app you can trust.
        3.  Press the "Get" button.

    .. NOTE::

        Some apps may require additional setup steps, like setting a password
        for the app, choosing database encryption, enabling Android sync, etc.

2.  Register that phone on Castellum with the authenticator app,
    by scanning a QR Code.

    .. figure:: /_images/google_auth.jpg
        :alt: Example from Google Authenticator
        :figclass: screenshot

        Example from **Google Authenticator**

    By selecting this option you will be asked to allow the app to take
    pictures and record video. Press "Allow" and scan the QR Code.

3.  The app will now generate a new **6-digit numeric code** every 30 seconds

    Whenever you want to log in to Castellum, you will need to input
    this numeric code, along with your private password.

4.  The code depends on the current time, so make sure that the phone has the
    correct time set

.. NOTE::

    If you have acquired a new smartphone device, it is important that you
    keep your old device in use until you set up the new one. Procceed by
    installing an authenticator app on the new device, as described above.
    Then log in to Castellum using your old device's TOTP and register your
    new device.


Hardware Keys (FIDO2)
---------------------

If you do not want to use your phone and TOTP, you can also chose to use
FIDO2-based hardware keys (tokens). In that case we recommend `Yubico FIDO2
tokens <https://www.yubico.com/de/product/security-key-nfc-by-yubico/>`_, but
any FIDO2-compatible token should work.

The tokens are connected to your device with USB and, when registered
successfully, usually just require a tap / key press when prompted on login.

To register your **FIDO2 hardware key**:

1.  Insert your hardware key in any USB port.
2.  When prompted by Castellum, click "Register security key".
3.  When prompted by Castellum, press your hardware key to complete its
    registration.

For additional details about supported hardware tokens or Authenticator apps,
contact your local IT department or security officer.