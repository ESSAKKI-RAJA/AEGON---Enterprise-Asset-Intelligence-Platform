# AEGON Quick Start

A one-minute setup guide to get AEGON running on your local machine.

## Prerequisites
- Node.js v20+
- Python 3.12+
- PostgreSQL 15+

## 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
*Backend runs on `http://127.0.0.1:8000`*

## 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://127.0.0.1:5173`*

## 3. One-Click Start (Windows)
We provide a convenient setup and run script:
```bash
.\scripts\setup.ps1
.\scripts\run-pipeline.ps1
```
