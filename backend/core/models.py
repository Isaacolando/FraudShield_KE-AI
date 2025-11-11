
from django.db import models
try:
    # For older Django versions (<3.1) that provide JSONField in contrib.postgres
    from django.contrib.postgres.fields import JSONField
except ImportError:
    # For Django 3.1+ use the JSONField on models
    JSONField = models.JSONField

class Entity(models.Model):
    ENTITY_TYPES = [('county','county'),('vendor','vendor'),('mp','mp'),('bank','bank'),('telco','telco')]
    name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.entity_type})"

class Bill(models.Model):
    bill_id = models.CharField(max_length=100, unique=True)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    purpose = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.bill_id

class Allocation(models.Model):
    allocation_id = models.CharField(max_length=100, unique=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    to_entity = models.ForeignKey(Entity, related_name='allocations', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date_allocated = models.DateField()
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.allocation_id

class Disbursement(models.Model):
    disbursement_id = models.CharField(max_length=100, unique=True)
    allocation = models.ForeignKey(Allocation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    to_entity = models.ForeignKey(Entity, related_name='disbursements', on_delete=models.CASCADE)
    date = models.DateField()
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.disbursement_id

class Transaction(models.Model):
    tx_id = models.CharField(max_length=100, unique=True)
    source_entity = models.ForeignKey(Entity, related_name='outgoing', on_delete=models.CASCADE)
    dest_entity = models.ForeignKey(Entity, related_name='incoming', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    timestamp = models.DateTimeField()
    tx_type = models.CharField(max_length=50)  # 'mpesa','bank','cheque'
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.tx_id

class EvidenceDocument(models.Model):
    doc_id = models.CharField(max_length=100, unique=True)
    # in full impl use GenericForeignKey; scaffold uses optional links
    related_allocation = models.ForeignKey(Allocation, on_delete=models.SET_NULL, null=True, blank=True)
    related_disbursement = models.ForeignKey(Disbursement, on_delete=models.SET_NULL, null=True, blank=True)
    related_transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='evidence/', null=True, blank=True)
    text_extracted = models.TextField(blank=True)
    ocr_fields = models.JSONField(default=dict, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.doc_id

class Flag(models.Model):
    flag_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    severity = models.IntegerField(default=3)  # scale 1-5
    reason = models.TextField()
    evidence = models.JSONField(default=dict, blank=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.flag_id