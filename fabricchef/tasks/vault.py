# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.colors import green, blue

from fabricchef.api import *

import json
from prettytable import PrettyTable


def parse_vault_item_name(vault_item_name):
    if "." in vault_item_name:
        return vault_item_name.split(".")
    else:
        abort(red(
            "Invalid vault_item_name. Specify Vault name and item name with dot delimited, like this foo.bar - %s" %
            vault_item_name
        ))


def format_vault_item_name(vault_name, item_name):
    return '%s.%s' % (vault_name, item_name)


def get_exists_vault_item_names():
    # Parsing text response because 'value list' does not supports output as json format.
    exists_vault_item_names = []
    vault_names = knife('vault list', always_run=True)('text').split('\n')
    for vault_name in sorted(vault_names):
        vault_item_names = knife('vault show %s' % vault_name, always_run=True)('text').split('\n')
        for vault_item_name in sorted(vault_item_names):
            exists_vault_item_names.append(format_vault_item_name(vault_name, vault_item_name))
    return exists_vault_item_names


@task
def list():
    """
    List all Vault items.
    """
    vault_item_names = get_exists_vault_item_names()
    if env.OutputFormat == 'json':
        print("[")
        for i in vault_item_names[:-1]:
            print("  \"%s\"," % i)
        print("  \"%s\"" % vault_item_names[-1])
        print("]")
    elif env.OutputFormat == 'table':
        print(blue("Vault items:"))
        table = PrettyTable(["Name"])
        table.align["Name"] = 'l'
        for i in vault_item_names:
            table.add_row([i])
        print(table)
        print("%s Vault item(s)" % len(vault_item_names))
    elif env.OutputFormat == 'flat':
        print_dict_as_flat_table({"_": vault_item_names})
    else:
        for i in vault_item_names:
            print(i)


@task
def show(vault_item_name):
    """
    Show Vault item.

    :param vault_item_name: Vault name. Like a foo.bar.
    """
    (vault_name, item_name) = parse_vault_item_name(vault_item_name)

    def print_table(knife_output):
        j = json.loads(knife_output)

        print(blue("Vault item:"))
        table1 = PrettyTable()
        table1.add_column("Name", "%s %s" % (vault_name, [j['id']]), 'l')
        table1.add_column("Admins", [", ".join(j['admins'])], 'l')
        print(table1)

        print(blue("Clients:"))
        table2 = PrettyTable(["Client"])
        table2.align["Client"] = 'l'
        for i in j['clients']:
            table2.add_row(i)
        print(table2)

        print(blue("Values:"))
        del j['id'], j['admins'], j['clients'], j['search_query']
        print(json.dumps(j, indent=2, sort_keys=True))

    printf(
        knife('vault show %s %s -p all' % (vault_name, item_name), always_run=True),
        ('json', print_table)
    )


# TODO Upsertにしたい
@task
def apply(vault_item_name, item_value, *admins):
    """
    Create Vault item. (and grant admin permission)

    Example)
      Create Vault item 'foo bar' with admin to max and alex.
      $ fab vault.apply:foo.bar,'{"password":"XXXXXXX"}',max,alex

    :param vault_item_name: Vault name. Like a foo.bar.
    :param item_value: Vault item value.
    :param admins: Additional administrator(s) for this Vault item.
    """
    (vault_name, item_name) = parse_vault_item_name(vault_item_name)
    print(green("Creating Vault item %s %s..." % (vault_name, item_name)))
    printt(
        knife('vault create %s %s \'%s\'' % (vault_name, item_name, item_value))
    )

    if admins:
        admins_str = ','.join(str(s) for s in admins)
        print(green("Grant administration permission to %s..." % admins_str))
        printt(
            knife('vault update %s %s -A "%s" -M client' % (vault_name, item_name, admins_str))
        )

    show(vault_item_name)
