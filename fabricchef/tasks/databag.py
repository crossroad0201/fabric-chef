# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.colors import green

from fabricchef.api import *


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
    # vault list がJSON出力をサポートしていないのでテキストを改行で切ってます
    exists_databag_item_names = []
    databag_names = knife('vault list', 'text', capture=True, always_run=True).split('\n')
    for databag_name in databag_names:
        databag_item_names = knife('vault show %s' % databag_name, 'text', capture=True, always_run=True).split('\n')
        for databag_item_name in databag_item_names:
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
    knife('vault show %s %s -p all' % (databag_name, item_name), always_run=True)


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
    knife('vault create %s %s \'%s\'' % (databag_name, item_name, item_value))

    if admins:
        admins_str = ','.join(str(s) for s in admins)
        print(green("Grant administration permission to %s..." % (admins_str)))
        knife('vault update %s %s -A "%s" -M client' % (databag_name, item_name, admins_str))

    show(databag_item_name)
