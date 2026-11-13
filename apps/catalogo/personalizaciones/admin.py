from django.contrib import admin
from apps.core.admin import MasterAdmin
from .models import Diseno

for model in [Diseno]:
    admin.site.register(model, MasterAdmin)

from apps.core.admin import LedgerAdmin
from .models import VersionDiseno, PersonalizacionDetalle, AprobacionDiseno
for model in [VersionDiseno, PersonalizacionDetalle, AprobacionDiseno]:
    admin.site.register(model, LedgerAdmin)
