# 🏦 MMM-Bank

[![Angular](https://img.shields.io/badge/Frontend-Angular%2018-red?style=flat-square&logo=angular)](https://angular.dev/)
[![Django](https://img.shields.io/badge/Backend-Django%205-green?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0.html.en)

> **MMM-Bank** is a sophisticated full-stack banking ecosystem designed to simulate modern financial operations. Built by students to master the integration of a powerful Django backend with a dynamic Angular SPA frontend.

---

## ✨ Key Features

- 💳 **Multi-Currency Accounts:** Open and manage accounts in USD, EUR, and UAH instantly.
- 💱 **Smart Exchange:** Real-time internal currency conversion using live exchange rates.
- 📜 **Categorized History:** Clean transaction logs grouped by date (Today, Yesterday, etc.).
- 📑 **Banking Details:** Automatic **IBAN** generation for every account with a "click-to-copy" system.
- 🛡️ **Financial Precision:** All calculations performed using the `Decimal` type to ensure 100% accuracy in balances.
- 🎨 **Modern UX/UI:** Fluid animated backgrounds, glassmorphism components, and a fully responsive layout.

---

## 🛠 Tech Stack

### **Frontend (SPA)**
- **Angular 18:** Standalone components, RxJS for data streams, and optimized Routing.
- **SCSS:** Advanced styling with variables and adaptive layouts.
- **FontAwesome:** Professional iconography.

### **Backend**
- **Django 5:** REST API architecture and secure authentication.
- **Atomic Transactions:** Ensures database integrity during complex money transfers.
- **Custom Logic:** Automated IBAN and BIC/SWIFT generation.

---

## 🚀 How to Run

### 0. Clone Project
```console
# Clone the repository
git clone https://github.com/Fev1L/MMM-Bank.git
cd MMM-Bank

# Setup environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac OR .venv\Scripts\activate for Windows
pip install -r requirements.txt
```
### 1. Backend (Django)
```console
# Install & Migrate
cd backend
python manage.py migrate
python manage.py runserver
```
### 2. Frontend (Angular)
```console
# Navigate to frontend directory
cd frontend
npm install

# Start development server
ng serve
```
### Visit http://localhost:4200 to see the app in action!

---

## 📊 Roadmap

[x] Authorisation: Log in/create an account in seconds.

[x] Accounts: The ability to create accounts dynamically.

[x] Transactions: flexible transaction creation.

[x] Credits System: Apply for and manage bank loans.

[x] Deposits: High-interest savings accounts.

[ ] 🚧 More: There’s plenty of interesting stuff to enhance the ecosystem.

[ ] 🚧 Profile: Advanced profile settings.

[ ] 🚧 Dark Mode: System-wide dark UI support.

---

## 👥 The Team

[Fev1L](https://github.com/Fev1L) — Team Lead & Lead developer.

[SanyaG23](https://github.com/SanyaG23) — Backend & API Engineer.

[dimachubuk15](https://github.com/dimachubuk15) — Administration & Security Specialist.

---

## 📸 Screenshots

![photo_2026-04-01 20 53 26](https://github.com/user-attachments/assets/83beb29d-e418-4dd8-88be-a27db8cd9e47)
![photo_2026-04-01 20 53 31](https://github.com/user-attachments/assets/45544fb4-8204-467a-bdc7-b508d85ebbd0)

---

### Built for educational purposes with a focus on clean code and user experience.
