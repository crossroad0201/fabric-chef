# -*- coding: utf-8 -*-

from __future__ import print_function

from fabric.api import *
from fabric.colors import red

env.KnifeConfPath = None
env.OutputFormat = 'text'  # FIXME デフォルトをtableに
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


def knife3(command_and_option, always_run=False):
    def fn_knife(knife_format):
        conf_option = '-c 5s' % env.KnifeConfPath if env.KnifeConfPath else ''
        # FIXME
        if not always_run and False: #env.DryRun:
            print(red('DRY-RUN: ') + 'knife %s %s' % (command_and_option, conf_option))
            return '{}'
        else:
            if knife_format  == 'text':
                return local('knife %s %s' % (command_and_option, conf_option), capture=True)
            else:
                return local('knife %s -F %s %s' % (command_and_option, knife_format, conf_option), capture=True)

    return fn_knife


def printf(fn_knife, print_to_table):
    def decorator_for(output_format):
        if output_format == 'json':
            return 'json', lambda s: print(s)
        elif output_format == 'table':
            return 'json', lambda s: print_to_table(s)
        else:
            return 'text', lambda s: print(s)

    (knife_format, decorate_and_print) = decorator_for(env.OutputFormat)
    result = fn_knife(knife_format)
    decorate_and_print(result)


def printt(fn_knife):
    print(fn_knife('text'))
