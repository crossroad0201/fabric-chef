# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.api import *
from fabric.colors import green,blue,yellow,red

from fabricchef.api import *

@task
def list():
    """
    List all Roles in Organization.
    """
    knife('role list', always_run=True)

@task
def apply(role_path='./roles/*'):
    """
    Create or Update Role(s) from specified path(dir or file).

    :param role_path: Path to Role definition file(s). Ex)foobar/roles/* , foobar/roles/foo_bar.json (Default ./roles/*)
    """
    print(green('Creating or updating Role(s) from %s...' % role_path))
    knife('knife role from file %s' % role_path)

    list()
