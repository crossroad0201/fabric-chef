# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.api import *
from fabric.colors import green,blue,yellow,red

from fabricchef.api import *

@task
def run(node_name, *run_lists):
    """
    Run recipe(s) on specified node.

    Example)
      $ fab chefenv:prod run_recipe:foobar.example.com,"role[install]","role[start]"

    :param node_name: Run on this node.
    "param run_lists: Recipe(s) to run.
    """
    print(green("Running recipe(s) %s on the node %s..." % (",".join(run_lists), node_name)))
    if env.DryRun:
        knife('ssh \'name:%s\' \'sudo chef-client --override-runlist "%s" --why-run\'' % (node_name, ",".join(run_lists)), always_run=True)
    else:
        knife('ssh \'name:%s\' \'sudo chef-client --override-runlist "%s"\'' % (node_name, ",".join(run_lists)), always_run=True)
