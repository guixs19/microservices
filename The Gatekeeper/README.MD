💳 Credit Management System

A complete credit management system built with FastAPI, SQLite, and Docker. The platform ensures that user balances never become negative by validating transactions before processing.

✨ Features
🎯 Core Features

✅ Non-negative balance enforcement — The system validates credits before every debit operation

✅ JWT Authentication — Secure token-based authentication

✅ Interactive dashboard — Modern and responsive user interface

✅ Transaction history — Full audit trail with timestamps

✅ Spending charts — Credit usage visualization over time

✅ CSV export — Transaction reporting and data export

🚀 Additional Features

Simulated payment webhook

Credit recharge functionality

Real-time visual feedback

Automatic balance updates

🛠️ Technologies

Backend: FastAPI, SQLAlchemy, Pydantic

Frontend: HTML5, CSS3, Vanilla JavaScript

Database: SQLite

Authentication: JWT + Bcrypt

Containerization: Docker & Docker Compose

Charts: Chart.js

📋 Requirements

Docker and Docker Compose (recommended)

OR Python 3.11+ with pip (local execution)

🚀 Installation and Setup
🐳 Using Docker (Recommended)

Clone the repository

git clone https://github.com/your-username/credit-system.git
cd credit-system
🔐 Security

The system uses JWT for stateless authentication and secure credential handling. Passwords are hashed before storage following industry best practices.

🧠 Business Logic

The application enforces strict business rules to maintain financial consistency:

Users cannot spend more credits than available

All debit operations are validated before execution

Transaction history is recorded for auditing purposes

Only authenticated users can access financial operations

📈 Use Cases

This type of system is commonly used in:

SaaS platforms with usage-based billing

API consumption models

Internal credit systems

Subscription and recharge services

🎥 Demo

A demonstration video showing the full workflow — authentication, credit operations, and dashboard interaction — is included in the repository.

🚀 Future Improvements

Potential enhancements include:

Payment gateway integration

Real payment webhooks

Subscription plans

Rate limiting based on credits

Audit logging

Cloud deployment
