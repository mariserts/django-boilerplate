# -*- coding: utf-8 -*-
ACL_CONFIG = {
    'admin': {
        'can_cascade_permissions': True,
        'code': 'admin',
        'default': False,
        'ignore_permissions': True,
        'name': 'Admin',
    },
    'editor': {
        'can_cascade_permissions': True,
        'code': 'editor',
        'default': False,
        'ignore_permissions': False,
        'name': 'Editor',
    },
    'user': {
        'can_cascade_permissions': False,
        'code': 'user',
        'default': True,
        'ignore_permissions': False,
        'name': 'User',
    },
}


CACHE_KEY_TENANT_GRAPH_NODES = 'tenant_graph_nodes'


CASCADE_ACCESS = True
