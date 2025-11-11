
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