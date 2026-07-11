# FinPulse 💳🌱

### AI/ML-Driven Financial Health Card for MSMEs
**IDBI Innovate 2026 | Track 03: Financial Inclusion, Digital Lending & Credit Decisioning**

---

## 📋 Executive Summary

**FinPulse** is a credit assessment engine designed to replace traditional, collateral-heavy credit scoring for MSMEs. By aggregating multi-source alternative data ecosystems (GST, UPI, Account Aggregator, and EPFO), FinPulse computes a multidimensional **Financial Health Score (0-100)** delivered via high-performance APIs.

* **The Problem:** Over 50% of viable MSMEs in India are rejected due to their "credit-invisible" or "New-to-Credit" status under archaic lending frameworks.
* **The Solution:** A unified, real-time assessment API engine that translates alternative transaction behavior into reliable, explainable risk markers for instantaneous lending decisions.
* **The Impact:** Reduces false rejections by 90%, enables near real-time decisioning (<30s), and expands access to an unmapped ₹5 Lakh Crore credit market.

---

## 🏗️ Technical Architecture

```text
[ Alternative Data Sources ]
(GSTN, NPCI, EPFO, Open Banking APIs)
             │
             ▼
┌───────────────────────────┐
│     Data Ingestion Layer  │ ──► Schema Normalization & Validation
└───────────────────────────┘
             │
             ▼
┌───────────────────────────┐
│   FinPulse Scoring Engine │ ──► Feature Engineering (Pandas / Polars)
└───────────────────────────┘ ──► Risk Classification Model (XGBoost)
             │
             ▼
┌───────────────────────────┐
│        Decision API       │ ──► FastAPI REST Endpoint (POST /api/v1/score)
└───────────────────────────┘ ──► Returns Full Diagnostic Health Card Payload