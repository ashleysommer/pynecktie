"""
pyNecktie
"""
import codecs
import os
import re
from distutils.errors import DistutilsPlatformError
from distutils.util import strtobool

from setuptools import setup


def open_local(paths, mode='r', encoding='utf8'):
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        *paths
    )

    return codecs.open(path, mode, encoding)


with open_local(['pynecktie', '__init__.py'], encoding='latin1') as fp:
    try:
        version = re.findall(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]\r?$",
                             fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


with open_local(['README.rst']) as rm:
    long_description = rm.read()

setup_kwargs = {
    'name': 'pyNecktie',
    'version': version,
    'url': 'http://github.com/ashleysommer/pynecktie/',
    'license': 'MIT',
    'author': 'Ashley Sommer',
    'author_email': 'ashleysommer@gmail.com',
    'description': (
        'A High Performance Asynchronous Python3 HTTP Micro Framework for serious business.'),
    'long_description': long_description,
    'packages': ['pynecktie'],
    'platforms': 'any',
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
}

ujson = 'ujson>=1.35'
uvloop = 'uvloop>=0.5.3'

requirements = [
    'httptools>=0.0.9',
    uvloop,
    ujson,
    'aiofiles>=0.3.0',
    'websockets>=5.0,<6.0',
    'multidict>=4.0,<5.0',
]
if strtobool(os.environ.get("NECKTIE_NO_UJSON", "no")):
    print("Installing without uJSON")
    requirements.remove(ujson)

# 'nt' means windows OS
if strtobool(os.environ.get("NECKTIE_NO_UVLOOP", "no")) or os.name == 'nt':
    print("Installing without uvLoop")
    requirements.remove(uvloop)

try:
    setup_kwargs['install_requires'] = requirements
    setup(**setup_kwargs)
except DistutilsPlatformError as exception:
    requirements.remove(ujson)
    requirements.remove(uvloop)
    print("Installing without uJSON or uvLoop")
    setup_kwargs['install_requires'] = requirements
setup(**setup_kwargs)
