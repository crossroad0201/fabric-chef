# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.api import *
from fabric.colors import green,blue,yellow,red

from fabricchef.api import *

@task
def list():
    """
    List all Environments in Organization.
    """
    knife('environment list', always_run=True)

@task
def show():
    """
    Show current Environment.
    """
    knife('environment show %s' % env.ChefEnv, always_run=True)

@task
def apply(env_path='./environments/*'):
    """
    Create or Update Environment(s) from specified path(dir or file).

    :param env_path: Path to Environment definition file(s). Ex)foobar/environments/* , foobar/environments/prod.json (Default ./environments/*)
    """
    print(green('Creating or updating Environment(s) from %s...' % env_path))
    knife('knife environment from file %s' % env_path)

    list()
