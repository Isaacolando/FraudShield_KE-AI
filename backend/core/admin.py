
from django.contrib import admin
from .models import Entity,Bill,Allocation,Disbursement,Transaction,EvidenceDocument,Flag, County

admin.site.register(Entity)
admin.site.register(Bill)
admin.site.register(Allocation)
admin.site.register(Disbursement)
admin.site.register(Transaction)
admin.site.register(EvidenceDocument)
admin.site.register(Flag)
admin.site.register(County)