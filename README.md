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
- **Django 6:** REST API architecture and secure authentication.
- **Atomic Transactions:** Ensures database integrity during complex money transfers.
- **Custom Logic:** Automated IBAN and BIC/SWIFT generation.

---

## 🚀 How to Run (Complete instructions)
This section will help you set up MMM-Bank on your local computer. Follow the steps in order.

## 0. Prerequisites

Before you begin, make sure you have the following installed:

Python (version 3.12 or later) — [Download here](https://www.python.org/downloads/)

Node.js (version 20 or later) — [Download here](https://nodejs.org/en/download)

Git — [Download here](https://git-scm.com/install/)

The project uses environment variables for security. You must create the 
actual configuration files by copying the provided examples and filling in your own credentials.

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
3. Create .env file:
```console
Navigate to the backend/ directory.

Copy .env.example to a new file named .env

Open .env and provide your SECRET_KEY (you can generate one or use a temporary development string) and ensure the EMAIL_HOST_PASSWORD is correct.

If you don't have your EMAIL_HOST_PASSWORD, you'll find instructions later in this tutorial
```   
5. Prepare the database:
Navigate to the backend folder and run the “migration” commands (this will create tables for users and accounts):
```console
cd backend
python3 manage.py migrate
```
5. Create an Administrator (Superuser):
This will allow you to access the bank's control panel.
```console
python manage.py createsuperuser

# Enter your username, email address, and password (the characters in your password wont appear as you type—this is normal).
```
6. Run server
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
3. Create environments files
```console
Navigate to frontend/src/environments/.

Create the environments folder if it doesn't exist.

Copy environment.example.ts to create two files: environment.ts and environment.development.ts:

Open these files and replace the placeholder values with your actual Firebase API keys and project IDs.

If you don't have your own Firebase API keys and project IDs, you'll find instructions later in this tutorial
```
3. Run website:
```console
npm start

or

ng serve
```
### 4. How to use it?

Now that both servers are running:

The website itself: Open http://localhost:4200 in your browser

The admin panel (Django): http://localhost:8000/admin (log in using the superuser credentials you created earlier).

### 5. 📖 Appendix: Detailed Setup Guides

#### A. How to Get an Email App Password (for backend `.env`)
If you are using Gmail to send emails from Django (e.g., for password resets), you cannot use your regular Google password due to security restrictions. You need an "App Password":
1. Go to your [Google Account](https://myaccount.google.com/).
2. Navigate to **Security** on the left-hand panel.
3. Ensure **2-Step Verification** is turned **ON**.
4. Click on **2-Step Verification**, scroll to the bottom, and select **App Passwords**.
5. Enter a name for the app (e.g., "MMM-Bank") and click **Create**.
6. A window will appear with a 16-character password. Copy it and paste it into your `backend/.env` file (e.g., `EMAIL_HOST_PASSWORD=your-16-char-password`).

#### B. How to Set Up a Firestore Database (for frontend `environment.ts`)
If you are setting up the project from scratch and need your own Firebase database for the real-time chat:
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project**, enter a name (e.g., "mmm-bank"), and follow the setup steps.
3. On the left menu, expand **Build** and click **Firestore Database**.
4. Click **Create database**. 
5. Select **Start in test mode** (this allows you to read/write data easily during local development) and click **Next** -> **Enable**.
6. **To get your API keys:** Go back to the **Project Overview** (home icon), click the **⚙️ Gear icon** -> **Project settings**.
7. Scroll down to the **Your apps** section, click the **Web icon (`</>`)**, and register the app.
8. Copy the generated `firebaseConfig` variables into your `frontend/src/environments/environment.ts` and `environment.development.ts` files.

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
