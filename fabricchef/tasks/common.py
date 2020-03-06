# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.colors import yellow, green

from fabricchef.api import *


@task
def conf(knife_conf_path='./.chef/knife.rb'):
    """
    Specify path of Knife config file.(Default ./chef/knife.rb)

    :param knife_conf_path: knife config file path.
    """
    env.KnifeConfPath = knife_conf_path
    print(yellow("Using Knife configuration file %s." % env.KnifeConfPath))


@task
def output(output_format):
    """
    Specify output format. (table|text|json|flat) (Default table)

    :param output_format: Output format.
    """
    env.OutputFormat = output_format


@task
def dryrun():
    """
    Enable Dry-Run mode. Do NOT update anything.
    """
    print("")
    print(red("!!!!! DRY-RUN mode !!!!!"))
    print("")
    env.DryRun = True


@tssk
def sudopass(sudo_password):
    """
    Set sudo password for 'knife ssh' command. (CAUTION Visible your password on console log)

    If set sudo password via this task, will be not prompt sudo password at every sudo command.

    :param sudo_password: sudo password.
    """
    env.SudoPassword = sudo_password
