from setuptools import find_packages, setup


setup(
    name="castellum",
    version="0.0.1",

    author="Max-Planck-Gesellschaft",
    license="AGPL-3.0-or-later",

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "cologne-phonetics==1.2.3",
        "Django==2.2.1",
        "django-auth-ldap==1.7.0",
        "django-bootstrap4==0.0.8",
        "django-extra-views==0.12.0",
        "django-ical==1.5",
        "django-npm==1.0.0",
        "django-parler==1.9.2",
        "django-phonenumber-field==2.3.1",
        "django-picklefield==2.0",
        "Faker==1.0.5",
        "file-magic==0.4.0",
        "jsonschema==3.0.1",
        "phonenumberslite==8.10.10",
        "psycopg2-binary==2.8.2",
        "python-dateutil==2.8.0",
    ],
)
