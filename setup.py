import re
import sys
from setuptools import setup

with open('spaces_client/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='spaces-client',
    version=version,
    #url='',
    license='MIT',
    author='Colin Simmonds',
    author_email='ctsimmonds@avaya.com',
    description='Python library for a chat client using Avaya Spaces.',
    long_description=long_description,
    packages=['spaces_client'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'python-socketio>=4.6.0'
        'requests>=2.21.0',
        'aiohttp>=3.4',
        'websockets>=7.0'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
