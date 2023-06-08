# -*- coding: utf-8 -*-
import networkx as nx
import uuid

from typing import List

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db import models

from . import constants
from .conf import settings
from .managers import CustomUserManager


def get_acl_choices() -> List[List[str]]:

    choices = []

    for key, value in constants.ACL_CONFIG.items():
        choices.append([value['code'], value['name']])

    return choices


def get_acl_default_choice():

    for key, value in constants.ACL_CONFIG.items():
        if value['default'] is True:
            return value['code']


class DateTimeStampedMixin(models.Model):

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UUIDStampedMixin(models.Model):

    class Meta:
        abstract = True

    id = models.UUIDField(
        primary_key=True,
        editable=False,
        unique=True,
        default=uuid.uuid4
    )


class User(
    AbstractUser,
    UUIDStampedMixin
):

    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(
        self,
        *args: List,
        **kwargs: dict,
    ) -> None:

        self.email = self.email.lower()
        self.username = self.email

        super(User, self).save(*args, **kwargs)

    def get_all_tenants(self) -> List:
        return []

    @staticmethod
    def has_tenant_access(
        tenant_id: str,
        user_id: str,
        acl: str,
        cascade: bool = settings.CASCADE_ACCESS
    ) -> bool:

        acl_conf = constants.ACL_CONFIG.get(acl, None)
        if acl_conf is None:
            return False

        if acl_conf.get('ignore_permissions', False) is True:
            return True

        can_cascade_permissions = acl_conf.get(
            'can_cascade_permissions',
            False
        )

        tenant_access = TenantUser.objects.filter(
            tenant_id=tenant_id,
            user_id=user_id,
        ).first()

        if cascade is False or can_cascade_permissions is False:
            return tenant_access is not None

        if tenant_access is not None:
            return True

        parents = Tenant.get_tenant_predecessors(tenant_id)
        if not parents:
            return False

        return TenantUser.objects.filter(
            tenant_id__in=parents,
            user_id=user_id,
        ).exists()


class Tenant(
    UUIDStampedMixin,
    DateTimeStampedMixin,
    models.Model
):

    parent = models.ForeignKey(
        'Tenant',
        related_name='children',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)

    def save(
        self,
        *args: List,
        **kwargs: dict,
    ) -> None:

        super(Tenant, self).save(*args, **kwargs)

        cache.set(
            Tenant.get_graph_nodes(),
            constants.CACHE_KEY_TENANT_GRAPH_NODES
        )

    @staticmethod
    def get_graph_nodes() -> List[List[str]]:

        nodes = []

        for tenant in Tenant.objects.filter(parent__isnull=False):
            nodes.append([str(tenant.parent_id), str(tenant.id)])

        return nodes

    @staticmethod
    def get_graph() -> nx.DiGraph:

        nodes = cache.get(constants.CACHE_KEY_TENANT_GRAPH_NODES, None)

        if nodes is None:
            nodes = Tenant.get_graph_nodes()
            cache.set(nodes, constants.CACHE_KEY_TENANT_GRAPH_NODES)

        G = nx.DiGraph()

        for node in nodes:
            G.add_edge(node[0], node[1])

        return G

    @staticmethod
    def get_tenant_decendants(tenant_id: str) -> List[str]:

        G = Tenant.get_graph()

        try:
            x = list(G.decendants(tenant_id))
        except nx.exception.NetworkXError:
            return []

        return x

    @staticmethod
    def get_tenant_predecessors(tenant_id: str) -> List[str]:

        G = Tenant.get_graph()

        try:
            x = list(
                map(
                    lambda node:
                        node[0],
                        list(nx.edge_dfs(G, tenant_id, orientation='reverse'))
                )
            )
        except nx.exception.NetworkXError:
            return []

        return x


class TenantUser(
    UUIDStampedMixin,
    DateTimeStampedMixin,
    models.Model
):

    class Meta:
        unique_together = ('tenant', 'user')

    tenant = models.ForeignKey(
        Tenant,
        related_name='users',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name='tenants',
        on_delete=models.CASCADE
    )
    acl = models.CharField(
        max_length=100,
        choices=get_acl_choices(),
        default=get_acl_default_choice()
    )
