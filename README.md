# Multi-Tenant Organization Manager

A secure, async backend system built with **FastAPI + SQLAlchemy (async)** supporting multi-tenancy, RBAC, audit logging, and AI-powered insights.

---

#  Overview

This project implements a **multi-tenant architecture** where users can:

- Create organizations
- Invite members with roles (Admin / Member)
- Manage organization-specific data (items)
- Track activity logs
- Query logs using AI (LLM)

---

#  Tech Stack

- **FastAPI** – async web framework  
- **SQLAlchemy 2.0 (async)** – ORM  
- **PostgreSQL** – database  
- **JWT (python-jose)** – authentication  
- **RBAC** – role-based access control  
- **Pytest + Testcontainers** – testing  
- **Docker + Docker Compose** – containerization  
- **OpenAI API** – AI insights  

---

#  Architecture


app/
├── api/ # Routes (auth, org, item, audit)
├── core/ # Security, RBAC, dependencies
├── db/ # DB session & base
├── models/ # SQLAlchemy models
├── services/ # Business logic


---

#  Features

##  Authentication
- User registration & login
- Password hashing (bcrypt)
- JWT-based authentication

##  Multi-Tenancy
- Users can belong to multiple organizations
- Data is scoped per organization

## RBAC (Role-Based Access Control)
- Admin vs Member roles
- Access enforced via dependency injection

## Items Management
- Members see only their items
- Admins see all organization items

##  Audit Logs
- Tracks all key actions
- Admin-only access

##  AI Integration
- Ask questions about logs
- Supports streaming responses
- Uses OpenAI (GPT)

---

#  Docker Setup (MANDATORY)

## ▶️ Run the system

```bash
docker compose up --build
 Access API
http://localhost:8000/docs


## Environment Variables
Create .env file and add your:
 - OPENAI_API_KEY=your_api_key_here
- DATABASE_URL=your_DATABASE_URL
- SECRET_KEY=your_DATABASE_URL


 Testing

## I used:

pytest
pytest-asyncio
testcontainers (PostgreSQL)
▶️ Run tests
pytest -v
**** What is tested
Authentication
RBAC enforcement
Organization isolation
Item access rules


All DB operations use asyncpg for performance and scalability.

