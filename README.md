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

## 🚀 How to Run (Complete instructions)
This section will help you set up MMM-Bank on your local computer. Follow the steps in order.

### 0. Prerequisites

Before you begin, make sure you have the following installed:

Python (version 3.10 or later) — [Download here](https://www.python.org/downloads/)

Node.js (version 20 or later) — [Download here](https://nodejs.org/en/download)

Git — [Download here](https://git-scm.com/install/)

### 1. Clone Project
Open the terminal (or command prompt) and run the following:
```console
# Clone the repository

git clone https://github.com/Fev1L/MMM-Bank.git

cd MMM-Bank
```
### 2. Backend (Django)

1. Create a virtual environment (this is an isolated “box” to prevent the project's libraries from interfering with others):
```console
# For Windows:
python3 -m venv .venv
.venv\Scripts\activate

# For macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
```
2. CInstall the required libraries:
```console
pip install -r requirements.txt
```
3. Prepare the database:
Navigate to the backend folder and run the “migration” commands (this will create tables for users and accounts):
```console
cd backend
python3 manage.py migrate
```
4. Create an Administrator (Superuser):
This will allow you to access the bank's control panel.
```console
python manage.py createsuperuser

# Enter your username, email address, and password (the characters in your password wont appear as you type—this is normal).
```
5. Run server
```console
python3 manage.py runserver

# Do not close this terminal window! The server must run continuously.
```

### 3. Frontend (Angular)
The front end is the attractive interface that users see.
1. Open a NEW terminal window (without closing the first one) and navigate to the frontend folder:
```console
cd MMM-Bank/frontend
```
2. Install the dependencies (Important!):
```console
npm install --legacy-peer-deps
```
3. Run website:
```console
npm start

or

ng serve
```
### 4. How to use it?

Copy .env.EXAMPLE to .env and fill in your credentials.

Copy environment.EXAMPLE to environment and fill in your credentials.

Now that both servers are running:

The website itself: Open http://localhost:4200 in your browser

The admin panel (Django): http://localhost:8000/admin (log in using the superuser credentials you created earlier).

### FAQ

 - “Port 4200 already in use” error: This means that Angular is already running. Just close the terminal and try again.

 - Red text during npm install: If you forgot to add --legacy-peer-deps, Firebase libraries may conflict. Just delete the node_modules folder and run the command correctly.

 - Images (Avatars) are not displayed: Make sure the backend server is running on port 8000, since images are loaded from there.

---

## 📊 Roadmap

[x] Authorisation: Log in/create an account in seconds.

[x] Accounts: The ability to create accounts dynamically.

[x] Transactions: flexible transaction creation.

[x] Credits System: Apply for and manage bank loans.

[x] Deposits: High-interest savings accounts.

[X] More: There’s plenty of interesting stuff to enhance the ecosystem.

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
