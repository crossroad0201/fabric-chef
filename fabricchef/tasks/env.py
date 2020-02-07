# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.colors import green,blue

from fabricchef.api import *

import json
from prettytable import PrettyTable

@task
def list():
    """
    List all Environments in Organization.
    """
    def to_table(result):
        j = json.loads(result)

        print(blue("Environments:", bold=True))
        table = PrettyTable(["Name"])
        table.align["Name"] = 'l'
        for i in j:
            table.add_row([i])
        print(table)
        print("%s Environment(s)" % len(j))

    printf(
        knife3('environment list', always_run=True),
        to_table
    )


@task
def show():
    """
    Show current Environment.
    """
    def to_table(result):
        j = json.loads(result)

        print(blue("Environment:", bold=True))
        table1 = PrettyTable()
        table1.add_column("Name", [j["name"]])
        table1.align["Name"] = 'l'
        table1.add_column("Description", [j["description"]])
        table1.align["Description"] = 'l'
        print(table1)

        print(blue("Cookbook versions:", bold=True))
        table2 = PrettyTable(["Name", "Version"])
        table2.align["Name"] = 'l'
        table2.align["Version"] = 'l'
        for name, version in j["cookbook_versions"].items():
            table2.add_row([name, version])
        print(table2)

        print(blue("Default attributes:", bold=True))
        print(json.dumps(j["default_attributes"], indent=2, sort_keys=True))

        print(blue("Override attributes:", bold=True))
        print(json.dumps(j["override_attributes"], indent=2, sort_keys=True))

    printf(
        knife3('environment show %s' % env.ChefEnv, always_run=True),
        to_table
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
        knife3('knife environment from file %s' % env_path)
    )

    list()
