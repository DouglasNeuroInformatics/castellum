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
        "Django==2.1.5",
        "django-auth-ldap==1.7.0",
        "django-bootstrap4==0.0.7",
        "django-extra-views==0.12.0",
        "django-npm==1.0.0",
        "django-parler==1.9.2",
        "django-phonenumber-field==2.1.0",
        "django-picklefield==2.0",
        "Faker==1.0.1",
        "jsonschema==2.6.0",
        "phonenumberslite==8.10.3",
        "psycopg2==2.7.6.1",
        "python-dateutil==2.7.5",
    ],
)
