# -*- coding: utf-8 -*-
# Authors:
#     Christian Heimes <cheimes@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright (C) 2016 Red Hat, Inc.
# All rights reserved.
#

import json
import os
import shutil

import betamax
from betamax.serializers import JSONSerializer

import pytest

from pki.client import PKIConnection

HERE = os.path.dirname(os.path.abspath(__file__))

CASSETTES_LIBRARY = os.path.join(HERE, 'cassettes')
# 'none, 'all', 'new_episodes'
RECORD_MODE = os.getenv('BETAMAX_RECORD', 'none')

if RECORD_MODE == 'all':
    shutil.rmtree(CASSETTES_LIBRARY)
    os.makedirs(CASSETTES_LIBRARY)


class FilteredSerializer(JSONSerializer):
    """Filter out response fields and pretty print JSON

    Tomcat returns some fields that differ between each request, e.g.
    current date. These headers cause git diffs during recordings.
    """
    name = 'filteredjson'
    drop_request_headers = {'Cookie'}
    drop_response_headers = {'Date', 'ETag', 'Last-Modified', 'Set-Cookie'}
    pretty = True

    def serialize(self, cassette_data):
        for interaction in cassette_data['http_interactions']:
            # interaction.pop('recorded_at')
            headers = interaction['request']['headers']
            for drop in self.drop_request_headers:
                headers.pop(drop, None)
            headers = interaction['response']['headers']
            for drop in self.drop_response_headers:
                headers.pop(drop, None)
        if self.pretty:
            return json.dumps(
                cassette_data,
                sort_keys=True,
                indent=1,
                separators=(',', ': '),
            )
        else:
            return json.dumps(cassette_data, sort_keys=True)


betamax.Betamax.register_serializer(FilteredSerializer)


with betamax.Betamax.configure() as config:
    config.cassette_library_dir = CASSETTES_LIBRARY
    # 'none, 'all', 'new_episodes'
    config.default_cassette_options['record_mode'] = RECORD_MODE
    config.default_cassette_options['match_requests_on'] = [
        'method', 'uri', 'headers', 'body'
    ]
    config.default_cassette_options['serialize_with'] = 'filteredjson'
    config.default_cassette_options['allow_playback_repeats'] = True


class PKIConfig(object):
    remote_protocol = u'https'
    remote_hostname = u'pki.test'
    remote_port = u'8443'
    ca_credentials = ['caadmin', 'Secret.123']
    admin_cert = os.path.join(HERE, 'ca_admin_cert.pem')

    name = u'pkitest'
    basedn = u'OU={name},O={name}'.format(name=name)
    subsystems = {u'CA', u'KRA'}
    secure_port = u'8443'
    unsecure_port = u'8080'
    hostname = remote_hostname
    ca_name = u'CA {} {}'.format(hostname, secure_port)
    kra_name = u'KRA {} {}'.format(hostname, secure_port)


@pytest.fixture()
def pkicfg():
    return PKIConfig


def get_client(pkicfg, betamax_session, subsystem):
    # enforce fixed user agent.
    # python-requests sets a user agent that contains its version.
    betamax_session.headers['User-Agent'] = 'PKI tests'
    return PKIConnection(
        protocol=pkicfg.remote_protocol,
        hostname=pkicfg.remote_hostname,
        port=pkicfg.remote_port,
        subsystem=subsystem,
        session=betamax_session)


@pytest.fixture()
def ca_connection(pkicfg, betamax_session):
    return get_client(pkicfg, betamax_session, 'ca')
