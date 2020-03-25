# -*- coding: utf-8 -*-
"""
Fabric tasks for Chef operations.

Use $ fab -l command to show all available tasks,
and You can see task detail using -d option like this $ fab -d node.add.
"""

from __future__ import print_function

from fabric.api import *

from fabricchef.api import *
from fabricchef.tasks.common import *
import fabricchef.tasks.chefenv as chefenv
import fabricchef.tasks.role as role
import fabricchef.tasks.vault as vault
import fabricchef.tasks.node as node
import fabricchef.tasks.recipe as recipe


@task
def init_chef_repo(user, client_key_path, editor='vim'):
    """
    Init this directory as chef repository.

    :param user: Chef user.
    :param client_key_path: Your private key file path.
    :param editor: Editor you use. (Default vim)
    """
    create_chef_repo("https://example.com", "example", user, client_key_path, editor)
