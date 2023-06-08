# -*- coding: utf-8 -*-
from django.conf import settings as dj_settings

from . import constants


class Settings:

    @property
    def CASCADE_ACCESS(self):
        return getattr(dj_settings, 'CASCADE_ACCESS', constants.CASCADE_ACCESS)


settings = Settings()
