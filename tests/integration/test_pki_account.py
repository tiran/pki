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
import requests

import pki.account


class PKIAccountTests(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def connect(self, pkicfg, ca_connection):
        self.connection = ca_connection
        self.cfg = pkicfg

    def test_login_no_auth(self):
        acc = pki.account.AccountClient(self.connection)
        with self.assertRaises(requests.HTTPError) as e:
            acc.login()
        self.assertEqual(e.exception.response.status_code, 401)

    def test_login_invalid(self):
        self.connection.authenticate('user', 'invalid')
        acc = pki.account.AccountClient(self.connection)
        with self.assertRaises(requests.HTTPError) as e:
            acc.login()
        self.assertEqual(e.exception.response.status_code, 401)

    def test_login_credentials(self):
        self.connection.authenticate(*self.cfg.ca_credentials)
        acc = pki.account.AccountClient(self.connection)
        acc.login()
        acc.logout()

    def test_login_cert(self):
        self.connection.set_authentication_cert(self.cfg.admin_cert)
        acc = pki.account.AccountClient(self.connection)
        acc.login()
        acc.logout()
