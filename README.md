# 💰 M-Pesa API Playground

[![Live Demo](https://img.shields.io/badge/Live_Demo-Render-blue)](https://mpesa-daraja-apis.onrender.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Repo-black)](https://github.com/ArapCheruiyot/Darajaplay)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-red)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📌 Overview

**M-Pesa API Playground** is an interactive demonstration platform for Safaricom's Daraja API. It allows developers to test and understand M-Pesa integration in a sandbox environment before going to production.

Built as a learning tool and reference implementation for anyone integrating mobile payments in Africa.

🔗 **Live Demo:** [mpesa-daraja-apis.onrender.com](https://mpesa-daraja-apis.onrender.com/)

---

## ✨ Features

### 🚀 Currently Implemented

| Feature | Description | Status |
|---------|-------------|--------|
| **C2B (STK Push)** | Customer-to-business payments via M-Pesa prompt | ✅ Live |
| **B2C (Payouts)** | Business-to-customer payments and disbursements | ✅ Live |
| **Real-time API Status** | Monitor connection status and response codes | ✅ Live |
| **Tab-based Interface** | Clean UI for testing different payment flows | ✅ Live |
| **Sentry Monitoring** | Production-grade error tracking | ✅ Live |

### 🔜 Coming Soon

| Feature | Status |
|---------|--------|
| Transaction Reversal | 🚧 In Development |
| QR Code Generation | 🚧 In Development |
| Transaction History | 📋 Planned |
| Webhook Debugger | 📋 Planned |

---

## 🛠️ Technical Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.10+ / Flask |
| **API** | Safaricom Daraja API (OAuth 2.0, STK Push, B2C) |
| **Monitoring** | Sentry SDK |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Deployment** | Render.com |
| **Version Control** | Git / GitHub |

---

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/test` | GET | Verify API connectivity |
| `/api/c2b/stkpush` | POST | Initiate STK Push payment |
| `/api/b2c/payout` | POST | Process B2C payment |
| `/api/callback` | POST | Handle M-Pesa transaction callbacks |
| `/api/debug/env` | GET | Debug environment configuration |
| `/api/test-error` | GET | Test Sentry error monitoring |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Safaricom Daraja API credentials (Sandbox)
- ngrok (for local callback testing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ArapCheruiyot/mpesa-playground.git
cd mpesa-playground
