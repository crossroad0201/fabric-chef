# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.colors import green,blue

from fabricchef.api import *

import json
from prettytable import PrettyTable
from flatten_json import flatten


@task
def list():
    """
    List all Environments in Organization.
    """
    def print_table(result):
        j = json.loads(result)

        print(blue("Environments:", bold=True))
        table = PrettyTable(["Name"])
        table.align["Name"] = 'l'
        for i in j:
            table.add_row([i])
        print(table)
        print("%s Environment(s)" % len(j))

    printf(
        knife('environment list', always_run=True),
        ('json', print_table)
    )


@task
def show(chef_env):
    """
    Show current Environment.

    :param chef_env: Chef Environment.
    """
    def print_table(knife_output):
        j = json.loads(knife_output)

        print(blue("Environment:", bold=True))
        table1 = PrettyTable()
        table1.add_column("Name", [j['name']], 'l')
        table1.add_column("Description", [j['description']], 'l')
        print(table1)

        print(blue("Cookbook versions:", bold=True))
        table2 = PrettyTable(["Name", "Version"])
        table2.align["Name"] = 'l'
        table2.align["Version"] = 'l'
        for name, version in j['cookbook_versions'].items():
            table2.add_row([name, version])
        print(table2)

        print(blue("Default attributes:", bold=True))
        table3 = PrettyTable(["Key", "Value"])
        table3.align["Key"] = 'l'
        table3.align["Value"] = 'l'
        for key, value in sorted(flatten(j['default_attributes'], '.').items()):
            table3.add_row([key, value])
        print(table3)

        print(blue("Override attributes:", bold=True))
        table4 = PrettyTable(["Key", "Value"])
        table4.align["Key"] = 'l'
        table4.align["Value"] = 'l'
        for key, value in sorted(flatten(j['override_attributes'], '.').items()):
            table4.add_row([key, value])
        print(table4)

    printf(
        knife('environment show %s' % chef_env, always_run=True),
        ('json', print_table)
    )


@task
def apply(env_path='./environments/*'):
    """
    Create or Update Environment(s) from specified path(dir or file).

    :param env_path: Path to Environment definition file(s).
                     Ex)foobar/environments/* , foobar/environments/prod.json (Default ./environments/*)
    """
    print(green('Creating or updating Environment(s) from %s...' % env_path))
    printt(
        knife('knife environment from file %s' % env_path)
    )

    list()
