#!/bin/sh
RPM_TOP_DIR=${RPM_TOP_DIR=$(rpm --eval %_topdir)}

specfile=$1
[[ -z "$specfile" ]] && { echo "ERROR: undefined specfile"; exit 1; }

ARCH=$2
[[ -z "$ARCH" ]] && { echo "ERROR: undefined architecture"; exit 1; }

SPECFILE=$RPM_TOP_DIR/SPECS/cross-$ARCH-$specfile
cat - $specfile > $SPECFILE << EOF
##
## This a generated specfile from ${specfile##*/}
##
%define cross $ARCH
##
EOF
exec rpm -ba $SPECFILE
