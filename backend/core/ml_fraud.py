# fraudshield/ml_fraud.py
import pandas as pd
from sklearn.ensemble import IsolationForest
from django.utils import timezone
from .models import Transaction, Flag, Entity
from django.contrib.contenttypes.models import ContentType
import uuid

def run_ml_fraud_detection():
    """Run ML every 60 seconds — creates HIGH severity flags"""
    print("ML Fraud Detection Running...")

    # Get last 7 days of transactions
    cutoff = timezone.now() - timezone.timedelta(days=7)
    txs = Transaction.objects.filter(timestamp__gte=cutoff).select_related(
        'source_entity', 'dest_entity'
    )

    if txs.count() < 10:
        print("Not enough data for ML")
        return

    # Build feature vector
    data = []
    tx_ids = []
    for tx in txs:
        src = tx.source_entity
        dst = tx.dest_entity
        data.append([
            float(tx.amount),
            1 if dst.entity_type == 'vendor' and not dst.national_id else 0,
            1 if src.entity_type == 'county' else 0,
            1 if 'mpesa' in tx.tx_type.lower() else 0,
            tx.timestamp.hour,
            tx.timestamp.weekday(),
            len([t for t in txs if t.dest_entity_id == dst.id])  # frequency
        ])
        tx_ids.append(tx.id)

    df = pd.DataFrame(data, columns=[
        'amount', 'ghost_vendor', 'from_county', 'is_mpesa',
        'hour', 'weekday', 'dest_freq'
    ])

    # Train Isolation Forest
    model = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly'] = model.fit_predict(df)
    df['score'] = model.decision_function(df)

    # Create flags for anomalies
    for i, row in df.iterrows():
        if row['anomaly'] == -1:  # Fraud
            tx = txs[i]
            reason = f"ML Anomaly: KSh {tx.amount:,.0f} to {tx.dest_entity.name}"
            create_flag_if_not_exists(tx, 5, reason, row['score'])

def create_flag_if_not_exists(obj, severity, reason, score):
    ct = ContentType.objects.get_for_model(obj)
    if Flag.objects.filter(content_type=ct, object_id=obj.id).exists():
        return

    Flag.objects.create(
        flag_id=str(uuid.uuid4()),
        severity=severity,
        reason=reason,
        score=float(score),
        content_type=ct,
        object_id=obj.id
    )
    print(f"ML FLAG: {reason}")