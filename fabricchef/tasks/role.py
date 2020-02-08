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
        ('json', print_table),
        as_flat=('json', lambda x: print_dict_as_flat_table({"_": json.loads(x)}))
    )


@task
def show(role_name):
    """
    Show Role.

    :param role_name: Role name.
    """
    def print_table(knife_output):
        j = json.loads(knife_output)

        print(blue("Role:", bold=True))
        table1 = PrettyTable()
        table1.add_column("Name", [j['name']], 'l')
        table1.add_column("Description", [j['description']], 'l')
        print(table1)

        print(blue("RunList:", bold=True))
        table2 = PrettyTable(["Position", "RunList"])
        table2.align["Position"] = 'r'
        table2.align["RunList"] = 'l'
        position = 0
        for i in j['run_list']:
            table2.add_row([position, i])
            position += 1
        print(table2)
        print("%s RunList(s)" % len(j['run_list']))

        print(blue("Default attributes:", bold=True))
        print_dict_as_flat_table(j['default_attributes'])

        print(blue("Override attributes:", bold=True))
        print_dict_as_flat_table(j['override_attributes'])

    printf(
        knife('role show %s' % role_name, always_run=True),
        as_table=('json', print_table)
    )


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
