# 🏦 MMM-Bank

[![Angular](https://img.shields.io/badge/Frontend-Angular%2018-red?style=flat-square&logo=angular)](https://angular.dev/)
[![Django](https://img.shields.io/badge/Backend-Django%205-green?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0.html.en)

> **MMM-Bank** is a sophisticated full-stack banking ecosystem designed to simulate modern financial operations. Built by students to master the integration of a powerful Django backend with a dynamic Angular SPA frontend.

---

## 📽️ [Advertisement MMM Bank](https://www.youtube.com/watch?v=a0B_9BZt2e4)

## 🌐 [Visit our Website live!](https://mmm-bank.vercel.app/)

## ✨ Key Features

- 🏦 Instant Banking: Open a digital account in seconds and manage your finances from anywhere in the world.
- 💰 Smart Savings: Create personalized "Piggy Banks" with progress tracking to reach your financial goals faster.
- 📈 Fixed Deposits: Grow your wealth with high-yield deposit plans and real-time profit calculation.
- 💸 Global Transfers: Send and receive funds across multiple currencies (USD, EUR, UAH) with competitive exchange rates.
- 📱 Seamless Experience: A fully responsive, modern interface designed for both desktop and mobile users.
- 🔒 Enterprise-Grade Security: Advanced data protection and precise financial calculations for total peace of mind.

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
### 1.1 Create Superuser (Admin Access)
To access the Django Administration panel and manage users/accounts manually:
```console
# Ensure you are in the backend directory with active venv
python manage.py createsuperuser
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

[X] More: There’s plenty of interesting stuff to enhance the ecosystem.

[ ] 🚧 Profile: Advanced profile settings.

[ ] 🚧 Dark Mode: System-wide dark UI support.

---

## 📂 Project Structure

```text
MMM-Bank/
├── backend/                # Django REST Framework Project
│   ├── config/               # Project settings & WSGI/ASGI
│   ├── main/                # Main API application
│   │   ├── models/         # Database models (User, Account, Transaction)
│   │   └── views/          # API logic & endpoints
│   ├── credits/              # Credits API
│   ├── deposits/              # Deposits API
│   └──  manage.py           # Django CLI
├── frontend/               # Angular SPA
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/ # Reusable UI elements
│   │   │   ├── services/   # API communication & State management
│   │   │   └── auth/       # Firebase authentication logic
│   │   └── environments/   # Configuration (Firebase keys)
│   └── package.json        # Node.js dependencies & scripts
├── .gitignore              # Global git ignore rules
└── requirements.txt    # Python dependencies
```

---

## 👥 The Team

[Fev1L](https://github.com/Fev1L) — Team Lead & Lead developer.

[SanyaG23](https://github.com/SanyaG23) — Backend & API Engineer.

[dimachubuk15](https://github.com/dimachubuk15) — Administration & Security Specialist.

---

## 📸 Screenshots
![photo](https://github.com/user-attachments/assets/8046abf9-e2da-4494-ba48-eb33654e9993)
![photo](https://github.com/user-attachments/assets/114cdc69-829c-438c-a52d-a9e94eda32bb)

---

### Built for educational purposes with a focus on clean code and user experience.
