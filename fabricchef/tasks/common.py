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


@task
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
    local('mkdir %s/.chef' % repo_dir)
    local('cat << EOF > %s/.chef/knife.rb\n%s\nEOF' % (repo_dir, knife_rb))
    local('cp %s %s/.chef/%s.pem' % (client_key_path, repo_dir, chef_user))
