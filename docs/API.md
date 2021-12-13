# API

## Overview

Castellum is primarily a GUI application. There is no API by default.
The following API endpoints can be enabled with the
`CASTELLUM_API_ENABLED` setting:

-   `/studies/api/studies/?status=<edit|execution|finished>`
-   `/studies/api/studies/<study_id>/`
-   `/execution/api/studies/<study_id>/domains/`
-   `/execution/api/studies/<study_id>/domains/<domain>/`
-   `/execution/api/studies/<study_id>/domains/<domain>/<pseudonym>/`
-   `/execution/api/studies/<study_id>/domains/<domain>/<pseudonym>/attributes/`
-   `/execution/api/studies/<study_id>/domains/<domain>/<pseudonym>/<target_domain>/`

## Authentication

Each user in castellum has an automatically generated token. This token
must be included in the `Authorization` HTTP header:

    Authorization: token 740a8632-4df1-4fd9-b7c5-9aaaa6626de0

To reset a token, simply clear it in the admin UI. A new one will be
generated automatically.

User accounts that are used for API clients should be prevented from
logging in by setting no password.
