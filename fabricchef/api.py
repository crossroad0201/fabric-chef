# -*- coding: utf-8 -*-

from __future__ import print_function

import json

from fabric.api import *
from fabric.colors import red
from flatten_json import flatten
from prettytable import PrettyTable

env.KnifeConfPath = None
env.OutputFormat = 'table'
env.RryRun = False


def knife(command_and_option, always_run=False):
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


def print_dict_as_flat_table(knife_output):
    j = json.loads(knife_output)
    table = PrettyTable(["Key", "Value"])
    table.align["Key"] = 'l'
    table.align["Value"] = 'l'
    for key, value in sorted(flatten(j, '.').items()):
        table.add_row([key, value])
    print(table)
    print("%s item(s)" % len(j))


def printf(fn_knife,
           as_table,
           as_text=('text', lambda s: print(s)),
           as_json=('json', lambda s: print(s)),
           as_flat=('json', print_dict_as_flat_table)
           ):
    def decorator_for(output_format):
        if output_format == 'json':
            return as_json[0], as_json[1]
        elif output_format == 'table':
            return as_table[0], as_table[1]
        elif output_format == 'flat':
            return as_flat[0], as_flat[1]
        else:
            return as_text[0], as_text[1]

    (knife_format, decorate_and_print) = decorator_for(env.OutputFormat)
    result = fn_knife(knife_format)
    decorate_and_print(result)


def printt(fn_knife):
    print(fn_knife('text'))
