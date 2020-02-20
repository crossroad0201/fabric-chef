Fabric Chef
====

Useful [Fabric](http://www.fabfile.org/installing-1.x.html) tasks for
[Chef](https://www.chef.io/) operations.

Chef `knife` command is too primitive, so many commands have to execute.

This library is wrapper for the Chef `knife` command and provide useful tasks for Chef operation in Command-Line interface.

```
$ fab node.list:prod
[localhost] local: knife search node "chef_environment:prod" -F json
+-----------------+------------------+-----------------+-----------------+---------------------------------------+-------------+---------+
| NodeName        | Platform         | FQDN            | IP Address      | Uptime                                | Environment | RunList |
+-----------------+------------------+-----------------+-----------------+---------------------------------------+-------------+---------+
| foo.example.com | centos(7.6.1810) | foo.example.com | ***.***.***.*** | 4 hours 22 minutes 57 seconds         | prod        | []      |
| bar.example.com | centos(7.6.1810) | bar.example.com | ***.***.***.*** | 7 days 00 hours 34 minutes 23 seconds | prod        | []      |
+-----------------+------------------+-----------------+-----------------+---------------------------------------+-------------+---------+
2 Node(s)

Done.

$ fab node.show:foo.example.com,show_all_attrs=True
[localhost] local: knife node show foo.example.com -l -F json
Node:
+-----------------+------------------+-----------------+-----------------+-------------------------------+-------------+---------+
| NodeName        | Platform         | FQDN            | IP Address      | Uptime                        | Environment | RunList |
+-----------------+------------------+-----------------+-----------------+-------------------------------+-------------+---------+
| foo.example.com | centos(7.6.1810) | foo.example.com | ***.***.***.*** | 4 hours 22 minutes 57 seconds | prod        | []      |
+-----------------+------------------+-----------------+-----------------+-------------------------------+-------------+---------+
Device:
+-----------+-----------------------+----------------------+
| CPU Cores |     Memory Free/Total | Disk Free/Total (KB) |
+-----------+-----------------------+----------------------+
|         4 | 5108128kB / 6109324kB |  17788140 / 20959212 |
+-----------+-----------------------+----------------------+

Done.
```

# Requirement

* Python 2.7.x (Do NOT support Python 3.x.)
* Chef Workstation (`knife` command) 

# Getting started

## Install

```
$ pip install git+https://github.com/crossroad0201/fabric-chef.git [-U]
```

## Recommended directory structure

Put the Fabric script file called 'fabfile.py' in your chef repository.

```
/[Your Chef repository]
  +- /.chef
  |    +- knife.rb
  |    +- [Your private key].pem
  +- /environments
  |    +- dev.json
  |    +- prod.json
  |    :
  +- /roles
  |    +- deploy.json
  |    +- restart.json
  |    :
  +- fabfile.py
```

## Create fabfile.py

`fabfile.py` is Python script file for define the Fabric tasks.

You will be available the tasks for Chef operation by import this library. 

```python
# -*- coding: utf-8 -*-

from __future__ import print_function

# Import required fabric-chef members. (Must be use from-import syntax.)
from fabricchef.api import *
from fabricchef.tasks.common import *

# Import Fabric tasks for Chef component you want to operate. (Must be use import syntax.
import fabricchef.tasks.env as env
import fabricchef.tasks.role as role
import fabricchef.tasks.vault as vault
import fabricchef.tasks.node as node
import fabricchef.tasks.recipe as recipe

# You can add any custom tasks for this Chef repository. 
@task
def custom_task():
  print('Hello.')
```

## Run

Run `fab` command with any task.

```
$ fab env.list
-> Should be show all Chef Environments in your Chef Organization.
```

# Usage

### Basic usage

* Execute single command. 
  ```
  $ fab env.list
  ```

* Execute multiple commands.(Execute sequentially)
  ```
  $ fab env.list vault.list
  ```

* Dry-Run.
  ```
  $ fab dryrun recipe.run:foobar.example.com,"role[install]"
  ```

* Specify knife config.
  ```
  $ fab conf:foobar/.chef/knife.rb env.list
  ```

* Specify output format os json.(Available table, text, json and flat)
  ```
  $ fab output:json env.list
  ```

* Combining some options.
  ```
  $ fab conf:foobar/.chef/knife.rb output:json node.list:prod
  ```

### Available Tasks

Use `$ fab -l` command to show all available tasks.

```
$ fab -l

Available commands:

    conf           Specify path of Knife config file.(Default ./chef/knife.rb...
    dryrun         Enable Dry-Run mode. Do NOT update anything.
    output         Specify output format. (table|text|json|flat) (Default table)
    vault.apply    Create Vault item. (and grant admin permission)
    vault.list     List all Vault items.
    vault.show     Show Vault item.
    env.apply      Create or Update Environment(s) from specified path(dir or...
    env.list       List all Environments in Organization.
    env.show       Show current Environment.
    node.add       Add Node to current Environment.
    node.list      List Nodes in specified Environment.
    node.show      Show Node.
    recipe.run     Run recipe(s) on specified node.
    role.apply     Create or Update Role(s) from specified path(dir or file).
    role.list      List all Roles in Organization.
```

And You can see task detail using -d option like this `$ fab -d node.add`.

```
$ fab -d node.add
Displaying detailed information for task 'node.add':

    Add Node to current Environment.

    Example)
      Add node with same name as host in Environment prod_ssk.
      $ fab add_node:prod,foobar.example.com

      Add node with specified name in Environment prod_ssk.
      $ fab add_node:prod,foobar.example.com,foobar

      Add node with same name as host in Environment prod_ssk, and  grant access to Vault items*_prod.
      $ fab add_node:prod,foobar.example.com,None,".*_prod"

    :param chef_env: Add to Chef Environment.
    :param host_name: Host name of node to be added.
    :param node_name: Node name. Use host name if specified None.  (Default Use host_name as node name)
    :param accessible_vault_item_patterns: Vault item(s) accessed from added node.(Can use regex) (Default nothing)

    Arguments: chef_env, host_name, node_name=None
```
