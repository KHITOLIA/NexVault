---

# 🌐 NexVault – Full Stack Banking System

🔗 **Live Application:** [https://nexvaullt.up.railway.app/](https://nexvaullt.up.railway.app/)

---

## 🧠 Project Overview

NexVault is a **production-deployed banking web application** that simulates real-world ATM and online banking operations. It is designed with a strong focus on **security, transaction integrity, and scalable backend architecture**.

The application enables users to manage accounts, perform financial transactions, and securely interact with banking services through a web interface.

---

## 🚀 Key Highlights

* 🔐 Secure authentication with hashed PIN (SHA-256)
* 💳 Real-time banking operations (Deposit, Withdraw, Transfer)
* 📊 Transaction tracking with detailed bank statements
* 🚫 Fraud prevention via account lock & transaction limits
* ☁️ Fully deployed on cloud (Railway + MySQL)
* 📧 Integrated email notifications (account creation & PIN reset)

---

## 🏗️ System Architecture

```
Frontend (HTML + Jinja)
        ↓
Flask Backend (Routing + Logic)
        ↓
SQLAlchemy ORM
        ↓
MySQL Database (Railway Cloud)
```

---

## ⚙️ Core Features

### 👤 Account Management

* User registration with unique account number generation
* Secure login system with session management
* Account lock after 3 failed login attempts
* PIN recovery using security question

---

### 💰 Banking Functionalities

* Balance inquiry
* Deposit & withdraw with daily limits
* Peer-to-peer money transfer
* Dynamic transaction validation

---

### 📊 Analytics & Records

* Bank statement generation (date-wise filtering)
* Categorized transactions:

  * Deposits
  * Withdrawals
  * Transfers (sent/received)

---

### 🔐 Security Mechanisms

* SHA-256 PIN hashing
* Brute-force protection (account lock timer)
* Input validation & transaction limits
* Session-based access control

---

## 🛠️ Tech Stack

| Layer      | Technology        |
| ---------- | ----------------- |
| Backend    | Flask             |
| Database   | MySQL (Railway)   |
| ORM        | SQLAlchemy        |
| Frontend   | HTML, CSS, Jinja2 |
| Deployment | Railway           |
| Email      | SMTP (Gmail)      |
| Utilities  | NumPy, dotenv     |

---

## 📦 Deployment Details

* Hosted on Railway with automatic CI/CD via GitHub
* Uses environment variables for secure configuration
* MySQL database integrated via Railway plugin
* Gunicorn used as production WSGI server

---

## 📧 Email System

* Welcome email on account creation
* PIN reset notifications
* SMTP-based integration (Gmail App Password)

> Note: SMTP may be restricted on some cloud environments; API-based services (e.g., SendGrid) are recommended for scalability.

---

## 🧩 Challenges & Solutions

### 🚧 Issue: MySQL driver errors during deployment

**Solution:** Switched from `MySQLdb` to `pymysql` and updated connection string.

---

### 🚧 Issue: Railway SMTP restrictions

**Solution:** Implemented SSL-based SMTP (port 465) with fallback error handling.

---

### 🚧 Issue: App crash after registration

**Solution:** Identified template rendering issue and improved error handling. 

---

## 📈 What This Project Demonstrates

* Full-stack application development
* Backend architecture design using Flask
* Secure authentication and session handling
* Database modeling with relational integrity
* Cloud deployment and environment management
* Debugging real-world production issues

---

## 🔮 Future Enhancements

* JWT-based authentication (API-first architecture)
* React frontend for better UI/UX
* OTP verification system
* Async email processing (Celery / background jobs)
* Financial analytics dashboard
* Fraud Detection System for having unusual Transactions/Patterns(Freeze by Admin)

---

## 👨‍💻 About the Developer

**Tushar**
Aspiring AI/ML Engineer & Full Stack Developer
Focused on building scalable, real-world applications with strong backend systems.

---

## ⭐ Why This Project Matters

This project goes beyond a basic CRUD app — it simulates **core banking workflows**, integrates **security practices**, and is **deployed in a production-like environment**, making it a strong portfolio piece for backend and full-stack roles.

---
