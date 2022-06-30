.. _access-calendar-feeds:

========================
List available calendars
========================


To access the calendar feeds overview page add "/feeds/" to the URL of the
castellum start page and confirm.

Find the different types of calendars
=====================================

1.  Under "Per User" find user-specific feeds:

    -   "all follow-ups" lists, in a single calendar, all follow-ups from all studies where you are a member.
    -   "all appointments" shows, in a single calendar, all appointments from all studies where you are a member.

2.  Under "Per Study", find all appointments for each study where you are a member.

3.  Under "Per Resource" find all occupied slots for all resources.

    -   The list of resources is configurable by your institution

    .. TODO::

        - link to resources guide

.. admonition:: Example

    The MPI for Human Development uses a two-step process for booking
    appointments of shared resources:

    1. A *resource committee* allocates time slots fairly across upcoming
       studies (in a dedicated room booking system outside of Castellum).
    2. Study recruiters are allowed to assign appointments within these time
       slots (in Castellum).

    In order to check availability of a resource it is sufficient to subscribe
    to the "Per Resource" feed. However, to check whether it is possible to swap
    open slots with other studies users have to match this feed information with
    the external calendar view of the room booking system.

Reset user tokens
=================

Each calendar feed URL contains a token that uniquely identifies you so you can
access feeds that would not be available to other users.

If another person gains access to that token they can consequently access
confidential information from castellum. So in that case the token needs to be
reset.

An administrator can delete the token in the admin UI. A new one will be
generated automatically.
