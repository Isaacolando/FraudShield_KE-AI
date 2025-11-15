
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Entity,Bill,Allocation,Disbursement,Transaction,EvidenceDocument,Flag
from .serializers import EntitySerializer,BillSerializer,AllocationSerializer,DisbursementSerializer,TransactionSerializer,EvidenceDocumentSerializer,FlagSerializer
from django.shortcuts import get_object_or_404
import uuid
from django.contrib.auth.decorators import login_required
import json
from .models import Transaction, EvidenceDocument
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials or not staff")
    return render(request, 'login.html')

@login_required
def alerts_view(request):
    if not request.user.is_staff:
        return redirect('login')
    return render(request, 'alerts.html')




@login_required(login_url='/login/')
def data_entry_view(request):
    if not request.user.is_staff:
        return redirect('login')

    tabs = [
        {
            "id": "entity",
            "label": "Entity",
            "fields": """
                <input type="text" name="name" placeholder="Name" required class="w-full px-4 py-3 rounded-xl border">
                <select name="entity_type" required class="w-full px-4 py-3 rounded-xl border">
                    <option value="county">County</option>
                    <option value="vendor">Vendor</option>
                    <option value="mp">MP</option>
                    <option value="bank">Bank</option>
                    <option value="telco">Telco</option>
                </select>
                <input type="text" name="national_id" placeholder="National ID (optional)" class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="phone" placeholder="Phone (optional)" class="w-full px-4 py-3 rounded-xl border">
            """
        },
        {
            "id": "bill",
            "label": "Bill",
            "fields": """
                <input type="text" name="bill_id" placeholder="Bill ID (e.g. B2025-001)" required class="w-full px-4 py-3 rounded-xl border">
                <input type="number" name="year" placeholder="Year" value="2025" required class="w-full px-4 py-3 rounded-xl border">
                <input type="number" step="0.01" name="amount" placeholder="Amount (KSh)" required class="w-full px-4 py-3 rounded-xl border">
                <textarea name="purpose" placeholder="Purpose" class="w-full px-4 py-3 rounded-xl border h-24"></textarea>
            """
        },
        {
            "id": "allocation",
            "label": "Allocation",
            "fields": """
                <input type="text" name="allocation_id" placeholder="Allocation ID" required class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="bill_id" placeholder="Bill ID (e.g. B2025-001)" required class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="to_entity" placeholder="Recipient Entity Name" required class="w-full px-4 py-3 rounded-xl border">
                <input type="number" step="0.01" name="amount" placeholder="Amount" required class="w-full px-4 py-3 rounded-xl border">
                <input type="date" name="date_allocated" required class="w-full px-4 py-3 rounded-xl border">
            """
        },
        {
            "id": "disbursement",
            "label": "Disbursement",
            "fields": """
                <input type="text" name="disbursement_id" placeholder="Disbursement ID" required class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="allocation_id" placeholder="Allocation ID" required class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="to_entity" placeholder="Recipient Entity Name" required class="w-full px-4 py-3 rounded-xl border">
                <input type="number" step="0.01" name="amount" placeholder="Amount" required class="w-full px-4 py-3 rounded-xl border">
                <input type="date" name="date" required class="w-full px-4 py-3 rounded-xl border">
            """
        },
        {
            "id": "transaction",
            "label": "Transaction",
            "fields": """
                <input type="text" name="tx_id" placeholder="Transaction ID" required class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="source_entity_id" placeholder="Source Entity ID" required class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="dest_entity_id" placeholder="Destination Entity ID" required class="w-full px-4 py-3 rounded-xl border">
                <input type="number" step="0.01" name="amount" placeholder="Amount" required class="w-full px-4 py-3 rounded-xl border">
                <input type="datetime-local" name="timestamp" required class="w-full px-4 py-3 rounded-xl border">
                <select name="tx_type" required class="w-full px-4 py-3 rounded-xl border">
                    <option value="mpesa">M-Pesa</option>
                    <option value="bank">Bank</option>
                    <option value="cheque">Cheque</option>
                </select>
            """
        },
        {
            "id": "evidence",
            "label": "Evidence",
            "fields": """
                <input type="text" name="doc_id" placeholder="Document ID" required class="w-full px-4 py-3 rounded-xl border">
                <input type="file" name="file" accept=".pdf,.jpg,.png" class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="related_allocation" placeholder="Allocation ID (optional)" class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="related_transaction" placeholder="Transaction ID (optional)" class="w-full px-4 py-3 rounded-xl border">
            """
        },
        {
            "id": "flag",
            "label": "Flag",
            "fields": """
                <select name="severity" required class="w-full px-4 py-3 rounded-xl border">
                    <option value="1">Low</option>
                    <option value="2">Medium</option>
                    <option value="3">High</option>
                    <option value="4">Critical</option>
                    <option value="5">Severe</option>
                </select>
                <textarea name="reason" placeholder="Reason for flag" required class="w-full px-4 py-3 rounded-xl border h-32"></textarea>
                <input type="text" name="object_id" placeholder="Related Object ID" required class="w-full px-4 py-3 rounded-xl border">
                <input type="text" name="content_type" placeholder="Model (e.g. transaction)" required class="w-full px-4 py-3 rounded-xl border">
            """
        }
    ]

    return render(request, 'data_entry.html', {
        'tabs': tabs,
        'tabs_json': json.dumps([{'id': t['id'], 'label': t['label']} for t in tabs])
    })
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

# Lightweight ingest endpoints 
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

# details views fuctions 
from django.shortcuts import render, get_object_or_404
from .models import Bill, Allocation, Disbursement, Transaction, Entity, EvidenceDocument

def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, bill_id=bill_id)
    allocations = bill.allocation_set.all()
    return render(request, 'detail/bill.html', {'bill': bill, 'allocations': allocations})

def allocation_detail(request, allocation_id):
    alloc = get_object_or_404(Allocation, allocation_id=allocation_id)
    return render(request, 'detail/allocation.html', {'alloc': alloc})

def disbursement_detail(request, disbursement_id):
    disb = get_object_or_404(Disbursement, disbursement_id=disbursement_id)
    return render(request, 'detail/disbursement.html', {'disb': disb})

def transaction_detail(request, tx_id):
    tx = get_object_or_404(Transaction, tx_id=tx_id)

    # ONLY DIRECT EVIDENCE
    evidence = EvidenceDocument.objects.filter(related_transaction=tx)

    return render(request, 'detail/transaction.html', {
        'tx': tx,
        'evidence': evidence
    })
def entity_detail(request, entity_id):
    entity = get_object_or_404(Entity, id=entity_id)
    incoming = Transaction.objects.filter(dest_entity=entity)
    outgoing = Transaction.objects.filter(source_entity=entity)
    return render(request, 'detail/entity.html', {
        'entity': entity,
        'incoming': incoming,
        'outgoing': outgoing
    })