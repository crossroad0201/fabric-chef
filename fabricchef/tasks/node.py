# -*- coding: utf-8 -*-

from __future__ import print_function

import itertools as itr
import re

from fabric.colors import green, blue, yellow

from fabricchef.api import *
from fabricchef.tasks.vault import get_exists_vault_item_names, parse_vault_item_name

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

        table = PrettyTable(["NodeName", "Platform", "FQDN", "IP Address", "Uptime", "Environment", "Tag", "RunList"])
        table.align["NodeName"] = 'l'
        table.align["Platform"] = 'l'
        table.align["FQDN"] = 'l'
        table.align["IP Address"] = 'l'
        table.align["Uptime"] = 'l'
        table.align["Environment"] = 'l'
        table.align["Tag"] = 'l'
        table.align["RunList"] = 'l'
        for i in sorted(j['rows'], key=lambda x: x['name']):
            a = i['automatic']
            if 'fqdn' in a:
                table.add_row([
                    i['name'],
                    "%s(%s)" % (a['platform'], a['platform_version']),
                    a['fqdn'],
                    a['ipaddress'],
                    a['uptime'],
                    i['chef_environment'],
                    ",".join(i['normal']['tags']) if i['normal']['tags'] else "",
                    ",".join(i['run_list'])
                ])
            else:
                table.add_row([
                    i['name'],
                    "",
                    "",
                    "",
                    "Unknown",
                    "",
                    "",
                    ""
                ])

        print(table)
        print("%s Node(s)" % len(j['rows']))

    query = '"chef_environment:%s"' % chef_env if chef_env else ''
    printf(
        knife('search node %s' % query, always_run=True),
        ('json', print_table)
    )


@task
def show(node_name):
    """
    Show Node.

    :param node_name: Node name.
    """
    def print_table(knife_output):
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
        table1.add_column("Tag", [",".join(j['normal']['tags'])], 'l')
        table1.add_column("RunList", [",".join(j['run_list'])], 'l')
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

    printf(
        knife('node show %s -l' % node_name, always_run=True),
        ('json', print_table)
    )


@task(alias='bootstrap')
def add(chef_env, host_name, **kwargs):
    """
    Add(Bootstrap) Node to current Environment.

    Example)
      Add node with same name as host in Environment prod.
      $ fab node.add:prod,foobar.example.com

      Add node with specified name in Environment prod.
      $ fab node.add:prod,foobar.example.com,node_name=foobar

      Grant access to Vault items '*_prod', and create tag 'foo' and 'bar'.
      $ fab node.add:prod,foobar.example.com,None,vaults=".*_prod",tags="foo bar"

    :param chef_env: Add to Chef Environment.
    :param host_name: Host name of node to be added.
    :param kwargs: Options.
        node_name - Node name. (Default Use host_name as node name)
        vaults    - Vault item(s) accessed. Space separated values. Can use regex.
        tags      - Tag(s). Space separated values.
    """
    _node_name = kwargs['node_name'] if 'node_name' in kwargs else host_name

    print(green("Adding Node %s(Host=%s) in Environment %s..." % (_node_name, host_name, chef_env)))
    printt(
        knife(
            'bootstrap %s --sudo --ssh-user=`whoami` --node-name=%s --environment=%s' %
            (host_name, _node_name, chef_env)
        )
    )

    if 'vaults' in kwargs:
        print(green("Retrieving existing Vault items..."))
        exists_vault_item_names = get_exists_vault_item_names()

        vaults = kwargs['vaults']
        vault_item_names_tobe_access = set()
        for p, i in itr.product([re.compile(x.strip()) for x in vaults.split(' ')], exists_vault_item_names):
            if p.match(i):
                vault_item_names_tobe_access.add(i)

        if vault_item_names_tobe_access:
            for i in vault_item_names_tobe_access:
                print(green("Grant access to Vault item %s..." % i))
                (vault_name, item_name) = parse_vault_item_name(i)
                printt(knife('vault update %s %s -C "%s"' % (vault_name, item_name, _node_name)))
        else:
            print(yellow(
                "No Vault item matches the specified pattern %s." %
                ", ".join(vaults)
            ))

    if 'tags' in kwargs:
        tags = kwargs['tags']
        add_tag(_node_name, tags)

    if not env.DryRun:
        show(_node_name)


@task
def add_tag(node_name, *args):
    """
    Add tag(s) to specified Node.

    Example)
      $ fab add_tag:foobar.example.com,foo,bar

    :param node_name: Node name.
    :param args: Tag(s).
    """
    space_separated_tags = ' '.join(args)
    print(green("Adding tag(s) %s to node %s..." % (space_separated_tags, node_name)))
    printt(knife('tag create %s %s' % (node_name, space_separated_tags)))


@task
def delete_tag(node_name, *args):
    """
    Delete tas(s) from specified Node.

    :param node_name: Node name.
    :param args: Tag(s).
    """
    space_separated_tags = ' '.join(args)
    print(green("Deleting tag(s) %s to node %s..." % (space_separated_tags, node_name)))
    printt(knife('tag delete %s %s' % (node_name, space_separated_tags)))
