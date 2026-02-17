# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Percolator."""

from __future__ import absolute_import, print_function

import json

from flask import current_app
from invenio_indexer.utils import schema_to_index
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search, current_search_client
from invenio_search.utils import build_index_name

from .models import OAISet
from .proxies import current_oaiserver
from .query import query_string_parser


def _build_percolator_index_name(index):
    """Build percolator index name."""
    suffix = "-percolators"
    return build_index_name(index, suffix=suffix, app=current_app)


def _create_percolator_mapping(index, mapping_path=None):
    """Update mappings with the percolator field.

    .. note::

        This is only needed from ElasticSearch v5 onwards, because percolators
        are now just a special type of field inside mappings.
    """
    percolator_index = _build_percolator_index_name(index)
    if not mapping_path:
        mapping_path = current_search.mappings[index]
    if not current_search_client.indices.exists(index=percolator_index):
        with open(mapping_path, "r") as body:
            mapping = json.load(body)
            mapping["mappings"]["properties"].update(PERCOLATOR_MAPPING["properties"])
            current_search_client.indices.create(index=percolator_index, body=mapping)
    


def _percolate_query(index, document):
    """Get results for a percolate query."""
    index = _build_percolator_index_name(index)
    es_client_params = dict(
        index=index, allow_no_indices=True,
        ignore_unavailable=True, body={
            'query': {
                'percolate': {
                    'field': 'query',
                    # 'document_type': percolator_doc_type,
                    'document': document,
                }
            }
        })
    results = current_search_client.search(**es_client_params)
    return results['hits']['hits']


PERCOLATOR_MAPPING = {
    'properties': {'query': {'type': 'percolator'}}
}


def _new_percolator(spec, search_pattern):
    """Create new percolator associated with the new set."""
    if spec and search_pattern:
        query = query_string_parser(search_pattern=search_pattern).to_dict()
        for index, mapping_path in current_search.mappings.items():
            # Create the percolator doc_type in the existing index for >= ES5
            # TODO: Consider doing this only once in app initialization
            _create_percolator_mapping(
                index, mapping_path)
            current_search_client.index(
                index=_build_percolator_index_name(index),
                id='oaiset-{}'.format(spec),
                body={'query': query}
            )


def _delete_percolator(spec, search_pattern):
    """Delete percolator associated with the new oaiset."""
    if spec:
        for index in current_search.mappings.keys():
            # Create the percolator doc_type in the existing index for >= ES5
            _create_percolator_mapping(index)
            current_search_client.delete(
                index=_build_percolator_index_name(index),
                id='oaiset-{}'.format(spec), ignore=[404]
            )


def _build_cache():
    """Build sets cache."""
    sets = current_oaiserver.sets
    if sets is None:
        # build sets cache
        sets = current_oaiserver.sets = [
            oaiset.spec for oaiset in OAISet.query.filter(
                OAISet.search_pattern.is_(None)).all()]
    return sets


def get_record_sets(record):
    """Find matching sets."""
    # get lists of sets with search_pattern equals to None but already in the
    # set list inside the record
    record_sets = set(record.get('_oai', {}).get('sets', []))
    for spec in _build_cache():
        if spec in record_sets:
            yield spec

    # get list of sets that match using percolator
    document = record.dumps()
    index = RecordIndexer().record_to_index(record)
    _create_percolator_mapping(index)
    results = _percolate_query(index, document)
    prefix = 'oaiset-'
    prefix_len = len(prefix)
    for match in results:
        set_name = match['_id']
        if set_name.startswith(prefix):
            name = set_name[prefix_len:]
            yield name

    raise StopIteration
