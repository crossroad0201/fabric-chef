# -*- coding: utf-8 -*-

from __future__ import print_function

import itertools as itr
import re

from fabric.colors import green, blue, yellow

from fabricchef.api import *
from fabricchef.tasks.databag import get_exists_databag_item_names, parse_databag_item_name

import json
from prettytable import PrettyTable


@task
def list():
    """
    List Nodes in current Environment.
    """
    def print_to_table(result):
        j = json.loads(result)

        table = PrettyTable(["NodeName", "Platform", "FQDN", "IP Address", "Uptime", "Environment", "RunList"])
        table.align["NodeName"] = 'l'
        table.align["Platform"] = 'l'
        table.align["FQDN"] = 'l'
        table.align["IP Address"] = 'l'
        table.align["Uptime"] = 'l'
        table.align["Environment"] = 'l'
        table.align["RunList"] = 'l'
        for i in j['rows']:
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

    printf(
        knife3('search node "chef_environment:%s"' % env.ChefEnv, always_run=True),
        print_to_table
    )


@task
def show(node_name, show_all_attrs='False'):
    """
    Show Node.

    :param node_name: Node name.
    :param show_all_attrs: Show all attributes.(True|False) (Default False)
    """
    def print_all_to_table(result):
        j = json.loads(result)
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

    def print_to_table(result):
        j = json.loads(result)

        print(blue("Node:", bold=True))
        table = PrettyTable()
        table.add_column("NodeName", [j['name']], 'l')
        table.add_column("Environment", [j['chef_environment']], 'l')
        table.add_column("RunList", [j['run_list']], 'l')
        print(table)

    if show_all_attrs in ('True', 'true', 'yes'):
        printf(
            knife3('node show %s -l' % node_name, always_run=True),
            print_all_to_table
        )
    else:
        printf(
            knife3('node show %s' % node_name, always_run=True),
            print_to_table
        )


@task
def add(host_name, node_name=None, *accessible_databag_item_patterns):
    """
    Add Node to current Environment.

    Example)
      Add node with same name as host in Environment prod.
      $ fab chefenv:prod node.add:foobar.example.com

      Add node with specified name in Environment prod.
      $ fab chefenv:prod node.add:foobar.example.com,foobar

      Add node with same name as host in Environment prod, and  grant access to DataBag items*_prod.
      $ fab chefenv:prod node.add:foobar.example.com,None,".*_prod"

    :param host_name: Host name of node to be added.
    :param node_name: Node name. Use host name if specified None.  (Default Use host_name as node name)
    :param accessible_databag_item_patterns: DataBag item(s) accessed from added node.(Can use regex) (Default nothing)
    """
    _node_name = node_name if node_name and node_name != 'None' else host_name

    print(green("Adding Node %s(Host=%s) in Environment %s..." % (_node_name, host_name, env.ChefEnv)))
    printt(
        knife3(
            'bootstrap %s --sudo --ssh-user=`whoami` --node-name=%s --environment=%s' %
            (host_name, _node_name, env.ChefEnv)
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
                printt(knife3('vault update %s %s -C "%s"' % (databag_name, item_name, _node_name)))
        else:
            print(yellow(
                "No DataBag item matches the specified pattern %s." %
                ", ".join(accessible_databag_item_patterns)
            ))

    if not env.DryRun:
        show(_node_name)
