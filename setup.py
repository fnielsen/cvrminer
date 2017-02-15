import os
from setuptools import setup


filename = os.path.join(os.path.dirname(__file__), 'requirements.txt')
requirements = open(filename).read().splitlines()


setup(
    name='cvrminer',
    author='Finn Aarup Nielsen',
    author_email='faan@dtu.dk',
    license='Apache License',
    install_requires=requirements,
    url='https://github.com/fnielsen/cvrminer',
    packages=['cvrminer'],
    tests_require=['flake8', 'pydocstyle'],
)
