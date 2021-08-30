# API

## Overview

Castellum is primarily a GUI application. There are only a few
carefully chosen API endpoints. These are:

-   `/execution/<study_id>/api/domains/`
-   `/execution/<study_id>/api/domains/<domain>/<pseudonym>/`
-   `/execution/<study_id>/api/domains/<domain>/<pseudonym>/attributes/`
-   `/execution/<study_id>/api/domains/<domain>/<pseudonym>/<target_domain>/`

## Authentication

Each user in castellum has an automatically generated token. This token
must be included in the `Authorization` HTTP header:

    Authorization: token 740a8632-4df1-4fd9-b7c5-9aaaa6626de0

To reset a token, simply clear it in the admin UI. A new one will be
generated automatically.

User accounts that are used for API clients should be prevented from
logging in by setting no password.
