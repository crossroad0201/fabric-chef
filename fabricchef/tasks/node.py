# -*- coding: utf-8 -*-

from __future__ import print_function

import itertools as itr
import re

from fabric.colors import green, blue, yellow

from fabricchef.api import *
from fabricchef.tasks.databag import get_exists_databag_item_names, parse_databag_item_name

import json
from prettytable import PrettyTable


# TODO Show Last Check-in.
@task
def list(chef_env=None):
    """
    List Nodes in specified Environment.

    :param chef_env: Chef Environment.(Default all environments)
    """
    def print_table(knife_output):
        j = json.loads(knife_output)

        table = PrettyTable(["NodeName", "Platform", "FQDN", "IP Address", "Uptime", "Environment", "RunList"])
        table.align["NodeName"] = 'l'
        table.align["Platform"] = 'l'
        table.align["FQDN"] = 'l'
        table.align["IP Address"] = 'l'
        table.align["Uptime"] = 'l'
        table.align["Environment"] = 'l'
        table.align["RunList"] = 'l'
        for i in sorted(j['rows'], key=lambda x: x['name']):
            a = i['automatic']
            table.add_row([
                i['name'],
                "%s(%s)" % (a['platform'], a['platform_version']),
                a['fqdn'],
                a['ipaddress'],
                a['uptime'],
                i['chef_environment'],
                i['run_list']
            ])
        print(table)
        print("%s Node(s)" % len(j))

    query = '"chef_environment:%s"' % chef_env if chef_env else ''
    printf(
        knife('search node %s' % query, always_run=True),
        ('json', print_table)
    )


@task
def show(node_name, show_all_attrs='False'):
    """
    Show Node.

    :param node_name: Node name.
    :param show_all_attrs: Show all attributes.(True|False) (Default False)
    """
    def print_table_all(knife_output):
        j = json.loads(knife_output)
        a = j['automatic']

        print(blue("Node:", bold=True))
        table1 = PrettyTable()
        table1.add_column("NodeName", [j['name']], 'l')
        table1.add_column("Platform", ["%s(%s)" % (a['platform'], a['platform_version'])], 'l')
        table1.add_column("FQDN", [a['fqdn']], 'l')
        table1.add_column("IP Address", [a['ipaddress']], 'l')
        table1.add_column("Uptime", [a['uptime']], 'l')
        table1.add_column("Environment", [j['chef_environment']], 'l')
        table1.add_column("RunList", [j['run_list']], 'l')
        print(table1)

        print(blue("Device:", bold=True))
        table2 = PrettyTable()
        table2.add_column("CPU Cores", [a['cpu']['cores']], 'r')
        table2.add_column("Memory Free/Total",
                          ["%s / %s" % (
                              a['memory']['free'],
                              a['memory']['total']
                          )], 'r')
        table2.add_column("Disk Free/Total (KB)",
                          ["%s / %s" %(
                              a['filesystem']['by_mountpoint']['/']['kb_available'],
                              a['filesystem']['by_mountpoint']['/']['kb_size']
                          )], 'r')
        print(table2)

    def print_table(knife_output):
        j = json.loads(knife_output)

        print(blue("Node:", bold=True))
        table = PrettyTable()
        table.add_column("NodeName", [j['name']], 'l')
        table.add_column("Environment", [j['chef_environment']], 'l')
        table.add_column("RunList", [j['run_list']], 'l')
        print(table)

    if show_all_attrs in ('True', 'true', 'yes'):
        printf(
            knife('node show %s -l' % node_name, always_run=True),
            ('json', print_table_all)
        )
    else:
        printf(
            knife('node show %s' % node_name, always_run=True),
            ('json', print_table)
        )


@task
def add(chef_env, host_name, node_name=None, *accessible_databag_item_patterns):
    """
    Add Node to current Environment.

    Example)
      Add node with same name as host in Environment prod.
      $ fab node.add:prod,foobar.example.com

      Add node with specified name in Environment prod.
      $ fab node.add:prod,foobar.example.com,foobar

      Add node with same name as host in Environment prod, and  grant access to DataBag items*_prod.
      $ fab node.add:prod,foobar.example.com,None,".*_prod"

    :param chef_env: Add to Chef Environment.
    :param host_name: Host name of node to be added.
    :param node_name: Node name. Use host name if specified None.  (Default Use host_name as node name)
    :param accessible_databag_item_patterns: DataBag item(s) accessed from added node.(Can use regex) (Default nothing)
    """
    _node_name = node_name if node_name and node_name != 'None' else host_name

    print(green("Adding Node %s(Host=%s) in Environment %s..." % (_node_name, host_name, chef_env)))
    printt(
        knife(
            'bootstrap %s --sudo --ssh-user=`whoami` --node-name=%s --environment=%s' %
            (host_name, _node_name, chef_env)
        )
    )

    if accessible_databag_item_patterns:
        print(green("Retrieving existing DataBag items..."))
        exists_databag_item_names = get_exists_databag_item_names()

        databag_item_names_tobe_access = set()
        for p, i in itr.product([re.compile(x) for x in accessible_databag_item_patterns], exists_databag_item_names):
            if p.match(i):
                databag_item_names_tobe_access.add(i)

        if databag_item_names_tobe_access:
            for i in databag_item_names_tobe_access:
                print(green("Grant access to DataBag item %s..." % i))
                (databag_name, item_name) = parse_databag_item_name(i)
                printt(knife('vault update %s %s -C "%s"' % (databag_name, item_name, _node_name)))
        else:
            print(yellow(
                "No DataBag item matches the specified pattern %s." %
                ", ".join(accessible_databag_item_patterns)
            ))

    if not env.DryRun:
        show(_node_name)
