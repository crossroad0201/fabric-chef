# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.api import *
from fabric.colors import red

env.KnifeConfPath = None
env.OutputFormat = 'text'
env.ChefEnv = 'dev'
env.RryRun = False


def knife(command_and_option, output_format=None, capture=False, always_run=False):
    conf_option = '-c 5s' % env.KnifeConfPath if env.KnifeConfPath else ''

    if not always_run and env.DryRun:
        print(red('DRY-RUN: ') + 'knife %s %s' % (command_and_option, conf_option))
        return '{}'
    else:
        __output_format = output_format if output_format else env.OutputFormat
        if __output_format == 'text':
            return local('knife %s %s' % (command_and_option, conf_option), capture=capture)
        else:
            return local('knife %s -F %s %s' % (command_and_option, __output_format, conf_option), capture=capture)
