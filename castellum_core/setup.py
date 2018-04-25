from setuptools import find_packages, setup


setup(
    name="castellum-core",
    version="0.0.1",

    author="Max-Planck-Gesellschaft",

    packages=find_packages(),

    install_requires=[
        "Django==2.0.4",
        "django-bootstrap4==0.0.6",
        "django-npm==1.0.0"
    ],
)
