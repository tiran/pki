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

import re
import unittest

import pytest
import pki.system


class PKISystemTests(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def connect(self, pkicfg, ca_connection):
        self.connection = ca_connection
        self.cfg = pkicfg

    def test_security_domain_info(self):
        client = pki.system.SecurityDomainClient(self.connection)
        info = client.get_security_domain_info()
        self.assertIsInstance(info, pki.system.SecurityDomainInfo)
        self.assertEqual(info.name, self.cfg.name)
        self.assertEqual(set(info.systems), self.cfg.subsystems)

        ca = info.systems[u'CA']
        self.assertIsInstance(ca, pki.system.SecurityDomainSubsystem)
        self.assertEqual(ca.name, u'CA')
        self.assertEqual(set(ca.hosts), {self.cfg.ca_name})
        host = ca.hosts[self.cfg.ca_name]
        self.assertEqual(
            host.__dict__,
            {
                'admin_port': self.cfg.secure_port,
                'agent_port': self.cfg.secure_port,
                'clone': u'FALSE',
                'domain_manager': u'TRUE',
                'ee_client_auth_port': self.cfg.secure_port,
                'hostname': self.cfg.hostname,
                'id': self.cfg.ca_name,
                'secure_port': self.cfg.secure_port,
                'subsystem_name': self.cfg.ca_name,
                'unsecure_port': self.cfg.unsecure_port}
        )
        self.assertEqual(info.systems[u'KRA'].name, u'KRA')

    def test_old_security_domain_info(self):
        client = pki.system.SecurityDomainClient(self.connection)
        info = client.get_old_security_domain_info()
        self.assertEqual(info.name, self.cfg.name)

    def test_get_status(self):
        client = pki.system.SystemStatusClient(self.connection)
        status = client.get_status()
        expected = re.escape(
            u'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
            u'<XMLResponse><State>1</State>'
            u'<Type>CA</Type><Status>running</Status>'
            u'<Version>VERSION</Version></XMLResponse>'
        ).replace('VERSION', '10.*[\w.-]+')
        self.assertRegex(status, expected)
