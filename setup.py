import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'pylexa',
    version = '0.0.7',
    author = 'Patrick Smith',
    author_email = 'pjs482@gmail.com',
    description = ('A library to ease creation of an Alexa Skills Kit'),
    keywords = 'amazon alexa ask',
    url = 'http://www.github.com/patricksmith/pylexa',
    packages=['pylexa'],
    install_requires=['flask', 'python-dateutil', 'pycrypto', 'pyopenssl'],
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
    ],
)
