# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.colors import green, blue

from fabricchef.api import *

import json
from prettytable import PrettyTable


def parse_databag_item_name(databag_item_name):
    if "." in databag_item_name:
        return databag_item_name.split(".")
    else:
        abort(red(
            "Invalid databag_item_name. Specify DataBag name and item name with dot delimited, like this foo.bar - %s" %
            databag_item_name
        ))


def format_databag_item_name(databag_name, item_name):
    return '%s.%s' % (databag_name, item_name)


def get_exists_databag_item_names():
    # Parsing text response because 'value list' does not supports output as json format.
    exists_databag_item_names = []
    databag_names = knife('vault list', always_run=True)('text').split('\n')
    for databag_name in sorted(databag_names):
        databag_item_names = knife('vault show %s' % databag_name, always_run=True)('text').split('\n')
        for databag_item_name in sorted(databag_item_names):
            exists_databag_item_names.append(format_databag_item_name(databag_name, databag_item_name))
    return exists_databag_item_names


@task
def list():
    """
    List all DataBag items.
    """
    databag_item_names = get_exists_databag_item_names()
    if env.OutputFormat == 'json':
        print("[")
        for i in databag_item_names[:-1]:
            print("  \"%s\"," % i)
        print("  \"%s\"" % databag_item_names[-1])
        print("]")
    elif env.OutputFormat == 'table':
        print(blue("DataBag items:"))
        table = PrettyTable(["Name"])
        table.align["Name"] = 'l'
        for i in databag_item_names:
            table.add_row([i])
        print(table)
        print("%s DataBag item(s)" % len(databag_item_names))
    elif env.OutputFormat == 'flat':
        print_dict_as_flat_table({"_": databag_item_names})
    else:
        for i in databag_item_names:
            print(i)


@task
def show(databag_item_name):
    """
    Show DataBag item.

    :param databag_item_name: DataBag name. Like a foo.bar.
    """
    (databag_name, item_name) = parse_databag_item_name(databag_item_name)

    def print_table(knife_output):
        j = json.loads(knife_output)

        print(blue("DataBag item:"))
        table1 = PrettyTable()
        table1.add_column("Name", "%s %s" % (databag_name, [j['id']]), 'l')
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
        knife('vault show %s %s -p all' % (databag_name, item_name), always_run=True),
        ('json', print_table)
    )


# TODO Upsertにしたい
@task
def apply(databag_item_name, item_value, *admins):
    """
    Create DataBag item. (and grant admin permission)

    Example)
      Create DataBag item 'foo bar' with admin to max and alex.
      $ fab databag.apply:foo.bar,'{"password":"XXXXXXX"}',max,alex

    :param databag_item_name: DataBag name. Like a foo.bar.
    :param item_value: DataBag item value.
    :param admins: Additional administrator(s) for this DataBag item.
    """
    (databag_name, item_name) = parse_databag_item_name(databag_item_name)
    print(green("Creating DataBag item %s %s..." % (databag_name, item_name)))
    printt(
        knife('vault create %s %s \'%s\'' % (databag_name, item_name, item_value))
    )

    if admins:
        admins_str = ','.join(str(s) for s in admins)
        print(green("Grant administration permission to %s..." % admins_str))
        printt(
            knife('vault update %s %s -A "%s" -M client' % (databag_name, item_name, admins_str))
        )

    show(databag_item_name)
