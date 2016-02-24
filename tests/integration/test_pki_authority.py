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

import unittest

import pytest

import pki
import pki.authority
import pki.account


class PKIAuthorityClientTests(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def connect(self, pkicfg, ca_connection):
        self.connection = ca_connection
        self.cfg = pkicfg
        self.client = pki.authority.AuthorityClient(self.connection)
        self.ca_dn = u'CN=CA Signing Certificate,{0.basedn}'.format(self.cfg)

    def login(self):
        self.connection.set_authentication_cert(self.cfg.admin_cert)
        pki.account.AccountClient(self.connection).login()

    def get_ad_by_dn(self, dn):
        for ca in self.client.list_cas():
            if ca.dn == dn:
                return ca
        else:
            ValueError(dn)

    def test_list_cas(self):
        collection = self.client.list_cas()
        self.assertIsInstance(collection, pki.authority.AuthorityDataCollection)
        cas = list(collection)
        self.assertEqual(len(cas), 1)
        ca = cas[0]
        self.assertEqual(ca.dn, self.ca_dn)
        self.assertEqual(ca.description, u'Host authority')
        self.assertTrue(ca.is_host_authority)
        self.assertTrue(ca.enabled)
        self.assertIs(ca.parent_aid, None)
        self.assertEqual(self.get_ad_by_dn(ca.dn).aid, ca.aid)

    def test_get_ca(self):
        ca = self.get_ad_by_dn(self.ca_dn)
        self.assertEqual(self.client.get_ca(ca.aid).dn, self.ca_dn)
        with self.assertRaises(pki.BadRequestException):
            self.client.get_ca('invalid')

    def test_disable_anon(self):
        with self.assertRaises(pki.ForbiddenException):
            self.client.disable_ca('aid')

    def XXX_test_disable_enable(self):
        self.login()
        ca = self.get_ad_by_dn(self.ca_dn)
        self.assertTrue(ca.enabled)

        self.client.disable_ca(ca.aid)
        ca = self.get_ad_by_dn(self.ca_dn)
        self.assertFalse(ca.enabled)

        self.client.enable_ca(ca.aid)
        ca = self.get_ad_by_dn(self.ca_dn)
        self.assertTrue(ca.enabled)

    def test_get_chain(self):
        ca = self.get_ad_by_dn(self.ca_dn)
        chain = self.client.get_chain(ca.aid)
        # XXX text makes no sense here
        self.assertEqual(chain[0], '0')
        chain = self.client.get_chain(ca.aid, 'PEM')
        # PEM encoded PKCS7? what a bundle of PEM-encoded X.509 certs?
        self.assertEqual(chain.split('\n')[0], '-----BEGIN PKCS7-----')

    def XXX_test_create_ca(self):
        self.login()

        ca = self.get_ad_by_dn(self.ca_dn)
        subca = pki.authority.AuthorityData(
            dn=u'CN=CA Test Certificate,{0.basedn}'.format(self.cfg),
            description=u'test CA cert',
            parent_aid=ca.aid,
            enabled='true'
        )
        self.client.create_ca(subca)
