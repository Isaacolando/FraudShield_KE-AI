
from django.urls import path, include
from rest_framework import routers
from .views import EntityViewSet,BillViewSet,AllocationViewSet,DisbursementViewSet,TransactionViewSet,EvidenceViewSet,FlagViewSet,IngestTransactions,IngestAllocations,IngestEvidence
from django.views.generic import TemplateView
from . import views
from django.contrib.auth import views as auth_views
router = routers.DefaultRouter()
router.register(r'entities', EntityViewSet)
router.register(r'bills', BillViewSet)
router.register(r'allocations', AllocationViewSet)
router.register(r'disbursements', DisbursementViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'evidence', EvidenceViewSet)
router.register(r'flags', FlagViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('ingest/transactions/', IngestTransactions.as_view(), name='ingest-transactions'),
    path('ingest/allocations/', IngestAllocations.as_view(), name='ingest-allocations'),
    path('ingest/evidence/', IngestEvidence.as_view(), name='ingest-evidence'),
    path('', TemplateView.as_view(template_name='dashboard.html'), name='home'),
    path('alerts/', TemplateView.as_view(template_name='alerts.html'), name='alerts'),
    path('data-entry/', views.data_entry_view, name='data-entry'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('bill/<str:bill_id>/', views.bill_detail, name='bill-detail'),
    path('allocation/<str:allocation_id>/', views.allocation_detail, name='allocation-detail'),
    path('disbursement/<str:disbursement_id>/', views.disbursement_detail, name='disbursement-detail'),
    path('transaction/<str:tx_id>/', views.transaction_detail, name='transaction-detail'),
    path('entity/<int:entity_id>/', views.entity_detail, name='entity-detail'),
    path('counties/<str:county_name>/', views.county_dashboard, name='county-dashboard'),
    path('rumor/<str:rumor_id>/', views.rumor_detail, name='rumor-detail'),
    path('counties/', views.county_list, name='county-list'),
]