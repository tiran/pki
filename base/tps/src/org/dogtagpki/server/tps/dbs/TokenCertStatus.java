// --- BEGIN COPYRIGHT BLOCK ---
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; version 2 of the License.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
//
// (C) 2014 Red Hat, Inc.
// All rights reserved.
// --- END COPYRIGHT BLOCK ---
package org.dogtagpki.server.tps.dbs;

/*
 * TokenCertStatus - certificate statuses in the tokendb
 *
 * @author cfu
 */
public enum TokenCertStatus {
    UNINITIALIZED("uninitialized"),
    ACTIVE("active"),
    REVOKED("revoked"),
    ONHOLD("revoked_on_hold"),
    EXPIRED("expired")
    ;

    private final String certStatusString;

    private TokenCertStatus(final String status) {
        this.certStatusString = status;
    }

    @Override
    public String toString() {
        return certStatusString;
    }
}
