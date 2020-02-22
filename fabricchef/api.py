# -*- coding: utf-8 -*-

from __future__ import print_function

import json

from fabric.api import *
from fabric.colors import red, green
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


def shorten(value, slen, elen):
    if value:
        s = value if type(value) == unicode else str(value) 
        if len(s) <= (slen + elen):
            return s
        else:
            if slen < 1:
                return '..%s' % s[len(s) - elen + 2:len(s)]
            elif elen < 1:
                return '%s..' % s[0:slen - 2]
            else:
                return '%s..%s' % (s[0:slen - 1], s[len(s) - elen + 1:len(s)])
    else:
        return value


def print_dict_as_flat_table(dict_value):
    table = PrettyTable(["Key", "Value"])
    table.align["Key"] = 'l'
    table.align["Value"] = 'l'
    for key, value in sorted(flatten(dict_value, '.').items()):
        table.add_row([shorten(key, 95, 5), shorten(value, 95, 5)])
    print(table)
    print("%s item(s)" % len(dict_value))


def printf(fn_knife,
           as_table,
           as_text=('text', lambda s: print(s)),
           as_json=('json', lambda s: print(s)),
           as_flat=('json', lambda s: print_dict_as_flat_table(json.loads(s)))
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


def create_chef_repo(chef_server, chef_org, chef_user, client_key_path, editor="vim", repo_dir="."):
    """
    Create Chef repository.

    Ex)
    $ fab create_chef_repo:https://example.com,test-org,scott,~/private_key.pem,emacs

    /example
      /.chef
        knife.rb
        scott.pem

    :param chef_server: Chef server. Like this "https://example.com"
    :param chef_org: Chef Organization.
    :param chef_user: Your Chef user name.
    :param client_key_path: Path for your private key(*.pem) file. Will be copy under chef repository directory.
    :param editor: Editor you use. (Default vim)
    :param repo_dir: Target directory. (Default current directory)
    """

    knife_rb = '''
current_dir = File.dirname(__FILE__)

log_level                :info
log_location             STDOUT
node_name                "%(User)s"
client_key               "#{current_dir}/%(User)s.pem"
chef_server_url          "%(ChefServer)s/organizations/%(Organization)s"
cookbook_path            ["#{current_dir}/../cookbooks"]

knife[:vault_mode] = 'client'
knife[:editor] = '/usr/bin/%(Editor)s'
    '''.strip() % dict(
        ChefServer=chef_server,
        Organization=chef_org,
        User=chef_user,
        Editor=editor
    )

    print(green("Create Chef repository to %s/.chef..." % repo_dir))
    local('mkdir -p %s/.chef' % repo_dir)
    local('cat << EOF > %s/.chef/knife.rb\n%s\nEOF' % (repo_dir, knife_rb))
    local('cp %s %s/.chef/%s.pem' % (client_key_path, repo_dir, chef_user))
