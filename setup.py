from setuptools import find_packages, setup


setup(
    name="castellum",
    version="0.0.1",

    author="Max-Planck-Gesellschaft",
    license="AGPL-3.0-or-later",

    packages=find_packages(),

    install_requires=[
        "cologne-phonetics==1.2.3",
        "Django==2.1.2",
        "django-auth-ldap==1.7.0",
        "django-bootstrap4==0.0.7",
        "django-extra-views==0.12.0",
        "django-npm==1.0.0",
        "django-phonenumber-field==2.0.1",
        "django-picklefield==1.1.0",
        "Faker==0.9.2",
        "psycopg2==2.7.5",
        "python-dateutil==2.7.3",
        "django-hvad @ https://github.com/KristianOellegaard/django-hvad/archive/2.0.0-beta.tar.gz",
    ],
)
