# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.colors import yellow

from fabricchef.api import *


@task
def conf(knife_conf_path='./.chef/knife.rb'):
    """
    Specify path of Knife config file.(Default ./chef/knife.rb)

    :param knife_conf_path: Kinife config file path.
    """
    env.KnifeConfPath = knife_conf_path
    print(yellow("Using Knife configuration file %s." % env.KnifeConfPath))


# TODO Supports table layout.
@task
def output(output_format='text'):
    """
    Specify output format. (text|json) (Default text)

    :param output_format: Output format.
    """
    env.OutputFormat = output_format


@task
def chefenv(chef_env):
    """
    Specify Environment for current use.(Default dev)

    :param chef_env: Environment.
    """
    env.ChefEnv = chef_env
    print(yellow("Set current Chef Environment to %s." % env.ChefEnv))


@task
def dryrun():
    """
    Enable Dry-Run mode. Do NOT update anything.
    """
    print("")
    print(red("!!!!! DRY-RUN mode !!!!!"))
    print("")
    env.DryRun = True
