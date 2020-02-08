# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.colors import green

from fabricchef.api import *


@task
def run(node_name, *run_lists):
    """
    Run recipe(s) on specified node.

    Example)
      $ fab run_recipe:foobar.example.com,"role[install]","role[start]"

    :param node_name: Run on this node.
    :param run_lists: Recipe(s) to run.
    """
    print(green("Running recipe(s) %s on the node %s..." % (",".join(run_lists), node_name)))
    if env.DryRun:
        printt(
            knife(
                'ssh \'name:%s\' \'sudo chef-client --override-runlist "%s" --why-run\'' %
                (node_name, ",".join(run_lists)),
                always_run=True
            )
        )
    else:
        printt(
            knife(
                'ssh \'name:%s\' \'sudo chef-client --override-runlist "%s"\'' %
                (node_name, ",".join(run_lists)),
                always_run=True
            )
        )
