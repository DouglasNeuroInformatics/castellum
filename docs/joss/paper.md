---
title: 'Castellum: A participant management tool for scientific studies'
tags:
  - Python
  - Django
  - GDPR
  - participant management
  - study recruitment
  - study execution
  - pseudonym service
authors:
  - name: Tobias Bengfort
    affiliation: 1
  - name: Taib Hayat
    affiliation: 1
  - name: Timo Göttel^[Corresponding author]
    orcid: 0000-0003-0218-6358
    affiliation: 1
affiliations:
 - name: Max Planck Institute for Human Development, Berlin, Germany
   index: 1
date: 03 June 2022
bibliography: paper.bib

---

# Summary
`Castellum` is a web application aimed mainly at the lifecycle of human research studies by supporting participant management, pseudonym service, recruitment, study appointments and study execution. 

The main design focus of `Castellum` is compliance with the General Data Protection Regulation (EU) (GDPR) and IT security. Additionally, it is designed to be adaptable to other work flows or processes at different research institutions.

# Statement of Need
The web app `Castellum` is used to enable participation of interested persons in scientific studies and to centrally manage all participants' data and their study specific pseudonyms of a research institution. Thus, contact information, personal data relevant to a study (as for example age, highest graduation degree, ...) and process information (as for example existing consents or last study participations at the institution) have to be accurately managed and stored. `Castellum` was developed in order to ensure this in accordance with the applicable standards of the GDPR.

## Overview Key Features
`Castellum` allows to assign individual study-specific pseudonyms to the participants of each study to ensure that the actual scientific data can be stored separately from the contact data in another system (on a different server or file system).

In addition, `Castellum` allows that multiple pseudonym spaces ("domains") can be created in studies, so that several pseudonyms can be used per participant in a study.

The specific and expandable assignment of pseudonyms is intended to prevent the pooling/merging of scientific data across studies (or groups of people) without an appropriate legal basis.

During the execution of a study it is technically ensured that only users with the corresponding study-specific access role can access the contact data in `Castellum` via a domain specific pseudonym search. As soon as the data collection phase of a study is marked as finished in `Castellum`, this possibility expires. From then on, only the data protection coordinator role is able to access study participations. 

Additionally, `Castellum` allows to delete the pseudonym space of a study independent of the study status. After the deletion of a pseudonym space it will be impossible for any user to connect pseudonymized scientific data to the contact data in `Castellum`. This process enables or replaces the usual procedure in human science of destroying the coding list at a certain point after data collection.

## Roles and Rights Management
Users in the corresponding LDAP group are assigned to different roles in `Castellum`.There are five global roles: Data protection coordinator, Principal subject manager, Receptionist, Study approver, Study coordinator. Two of these roles (Data protection coordinator, Principal subject manager) allow comprehensive access to subject data. These roles should only be assigned to a very small group of people.
Within a study recruitment, recruiters are granted access to the contact data of persons who match the set filter criteria of the study. Conductors get access to the contact data and pseudonyms of persons who are marked as participating in the study. While users with the role of Principal subject manager are shown all matching records in the results list of subject search, the study-specific subject managers only receive search results for particpating subjects of their affiliated studies.

In addition to user management with roles, `Castellum` controls access to datasets via privacy levels. Different privacy levels are assigned to users, subjects and attributes. This ensures that users, regardless of the roles assigned to them, can only view records that correspond to their privacy level. Hierarchically the privacy level of a subject is higher than the privacy levels of the attributes.

`Castellum` allows that data is distributed across two databases (contact data can be kept separated from all other data). The actual research data is **never** stored in `Castellum`. The linking to this data is regulated by pseudonyms, which can only be resolved via appropriate rights in `Castellum`.

## Two-factor Authentication
To protect individuals' personal data from compromise or weak passwords, `Castellum` uses a standalone two-factor authentication (2FA) for Django that was also developed by a `Castellum` team member [@mfa3]. Users are required to enter an additional code before they can can log in to `Castellum`. Currently, any generic time-based one-time password (TOTP) application or FIDO2 hardware security token is supported.

## Considerations on the Production Environment 
The application should be hosted locally at a research facility and it is recommended to make it only available on the intranet; i.e., direct access via the internet should not be possible to minimize security threats. The access to the web interface should always be encrypted (SSL). 

Access to the server should be restricted to a small group of administrators of the corresponding institute. It is recommended that users should undergo recurring training on GDPR compliant usage of `Castellum` and its suggested interaction with participants.

# Acknowledgements

The `Castellum` project is funded by internal funds of the Max Planck Society.

# References