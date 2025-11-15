# FraudShield Kenya — National Fraud Monitor

Real-time public fund tracking & AI-powered fraud detection across 47 counties.

> "Hii ni yetu."
> A transparent, unbreakable, Kenyan-made system to **track every shilling** — from Parliament Bill → County Allocation → Disbursement → Bank/MPesa Transaction — with **instant fraud alerts**.

## Problem We Solve

> **KSh 2B+ lost yearly** to ghost projects, fake vendors, and double payments.  
> **No one knows** where money goes after allocation.  
> **Audits take 18 months**.  
> **Citizens are in the dark**.

## Solution: FraudShield Kenya

### Real-Time Fund Flow Graph
- **Live visualization** of money moving from **Treasury → Counties → Vendors → Banks**
- **Red edges = ML-detected fraud** (ghost payments, loops, timing anomalies)
- **Hover → instant details** | **Click → full audit trail**

### AI Fraud Detection (Built-in)
| Flag Type | Trigger |

| Ghost Vendor | No KRA PIN, no phone, sudden large payment |
| Double Payment | Same amount, same day, same vendor |
| Timing Anomaly | Payment before allocation |
| Loop Fraud | Money returns to source within 72h |
## Features

| Feature | Status |

| Interactive Fund Flow Graph (Cytoscape.js) | Done |
| Hover + Click → Full Detail Pages | Done |
| Persistent Dark Mode (localStorage + system) | Done |
| Staff Data Entry Portal (Bills, Allocations, etc.) | Done |
| ML Fraud Flags (severity 1–5) | Done |
| Evidence Upload (PDF, Images) | Done |
| Responsive Kenyan Design (Red/Black/Green) | Done |
| Django REST API + Admin | Done |
| County-Level Drilldown (coming) | In Progress |
--->In details
FraudShield — National Payment & Government Funds Flow Fraud Detection
• Ingests: telco/mobile-money transactions, bank transfers, government allocation
records (bills → votes → allocations → county disbursements → project payments),
and evidence documents (receipts, invoices, PDFs).
• Builds: a transaction graph / knowledge graph that links money flows to entities
(MPs, counties, vendors) and documents.
• Detects: anomalies in flows (unusual routing, amounts, duplicate beneficiaries,
mismatched invoice data), suspicious document tampering, and policy violations
(funds used for non-intended projects).
• Outputs: ranked alerts with explainability (why flagged), evidence links, and
notifications to relevant bodies

Data ingestion: batch + streaming. Normalize transaction records and government
allocation records into a single schema.
• Linking: entity resolution & knowledge graph that connects IDs, phone numbers,
vendor names, county codes, project IDs.
• Models:
o Graph-based anomaly detection (graph features + isolation forest /
autoencoder; optionally GNN for more advanced teams).
o Time-series / sequence anomaly detection for repeated flows (LSTM
autoencoder or Temporal Convolution).
o NLP/OCR pipeline to extract fields from receipts/invoices (Tesseract or
commercial OCR) + NLP mismatch detection (NER + fuzzy matching).
• Explainability: SHAP or rule-based extractors to show which features triggered flag.
• UI/Integrations: admin dashboard + alert inbox + exportable report + push
notifications.
     Prioritized MVP features (what to build first
1. Ingest synthetic mobile money transactions and gov allocation records into
PostgreSQL.
2. Build entity resolution to match phone numbers / IDs to entities.
3. Knowledge graph (simple adjacency tables) that shows flows
bill→allocation→disbursement→transaction.
4. Train an anomaly detector (IsolationForest or Autoencoder) on transaction + flow
features.
5. Dashboard view showing top 10 flagged flows with evidence links and one-click
“export PDF” report.
6. Notification (Firebase cloud message or email) for high-severity flags.

## Tech Stack

```bash
Django 5.1 + Django REST Framework
PostgreSQL
Tailwind CSS (CDN) + Vanilla JS
Cytoscape.js (Graph)
AOS Animations
Qdrant (future vector search)
Celery + Redis (future async)
