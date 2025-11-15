from django.core.management.base import BaseCommand
from core.ml_fraud import run_ml_fraud_detection

class Command(BaseCommand):
    help = "Run ML Fraud Detection"

    def handle(self, *args, **options):
        run_ml_fraud_detection()
        self.stdout.write(self.style.SUCCESS("ML Fraud Detection Complete"))