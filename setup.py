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
        "Django==2.2.4",
        "django-auth-ldap==2.0.0",
        "django-bootstrap4==0.0.8",
        "django-ical==1.5",
        "django-npm==1.0.0",
        "django-parler==2.0",
        "django-phonenumber-field==3.0.1",
        "django-picklefield==2.0",
        "Faker==2.0.1",
        "file-magic==0.4.0",
        "jsonschema==3.0.2",
        "phonenumberslite==8.10.17",
        "psycopg2-binary==2.8.3",
        "python-dateutil==2.8.0",
    ],
)
