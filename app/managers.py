# -*- coding: utf-8 -*-
from typing import Type

from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: str,
        **extra_fields: dict,
    ) -> Type:

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(
        self,
        email: str,
        password: str,
        **extra_fields: dict,
    ) -> Type:

        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields: dict,
    ) -> Type:

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser must be set to True')

        return self._create_user(email, password, **extra_fields)
