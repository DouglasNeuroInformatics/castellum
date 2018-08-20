from setuptools import find_packages, setup


entry_points = {
    "console_scripts": [
        "castellum-admin = django.core.management:execute_from_command_line",
    ],
}


setup(
    name="castellum",
    version="0.0.1",

    author="Max-Planck-Gesellschaft",
    license="AGPL-3.0-or-later",

    packages=find_packages(),

    entry_points=entry_points,

    install_requires=[
        "Django==2.1.0",
        "django-auth-ldap==1.4.0",
        "django-bootstrap4==0.0.6",
        "django-extra-views~=0.11.0",
        "django-npm==1.0.0",
        "django-phonenumber-field==2.0.0",
        "django-picklefield==1.0.0",
        "Faker==0.8.16",
        "psycopg2==2.7.4",
        "python-dateutil",
    ],
)
