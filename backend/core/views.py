
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