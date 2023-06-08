# -*- coding: utf-8 -*-
from django.test import TestCase

from .. import constants
from ..models import Tenant, TenantUser, User


class TenantAccessTestCase(TestCase):

    def setUp(self) -> None:

        self.test_admin = User.objects.create(
            email='admin@testcase.com'
        )
        self.test_editor = User.objects.create(
            email='editor@testcase.com'
        )
        self.test_user = User.objects.create(
            email='user@testcase.com'
        )

        self.tenant_a = Tenant.objects.create(
            name='a'
        )
        self.tenant_aa = Tenant.objects.create(
            name='aa',
            parent=self.tenant_a
        )
        self.tenant_aaa = Tenant.objects.create(
            name='aaa',
            parent=self.tenant_aa
        )
        self.tenant_aaaa = Tenant.objects.create(
            name='aaaa',
            parent=self.tenant_aaa
        )

        self.tenant_access_editor = TenantUser.objects.create(
            tenant=self.tenant_aa,
            user=self.test_editor,
            acl=constants.ACL_CONFIG['editor']['code']
        )

        self.tenant_access_user = TenantUser.objects.create(
            tenant=self.tenant_aa,
            user=self.test_user,
            acl=constants.ACL_CONFIG['user']['code']
        )

    def tearDown(self) -> None:

        Tenant.objects.all().delete()
        TenantUser.objects.all().delete()
        User.objects.all().delete()

    def test_admin_access(self) -> None:

        acl = constants.ACL_CONFIG['admin']['code']

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_a.id),
                str(self.test_admin.id),
                acl,
                True
            ),
            True
        )

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_aa.id),
                str(self.test_admin.id),
                acl,
                True
            ),
            True
        )

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_aaa.id),
                str(self.test_admin.id),
                acl,
                True
            ),
            True
        )

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_aaaa.id),
                str(self.test_admin.id),
                acl,
                True
            ),
            True
        )

    def test_editor_access(self) -> None:

        acl = constants.ACL_CONFIG['editor']['code']

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_a.id),
                str(self.test_editor.id),
                acl,
                True
            ),
            False
        )

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_aa.id),
                str(self.test_editor.id),
                acl,
                True
            ),
            True
        )

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_aaa.id),
                str(self.test_editor.id),
                acl,
                True
            ),
            True
        )

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_aaaa.id),
                str(self.test_editor.id),
                acl,
                True
            ),
            True
        )

    def test_user_access(self) -> None:

        acl = constants.ACL_CONFIG['user']['code']

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_a.id),
                str(self.test_user.id),
                acl,
                True
            ),
            False
        )

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_aa.id),
                str(self.test_user.id),
                acl,
                True
            ),
            True
        )

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_aaa.id),
                str(self.test_user.id),
                acl,
                True
            ),
            False
        )

        self.assertIs(
            User.has_tenant_access(
                str(self.tenant_aaaa.id),
                str(self.test_user.id),
                acl,
                True
            ),
            False
        )
