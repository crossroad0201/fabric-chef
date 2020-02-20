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
import fabricchef.tasks.env as env
import fabricchef.tasks.role as role
import fabricchef.tasks.vault as vault
import fabricchef.tasks.node as node
import fabricchef.tasks.recipe as recipe
