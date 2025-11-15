# fraudshield/ml_fraud.py
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from django.utils import timezone
from .models import Transaction, Flag, Entity, County, Rumor
from django.contrib.contenttypes.models import ContentType
import uuid
import requests
import json
import re

# === CONFIG ===
X_API_BEARER = "YOUR_X_BEARER_TOKEN"
X_SEARCH_URL = "https://api.twitter.com/2/tweets/search/recent"

def run_ml_fraud_detection():
    """Run every 60s — Isolation Forest + Frequency + Timing"""
    cutoff = timezone.now() - timezone.timedelta(days=7)
    txs = Transaction.objects.filter(timestamp__gte=cutoff).select_related(
        'source_entity', 'dest_entity', 'source_entity__county', 'dest_entity__county'
    )
    if txs.count() < 20:
        return

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
            txs.filter(dest_entity=dst).count(),
            1 if src.county and dst.county and src.county != dst.county else 0,
            1 if tx.timestamp.hour < 6 or tx.timestamp.hour > 22 else 0,
        ])
        tx_ids.append(tx.id)

    cols = ['amount','ghost','from_county','mpesa','hour','weekday','freq','cross_county','night']
    df = pd.DataFrame(data, columns=cols)
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)
    model = IsolationForest(contamination=0.03, random_state=42)
    df['anomaly'] = model.fit_predict(df_scaled)
    df['score'] = model.decision_function(df_scaled)

    for i, row in df.iterrows():
        if row['anomaly'] == -1:
            tx = Transaction.objects.get(id=tx_ids[i])
            reason = f"ML Anomaly: KSh {tx.amount:,.0f} → {tx.dest_entity.name} (Score: {row['score']:.3f})"
            create_flag(tx, 5, reason, row['score'])

def scrape_x_rumors():
    """Scrape X for county fraud rumors"""
    counties = County.objects.values_list('name', flat=True)
    for county in counties[:10]:  # limit
        query = f"({county} corruption OR fraud OR ghost) lang:en -is:retweet"
        headers = {"Authorization": f"Bearer {X_API_BEARER}"}
        params = {"query": query, "max_results": 10}
        try:
            resp = requests.get(X_SEARCH_URL, headers=headers, params=params, timeout=10)
            if resp.status_code != 200: continue
            tweets = resp.json().get('data', [])
            for t in tweets:
                text = t['text']
                sentiment = "negative" if any(w in text.lower() for w in ['fraud','ghost','corrupt']) else "neutral"
                Rumor.objects.update_or_create(
                    rumor_id=t['id'],
                    defaults={
                        'text': text[:500],
                        'source': 'twitter',
                        'url': f"https://x.com/i/web/status/{t['id']}",
                        'sentiment': sentiment,
                        'score': -0.9 if sentiment == 'negative' else 0.1,
                        'timestamp': timezone.now(),
                        'related_county': County.objects.filter(name__icontains=county).first()
                    }
                )
        except: pass

def create_flag(obj, severity, reason, score):
    ct = ContentType.objects.get_for_model(obj)
    if Flag.objects.filter(content_type=ct, object_id=obj.id, reason__icontains=reason[:50]).exists():
        return
    Flag.objects.create(
        flag_id=str(uuid.uuid4()),
        severity=severity,
        reason=reason,
        score=float(score),
        content_type=ct,
        object_id=obj.id
    )