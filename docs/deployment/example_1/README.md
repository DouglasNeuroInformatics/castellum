# Example 1: Containerized Deployment

This section of the deployment documentation illustrates how to set up
Castellum based on Docker, uWSGI, PostgreSQL, and LDAP.

## Before You Start

This guide illustrates how to set up a containerized deployment of
Castellum. If you prefer to install Castellum manually, please refer to
[Example 2](../example_2/README.md). We assume you have root access to a
(virtual) machine running a recent Linux distribution that has internet
access. Further, [Docker](https://www.docker.com/#) needs to be
installed and configured correctly on this machine.

## Quickstart

Simply open a terminal and launch `start.sh`. Pass `--demo` to
automatically create demo content.
