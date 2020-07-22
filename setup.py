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
        "Django==3.0.8",
        "django-bootstrap4==2.2.0",
        "django-ical==1.7.1",
        "django-npm==1.0.0",
        "django-parler==2.0.1",
        "django-phonenumber-field==4.0.0",
        "django-stronghold==0.4.0",
        "Faker==4.1.1",
        "file-magic==0.4.0",
        "geopy==2.0.0",
        "icalendar==4.0.6",
        "jsonschema==3.2.0",
        "phonenumberslite==8.12.6",
        "psycopg2-binary==2.8.5",
        "python-dateutil==2.8.1",
        "requests==2.24.0",
        "simplecharts==0.0.2",
    ],
)
