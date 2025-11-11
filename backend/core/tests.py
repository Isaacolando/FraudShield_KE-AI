from django.test import TestCase

# FraudShield Django Project Scaffold

This single text document contains a ready-to-copy Django project scaffold. Each file is shown with a header `=== FILE: <path> ===` followed by the file contents. Create the corresponding files locally with the exact paths and contents. 

---

=== FILE: README.md ===
```
# FraudShield - Django Scaffold

Quickstart:
1. Create a Python virtualenv: `python -m venv .venv && source .venv/bin/activate`
2. Install requirements: `pip install -r requirements.txt`
3. Apply migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Run server: `python manage.py runserver`

This scaffold provides a minimal Django + DRF app with models, serializers, basic views and URLs for ingesting transactions, allocations, evidence and listing flags.

To load synthetic data: copy the JSON outputs from earlier replies into `data/` and use `manage.py loaddata` or a custom script.

Next steps: link this API with the React dashboard (will be provided separately).
```

---

=== FILE: requirements.txt ===
```
Django>=4.2
djangorestframework
psycopg2-binary
django-cors-headers
python-dotenv
Pillow
```

---

=== FILE: manage.py ===
```
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fraudshield_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django") from exc
    execute_from_command_line(sys.argv)
```

---

=== FILE: fraudshield_project/__init__.py ===
```
# empty
```

---

=== FILE: fraudshield_project/asgi.py ===
```
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fraudshield_project.settings')
application = get_asgi_application()
```

---

=== FILE: fraudshield_project/wsgi.py ===
```
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fraudshield_project.settings')
application = get_wsgi_application()
```

---

=== FILE: fraudshield_project/settings.py ===
```
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY','django-insecure-secret')
DEBUG = os.getenv('DEBUG','1') == '1'
ALLOWED_HOSTS = ['*']

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fraudshield_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fraudshield_project.wsgi.application'

# Use SQLite for the scaffold (switch to Postgres in production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

=== FILE: fraudshield_project/urls.py ===
```
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

=== FILE: core/__init__.py ===
```
# core app
```

---

=== FILE: core/apps.py ===
```
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
```

---

=== FILE: core/models.py ===
```
from django.db import models
from django.contrib.postgres.fields import JSONField if False else models.JSONField

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
```

---

=== FILE: core/admin.py ===
```
from django.contrib import admin
from .models import Entity,Bill,Allocation,Disbursement,Transaction,EvidenceDocument,Flag

admin.site.register(Entity)
admin.site.register(Bill)
admin.site.register(Allocation)
admin.site.register(Disbursement)
admin.site.register(Transaction)
admin.site.register(EvidenceDocument)
admin.site.register(Flag)
```

---

=== FILE: core/serializers.py ===
```
from rest_framework import serializers
from .models import Entity,Bill,Allocation,Disbursement,Transaction,EvidenceDocument,Flag

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'

class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = '__all__'

class DisbursementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disbursement
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class EvidenceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceDocument
        fields = '__all__'

class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = '__all__'
```

---

=== FILE: core/views.py ===
```
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Entity,Bill,Allocation,Disbursement,Transaction,EvidenceDocument,Flag
from .serializers import EntitySerializer,BillSerializer,AllocationSerializer,DisbursementSerializer,TransactionSerializer,EvidenceDocumentSerializer,FlagSerializer
from django.shortcuts import get_object_or_404
import uuid

class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

class AllocationViewSet(viewsets.ModelViewSet):
    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer

class DisbursementViewSet(viewsets.ModelViewSet):
    queryset = Disbursement.objects.all()
    serializer_class = DisbursementSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class EvidenceViewSet(viewsets.ModelViewSet):
    queryset = EvidenceDocument.objects.all()
    serializer_class = EvidenceDocumentSerializer

class FlagViewSet(viewsets.ModelViewSet):
    queryset = Flag.objects.all().order_by('-created_at')
    serializer_class = FlagSerializer

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        flag = self.get_object()
        flag.resolved = True
        flag.save()
        return Response({'status':'resolved'})

# Lightweight ingest endpoints (bulk-friendly)
from rest_framework.views import APIView

class IngestTransactions(APIView):
    def post(self, request):
        data = request.data if isinstance(request.data, list) else [request.data]
        created = []
        for item in data:
            item.setdefault('tx_id', str(uuid.uuid4()))
            serializer = TransactionSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
        return Response({'created': created}, status=status.HTTP_201_CREATED)

class IngestAllocations(APIView):
    def post(self, request):
        data = request.data if isinstance(request.data, list) else [request.data]
        created = []
        for item in data:
            item.setdefault('allocation_id', str(uuid.uuid4()))
            serializer = AllocationSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
        return Response({'created': created}, status=status.HTTP_201_CREATED)

class IngestEvidence(APIView):
    parser_classes = ()
    def post(self, request):
        # Simple handling for scaffold: expects multipart/form-data with file + related ids
        data = request.data
        data_dict = data.copy()
        data_dict.setdefault('doc_id', str(uuid.uuid4()))
        serializer = EvidenceDocumentSerializer(data=data_dict)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

---

=== FILE: core/urls.py ===
```
from django.urls import path, include
from rest_framework import routers
from .views import EntityViewSet,BillViewSet,AllocationViewSet,DisbursementViewSet,TransactionViewSet,EvidenceViewSet,FlagViewSet,IngestTransactions,IngestAllocations,IngestEvidence

router = routers.DefaultRouter()
router.register(r'entities', EntityViewSet)
router.register(r'bills', BillViewSet)
router.register(r'allocations', AllocationViewSet)
router.register(r'disbursements', DisbursementViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'evidence', EvidenceViewSet)
router.register(r'flags', FlagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('ingest/transactions/', IngestTransactions.as_view(), name='ingest-transactions'),
    path('ingest/allocations/', IngestAllocations.as_view(), name='ingest-allocations'),
    path('ingest/evidence/', IngestEvidence.as_view(), name='ingest-evidence'),
]
```

---

=== FILE: core/migrations/0001_initial.py ===
```
# You can run `python manage.py makemigrations core` to create migrations locally.
# This scaffold omits full migration code. Run makemigrations then migrate after creating files.
```

---

=== FILE: .env.example ===
```
SECRET_KEY=changeme
DEBUG=1
```

---

=== FILE: run_instructions.txt ===
```
1. Create virtualenv and activate
2. pip install -r requirements.txt
3. python manage.py makemigrations
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver

API endpoints available at http://127.0.0.1:8000/api/

