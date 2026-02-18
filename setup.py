# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that implements OAI-PMH server."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

tests_require = [
    'SQLAlchemy-Continuum>=1.2.1',
    'coverage>=4.0',
    'invenio-indexer==2.3.0',
    'invenio-jsonschemas==1.0.1',
    'invenio-marc21>=1.0.0a9',
    'mock>=1.3.0',
    'pytest-invenio>=1.2.1',
]

invenio_search_version = '1.2.0'

extras_require = {
    'admin': [
        'Flask-Admin==1.6.1',
    ],
    'celery': [
        'invenio-celery==1.3.1',
    ],
    # Elasticsearch
    'elasticsearch7': [
        'invenio-search[elasticsearch7]>={}'.format(invenio_search_version)
    ],
    'opensearch1': [
        'invenio-search[opensearch1]>=2.1.0,<3.0.0'
    ],
    'opensearch2': [
        'invenio-search[opensearch2]>=2.1.0,<3.0.0'
    ],
    # Database
    'mysql': [
        'invenio-db[mysql]==1.1.5',
    ],
    'postgresql': [
        'invenio-db[postgresql]==1.1.5',
    ],
    'sqlite': [
        'invenio-db==1.1.5',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name[0] == ':' or name in (
            'mysql', 'postgresql', 'sqlite',
            'elasticsearch2', 'elasticsearch5',
            'elasticsearch6', 'elasticsearch7',
            'opensearch1', 'opensearch2'):
        continue
    extras_require['all'].extend(reqs)

install_requires = [
    'arrow==1.3.0',
    'Flask==2.1.3',
    'Werkzeug>=0.14.1',
    'Flask-BabelEx>=0.9.3',
    'dojson==1.5.0',
    'invenio-pidstore==1.3.1',
    'invenio-records>=1.0.0',
    'invenio-rest==1.2.8',
    'lxml==5.2.2',
    'flask-cors>=3.0.8',
    'marshmallow==2.21.0',
]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_oaiserver', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-oaiserver',
    version=version,
    description=__doc__,
    long_description=readme,
    keywords='invenio OAI-PMH',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-oaiserver',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_oaiserver = invenio_oaiserver:InvenioOAIServer',
        ],
        'invenio_base.blueprints': [
            'invenio_oaiserver = invenio_oaiserver.views.server:blueprint',
        ],
        'invenio_base.api_apps': [
            'invenio_oaiserver = invenio_oaiserver:InvenioOAIServer',
        ],
        'invenio_db.alembic': [
            'invenio_oaiserver = invenio_oaiserver:alembic',
        ],
        'invenio_db.models': [
            'invenio_oaiserver = invenio_oaiserver.models',
        ],
        'invenio_admin.views': [
            'invenio_oaiserver = invenio_oaiserver.admin:set_adminview',
        ],
        'invenio_jsonschemas.schemas': [
            'oaiserver = invenio_oaiserver.schemas',
        ],
        'invenio_pidstore.minters': [
            'oaiid = invenio_oaiserver.minters:oaiid_minter',
        ],
        'invenio_pidstore.fetchers': [
            'oaiid = invenio_oaiserver.fetchers:oaiid_fetcher',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 5 - Production/Stable',
    ],
)
