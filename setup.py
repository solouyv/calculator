#!/usr/bin/env python3

from subprocess import check_call
from setuptools import find_packages, setup
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        check_call("export FLASK_APP=web".split())
        check_call("flask init-db".split())


setup(
    name='webpycalc',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'webpycalc = webpycalc:main',
            'pycalc = pycalc:main',
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
    install_requires=[
        'flask',
    ],
)
