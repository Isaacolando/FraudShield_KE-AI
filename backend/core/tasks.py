# core/tasks.py
from celery import shared_task
from .ml_fraud import run_ml_fraud_detection, scrape_x_rumors

@shared_task
def run_fraud_detection_task():
    run_ml_fraud_detection()

@shared_task
def scrape_rumors_task():
    scrape_x_rumors()