# FinSight (Temporary Name)

AI-powered Financial Health Card for MSMEs

## Problem Statement

Traditional MSME credit evaluation depends heavily on credit history and financial statements. Many New-to-Credit (NTC) and New-to-Bank (NTB) businesses lack these records despite having healthy financial activity.

Our solution combines alternate financial data sources such as GST, UPI, EPFO and Bank Statements to generate an explainable Financial Health Score that assists banks in making faster and more inclusive lending decisions.

---

## Features

- Financial Health Score (0–100)
- Green / Amber / Red Risk Classification
- Explainable Score Breakdown
- Dashboard for Loan Officers
- REST API for Score Generation

---

## Tech Stack

### Frontend
- React
- Vite
- Tailwind CSS
- Chart.js / Recharts

### Backend
- FastAPI
- Python

### ML
- Pandas
- Scikit-learn / XGBoost

### Database
- PostgreSQL

---

## Team

| Member | Responsibility |
|---------|----------------|
| Soham | Dataset & Data Preparation |
| Tanay | Backend (FastAPI, APIs, Database) |
| Nishtha | Frontend (React + Vite) |
| Ayaan | Machine Learning + Documentation |

---

## Folder Structure

```
project/
│
├── frontend/
├── backend/
├── ml/
├── datasets/
├── docs/
└── README.md
```

---

## Development Flow

Dataset → ML Model → Backend API → Frontend Dashboard → Final Testing