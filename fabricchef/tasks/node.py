# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.api import *
from fabric.colors import green,blue,yellow,red

from fabricchef.api import *
from fabricchef.tasks.databag import get_exists_databag_item_names,parse_databag_item_name

import re
import itertools as itr

@task
def list():
    """
    List Nodes in current Environment.
    """
    knife('search node "chef_environment:%s"' % env.ChefEnv, always_run=True)

@task
def show(node_name, show_all_attrs='False'):
    """
    Show Node.

    :param node_name: Node name.
    :param show_all_attrs: Show all attributes.(True|False) (Default False)
    """
    if show_all_attrs in ('True', 'true', 'yes'):
        knife('node show %s -l' % node_name, always_run=True)
    else:
        knife('node show %s' % node_name, always_run=True)

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
    knife('bootstrap %s --sudo --ssh-user=`whoami` --node-name=%s --environment=%s' % (host_name, _node_name, env.ChefEnv))

    if accessible_databag_item_patterns:
        print(green("Retrieving existing DataBag items..."))
        exists_databag_item_names = get_exists_databag_item_names()

        databag_item_names_tobe_access = set()
        for p,i in itr.product([re.compile(x) for x in accessible_databag_item_patterns], exists_databag_item_names):
            if p.match(i):
                databag_item_names_tobe_access.add(i)

        if databag_item_names_tobe_access:
            for i in databag_item_names_tobe_access:
                print(green("Grant access to DataBag item %s..." % i))
                (databag_name, item_name) = parse_databag_item_name(i)
                knife('vault update %s %s -C "%s"' % (databag_name, item_name, _node_name))
        else:
            print(yellow("No DataBag item matches the specified pattern %s." % ", ".join(accessible_databag_item_patterns)))

    if not env.DryRun:
        show(_node_name)
