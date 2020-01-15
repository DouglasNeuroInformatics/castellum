from setuptools import find_packages
from setuptools import setup

setup(
    name="castellum",
    version="0.0.1",

    author="Max-Planck-Gesellschaft",
    license="AGPL-3.0-or-later",

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
        "cologne-phonetics==1.2.3",
        "Django==3.0.2",
        "django-auth-ldap==2.0.0",
        "django-axes==5.0.20",
        "django-bootstrap4==1.1.1",
        "django-ical==1.7.0",
        "django-npm==1.0.0",
        "django-parler==2.0.1",
        "django-phonenumber-field==4.0.0",
        "django-picklefield==2.0",
        "Faker==3.0.0",
        "file-magic==0.4.0",
        "jsonschema==3.2.0",
        "phonenumberslite==8.11.1",
        "psycopg2-binary==2.8.4",
        "python-dateutil==2.8.1",
        "simplecharts==0.0.2",
    ],
)
