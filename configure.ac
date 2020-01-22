# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
define([VERSION_MAJOR], [1])
define([VERSION_MINOR], [1])
define([VERSION_FIX], [2])
define([VERSION_NUMBER], VERSION_MAJOR[.]VERSION_MINOR[.]VERSION_FIX)
define([VERSION_SUFFIX], [_master])

AC_INIT([ovirt-fast-forward-upgrade], VERSION_NUMBER[]VERSION_SUFFIX, [devel@ovirt.org])
PACKAGE_NAME="ovirt-fast-forward-upgrade"
PACKAGE_RPM_VERSION="VERSION_NUMBER"
PACKAGE_RPM_RELEASE="0"
AM_INIT_AUTOMAKE([-Wall -Werror foreign -Wno-portability tar-pax])

AC_SUBST([PACKAGE_RPM_VERSION])
AC_SUBST([PACKAGE_RPM_RELEASE])
AC_SUBST([COMMIT])
AC_SUBST([SHORT_COMMIT])

AC_PROG_INSTALL
AC_PROG_SED
AC_PROG_MAKE_SET
AC_PROG_MKDIR_P
AC_PROG_LN_S

AM_PATH_PYTHON([2.6],,[AC_MSG_ERROR([Cannot find python])])
case "${PYTHON_VERSION}" in
        2.*);;
        3.*);;
        *) AC_MSG_ERROR([python 2.6 or newer is required])
esac

# Python tools
AC_ARG_VAR([PYFLAKES], [flake8 utility])
AC_CHECK_PROGS([PYFLAKES], [flake8])

AC_CONFIG_FILES([
		Makefile
		src/Makefile
		man/Makefile
		ovirt-fast-forward-upgrade.spec])
AC_OUTPUT
