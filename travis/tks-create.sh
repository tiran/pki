#!/bin/bash
set -e

pkispawn -vv -f ${BUILDDIR}/pki/travis/pki.cfg -s TKS
