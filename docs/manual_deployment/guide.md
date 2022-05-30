# Production-Ready Deployment

The following guide aims to provide some tips for setting up a production-ready
deployment of Castellum. Just like the rest of the development documentation a familiarity
with web servers and databases in general, and Django and PostgreSQL specifically,
is assumed. To not needlessly clutter the main text, stubs of most configuration files
are provided alongside this document.

## Before You Start

This guide is mainly intended for manual installations of Castellum. If you prefer
a containerized setup, please refer to [example deployment](../example_deployment/).
We assume you have root access to two (virtual) machines running a recent Linux
distribution that have internet access and are connected to the same (private)
network:

* **Host 1**: `castellum-sv`, IP: 192.168.10.1
* **Host 2**: `castellum-db`, IP: 192.168.10.2

> Any recommended hardware specs?

Following the recommendation of the main deployment documentation, we further
presume that Castellum is going to be integrated into an existing LDAP setup:

* **LDAP Server**: `auth-sv`

Unless explicitly stated otherwise, all command prompts below are intended to
be run as `root`.

## Preparations

For the sake of simplicity we suppose `SELinux` is deactivated on both hosts.
However, for enhanced security please consider enabling `SELinux` and using
helper tools such as `audit2allow` to generate appropriate policy modules (for
a general introduction to `SELinux` access management, please refer to the [official
Red Hat Product Documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/security-enhanced_linux/sect-security-enhanced_linux-fixing_problems-allowing_access_audit2allow)).

### `castellum-sv`

Install required packages:

```bash
# Red Hat/Fedora/CentOS
dnf install @postgresql
dnf install openldap-devel postgresql-contrib nginx
```

```bash
# Debian/Ubuntu
apt install postgresql
apt install libldap-dev postgresql-contrib nginx
```

Download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
into `/opt/conda`.

### `castellum-db`

Install required packages:

```bash
# Red Hat/Fedora/CentOS
dnf install @postgresql
```

```bash
# Debian/Ubuntu
apt install postgresql
```

## Database Setup

- Default db on primary, contacts db on secondary
- Introduce names of dbs

### `castellum-sv`

Ensure PostgreSQL is started at boot, create new database cluster and start corresponding
daemon:

```bash
systemctl enable postgresql
postgresql-setup --initdb
systemctl start postgresql
```

Create a directory to collect all Castellum-related credentials, choose passwords
for both `default` as well as `contacts` databases and write them to dedicated files:

```bash
mkdir /etc/castellum
"${EDITOR:-emacs}" /etc/castellum/db_default.pw
"${EDITOR:-emacs}" /etc/castellum/db_contacts.pw
```

