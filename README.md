Fabric Chef
====

Useful [Fabric](http://www.fabfile.org/installing-1.x.html) tasks for
[Chef](https://www.chef.io/) operations.

# Requirement

* Python 2.7.x (Do NOT support Python 3.x)
* Chef Workstation 

# Getting started

## Install

```
$ pip install git+https://github.com/crossroad0201/fabric-chef.git [-U]
```

## Create fabfile.py

```python
# -*- coding: utf-8 -*-

from __future__ import print_function

# Import required fabchef members. (Must be use from-import syntax.)
from fabricchef.api import *
from fabricchef.tasks.common import *

# Import Fabric tasks for Chef component you want to operate. (Must be use import syntax.
import fabricchef.tasks.env as env
import fabricchef.tasks.role as role
import fabricchef.tasks.databag as databag
import fabricchef.tasks.node as node
import fabricchef.tasks.recipe as recipe
```

## Run

```
$ fab env.list
-> Should be show all Chef Environments in your Chef Organization.
```

# Usage

### Run Fabric Tasks 

* Execute single command. 
  ```
  $ fab env.list
  ```

* Execute multiple commands.(Sequential)
  ```
  $ fab env.list databag.list
  ```

* Execute command with specified Chef Envitonment.
  ```
  $ fab chefenv:prod_ssk env.show
  ```

* Execute command in DRY-RUN mode.
  ```
  $ fab dryrun chefenv:prod_ssk recipe.run:foobar.example.com,"role[install]"
  ```

* Execute command with specified Knife config.
  ```
  $ fab conf:foobar/.chef/knife.rb env.list
  ```

* Output command execution result in JSON format.
  ```
  $ fab output:json env.list
  ```

* Using some options.
  ```
  $ fab conf:foobar/.chef/knife.rb output:json chefenv:prod_kks node.list
  ```

### Available Tasks

Use `$ fab -l` command to show all available tasks.

```
$ fab -l

Available commands:

    chefenv        Specify Environment for current use.(Default dev)
    conf           Specify path of Knife config file.(Default ./chef/knife.rb...
    dryrun         Enable Dry-Run mode. Do NOT update anything.
    output         Specify output format. (text|json) (Default text)
    databag.apply  Create DataBag item. (and grant admin permission)
    databag.list   List all DataBag items.
    databag.show   Show DataBag item.
    env.apply      Create or Update Environment(s) from specified path(dir or...
    env.list       List all Environments in Organization.
    env.show       Show current Environment.
    node.add       Add Node to current Environment.
    node.list      List Nodes in current Environment.
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
      $ fab chefenv:prod_ssk add_node:foobar.example.com

      Add node with specified name in Environment prod_ssk.
      $ fab chefenv:prod_ssk add_node:foobar.example.com,foobar

      Add node with same name as host in Environment prod_ssk, and  grant access to DataBag items*_prod.
      $ fab chefenv:prod_ssk add_node:foobar.example.com,None,".*_prod"

    :param host_name: Host name of node to be added.
    :param node_name: Node name. Use host name if specified None.  (Default Use host_name as node name)
    :param accessible_databag_item_patterns: DataBag item(s) accessed from added node.(Can use regex) (Default nothing)

    Arguments: host_name, node_name=None
```
  
## API

TBD

  