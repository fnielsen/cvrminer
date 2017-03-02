import os

from setuptools import setup

import versioneer


filename = os.path.join(os.path.dirname(__file__), 'requirements.txt')
requirements = open(filename).read().splitlines()


setup(
    name='cvrminer',
    author='Finn Aarup Nielsen',
    author_email='faan@dtu.dk',
    cmdclass=versioneer.get_cmdclass(),
    license='Apache License',
    package_data={
        'cvrminer': [
            'data/purpose_stop_words.txt',
        ]
    },
    install_requires=requirements,
    url='https://github.com/fnielsen/cvrminer',
    version=versioneer.get_version(),
    packages=['cvrminer'],
    tests_require=['flake8', 'pydocstyle'],
)
