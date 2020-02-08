# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.colors import green,blue

from fabricchef.api import *

import json
from prettytable import PrettyTable


@task
def list():
    """
    List all Roles in Organization.
    """
    def print_table(knife_output):
        j = json.loads(knife_output)

        print(blue("Roles:", bold=True))
        table = PrettyTable(["Name"])
        table.align["Name"] = 'l'
        for i in j:
            table.add_row([i])
        print(table)
        print("%s Role(s)" % len(j))

    printf(
        knife('role list', always_run=True),
        ('json', print_table)
    )


# TODO Supports show


@task
def apply(role_path='./roles/*'):
    """
    Create or Update Role(s) from specified path(dir or file).

    :param role_path: Path to Role definition file(s). Ex)foobar/roles/* , foobar/roles/foo_bar.json (Default ./roles/*)
    """
    print(green('Creating or updating Role(s) from %s...' % role_path))
    printt(
        knife('knife role from file %s' % role_path)
    )

    list()
