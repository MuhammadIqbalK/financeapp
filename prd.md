# PRD — Simple Personal Finance App

**Version:** 1.0
**Status:** MVP
**Stack:** FastAPI + Svelte + PostgreSQL

# ======= PG ENV =====
DATABASE_URL="postgresql://admin:111111@localhost:5440/financeapp"
---

## 1. Product Overview

A lightweight personal finance application for tracking daily income and expenses.

The primary goal is to let users quickly answer:

* How much money do I have?
* Where does my money go?
* How much did I earn?
* How much did I spend?
* Am I staying within my budget?

### Core Principle

> **Simple, fast, personal, and easy to maintain.**

No accounting system, complex financial planning, or enterprise features.

---

# 2. MVP Scope

The application has only 5 core areas:

```text
Dashboard
Transactions
Categories
Budgets
Settings
```

---

# 3. User

MVP supports a single personal user account.

No:

* Roles
* Teams
* Employees
* Multi-tenant architecture
* Permissions
* Organization management

---

# 4. Core Features

## 4.1 Dashboard

Display a simple financial summary.

### Summary

```text
Balance
Income
Expenses
Savings
```

Example:

```text
Balance       Rp8.500.000
Income        Rp12.000.000
Expenses      Rp3.500.000
Savings       Rp8.500.000
```

### Period

```text
Today
This Week
This Month
Custom Range
```

### Charts

* Income vs Expense
* Expense by Category

### Recent Transactions

Show the latest transactions.

---

# 5. Transactions

The main feature of the application.

A transaction contains:

```text
Transaction
├── Type
├── Amount
├── Category
├── Description
├── Date
└── Account
```

### Transaction Types

```text
Income
Expense
```

### Example

```text
Expense
Rp50.000
Food
Lunch
23 Sep 2026
```

### Features

* Add transaction
* Edit transaction
* Delete transaction
* View transaction
* Search transactions
* Filter by type
* Filter by category
* Filter by date

---

# 6. Categories

Simple user-defined categories.

### Default Income Categories

```text
Salary
Bonus
Freelance
Investment
Other
```

### Default Expense Categories

```text
Food
Transport
Shopping
Bills
Entertainment
Health
Education
Other
```

Users can:

* Add category
* Rename category
* Delete category
* Set category type

No nested categories for MVP.

---

# 7. Budget

Simple monthly budgeting.

User can define a spending limit per category.

Example:

```text
September 2026

Food          Rp1.500.000
Transport       Rp500.000
Entertainment   Rp500.000
Shopping        Rp750.000
```

Dashboard shows:

```text
Food

Spent:
Rp1.200.000

Budget:
Rp1.500.000

Remaining:
Rp300.000
```

### Budget Rules

```text
Remaining = Budget - Expense

Usage % = Expense / Budget × 100
```

No complex forecasting.

---

# 8. Account

A user can track different money accounts.

Examples:

```text
Cash
BCA
Mandiri
GoPay
OVO
```

Account structure:

```text
Account
├── Name
├── Type
└── Initial Balance
```

Types:

```text
Cash
Bank
E-Wallet
Other
```

The application calculates the current balance from the initial balance and transactions.

---

# 9. Transfer

A simple transfer feature allows moving money between accounts.

Example:

```text
BCA
Rp1.000.000
      ↓
GoPay
Rp1.000.000
```

A transfer does **not** count as income or expense.

---

# 10. Reports

Only basic reports are required.

### Monthly Summary

```text
Income       Rp12.000.000
Expenses      Rp3.500.000
Net           Rp8.500.000
```

### Expense Breakdown

```text
Food            35%
Transport       20%
Bills           20%
Shopping        15%
Other           10%
```

### Monthly Trend

```text
Month       Income       Expense

Jun         10M          3M
Jul         11M          4M
Aug         12M          3.5M
Sep         12M          3M
```

---

# 11. Authentication

Simple authentication:

```text
Register
Login
Logout
```

Use:

```text
Email
Password
```

JWT-based authentication is sufficient.

---

# 12. Database

Only the essential entities are required.

```mermaid
erDiagram

    USERS {
        uuid id PK
        string email UK
        string password_hash
        timestamp created_at
    }

    ACCOUNTS {
        uuid id PK
        uuid user_id FK
        string name
        string type
        decimal initial_balance
        boolean is_active
        timestamp created_at
    }

    CATEGORIES {
        uuid id PK
        uuid user_id FK
        string name
        string type
        boolean is_active
    }

    TRANSACTIONS {
        uuid id PK
        uuid user_id FK
        uuid account_id FK
        uuid category_id FK
        string type
        decimal amount
        string description
        date transaction_date
        timestamp created_at
    }

    BUDGETS {
        uuid id PK
        uuid user_id FK
        uuid category_id FK
        integer month
        integer year
        decimal amount
    }

    USERS ||--o{ ACCOUNTS : owns
    USERS ||--o{ CATEGORIES : owns
    USERS ||--o{ TRANSACTIONS : creates
    USERS ||--o{ BUDGETS : creates

    ACCOUNTS ||--o{ TRANSACTIONS : contains
    CATEGORIES ||--o{ TRANSACTIONS : categorizes
    CATEGORIES ||--o{ BUDGETS : limits
```

---

# 13. Backend

FastAPI provides a small REST API.

```text
FastAPI
│
├── Auth
├── Accounts
├── Categories
├── Transactions
├── Budgets
└── Dashboard
```

### API

```http
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

```http
GET    /api/accounts
POST   /api/accounts
PUT    /api/accounts/{id}
DELETE /api/accounts/{id}
```

```http
GET    /api/categories
POST   /api/categories
PUT    /api/categories/{id}
DELETE /api/categories/{id}
```

```http
GET    /api/transactions
POST   /api/transactions
GET    /api/transactions/{id}
PUT    /api/transactions/{id}
DELETE /api/transactions/{id}
```

```http
GET    /api/budgets
POST   /api/budgets
PUT    /api/budgets/{id}
DELETE /api/budgets/{id}
```

```http
GET /api/dashboard
```

---

# 14. Frontend

Use Svelte/SvelteKit with a simple structure.

```text
src/
├── lib/
│   ├── api/
│   │   ├── auth.ts
│   │   ├── accounts.ts
│   │   ├── categories.ts
│   │   ├── transactions.ts
│   │   └── budgets.ts
│   │
│   └── components/
│       ├── ui/
│       ├── dashboard/
│       ├── transactions/
│       └── budgets/
│
└── routes/
    ├── login/
    ├── dashboard/
    ├── transactions/
    ├── accounts/
    ├── categories/
    ├── budgets/
    └── settings/
```

---

# 15. UI Structure

```text
┌───────────────────────────────────┐
│ Personal Finance                  │
├──────────────┬────────────────────┤
│ Dashboard    │                    │
│ Transactions │     Content        │
│ Accounts     │                    │
│ Categories   │                    │
│ Budgets      │                    │
│ Settings     │                    │
└──────────────┴────────────────────┘
```

---

# 16. Add Transaction UI

The most frequently used screen should be very simple.

```text
┌─────────────────────────────┐
│ Add Transaction             │
├─────────────────────────────┤
│                             │
│ Type                        │
│ [ Expense ] [ Income ]      │
│                             │
│ Amount                      │
│ [ Rp ______________ ]       │
│                             │
│ Category                    │
│ [ Food ▼ ]                  │
│                             │
│ Account                     │
│ [ BCA ▼ ]                   │
│                             │
│ Description                 │
│ [ Lunch____________ ]       │
│                             │
│ Date                        │
│ [ 23 Sep 2026 ]             │
│                             │
│       [ Save ]              │
└─────────────────────────────┘
```

---

# 17. Dashboard UI

```text
┌────────────────────────────────────────┐
│ September 2026                         │
├────────────┬────────────┬──────────────┤
│ Balance    │ Income     │ Expenses     │
│ Rp8.5M     │ Rp12M      │ Rp3.5M       │
├────────────┴────────────┴──────────────┤
│                                        │
│ Income vs Expense                      │
│                                        │
│       ╱╲                               │
│  ╱╲  ╱  ╲                              │
│ ╱  ╲╱    ╲                             │
│                                        │
├──────────────────────┬─────────────────┤
│ Expense Categories    │ Recent          │
│                       │ Transactions    │
│ Food       35%        │ Lunch   -50K   │
│ Bills      20%        │ Salary +12M    │
│ Transport  20%        │ Fuel    -100K  │
└──────────────────────┴─────────────────┘
```

---

# 18. Financial Calculations

Keep calculations simple.

### Account Balance

```text
Current Balance
=
Initial Balance
+
Income
-
Expense
+
Transfer In
-
Transfer Out
```

### Total Balance

```text
Total Balance
=
SUM(all account balances)
```

### Savings

```text
Savings
=
Income - Expenses
```

### Budget

```text
Remaining
=
Budget - Category Expenses
```

---

# 19. Architecture

Use a **modular monolith**.

```mermaid
flowchart LR

    Svelte[Svelte / SvelteKit]
    API[FastAPI]
    DB[(PostgreSQL)]

    Svelte -->|REST JSON| API
    API --> DB
```

No microservices.

No message broker.

No Redis.

No background worker.

No event bus.

No Kubernetes.

---

# 20. Technology

| Layer             | Technology      |
| ----------------- | --------------- |
| Frontend          | SvelteKit       |
| Backend           | FastAPI         |
| Database          | PostgreSQL      |
| ORM               | SQLAlchemy      |
| Migration         | Alembic         |
| Validation        | Pydantic        |
| Authentication    | JWT             |
| Frontend Language | TypeScript      |
| Backend Language  | Python          |
| Testing           | Pytest + Vitest |

---

# 21. MVP Development Priority

### P0 — Essential

* Authentication
* Accounts
* Categories
* Transactions
* Dashboard
* Balance calculation

### P1 — Useful

* Budgets
* Reports
* Search/filter
* Transfer between accounts

### P2 — Later

* Export CSV
* Export PDF
* Recurring transactions
* Dark mode
* Import bank statements
* Financial goals
* Mobile/PWA

---

# 22. Explicitly Out of Scope

Do **not** implement these in MVP:

```text
❌ Double-entry accounting
❌ Invoice
❌ Customer management
❌ Payroll
❌ Inventory
❌ Tax management
❌ Multi-company
❌ Multi-branch
❌ Complex permissions
❌ Financial forecasting
❌ Investment portfolio management
❌ Payment gateway
❌ Bank API integration
❌ Microservices
❌ Event-driven architecture
```

---

# 23. MVP Definition of Done

The MVP is complete when a user can:

1. Register/login.
2. Create a bank/cash/e-wallet account.
3. Create income and expense categories.
4. Add income.
5. Add expenses.
6. Transfer money between accounts.
7. See current total balance.
8. See monthly income and expenses.
9. See spending by category.
10. Set a monthly category budget.
11. See budget usage.
12. Filter transaction history by date/category/type.

---

# 24. Final Product Concept

The application should feel closer to:

```text
        PERSONAL FINANCE
              │
     ┌────────┴────────┐
     │                 │
   MONEY            CONTROL
     │                 │
 ┌───┴────┐       ┌────┴─────┐
 │        │       │          │
Income  Expense  Budget    Reports
 │        │
 └────┬───┘
      │
   Accounts
```

**The core loop is simply:**

```text
Add Income
     ↓
Add Expense
     ↓
Track Balance
     ↓
Check Budget
     ↓
Understand Spending
```

This keeps the application small enough for a **FastAPI + Svelte personal project**, while leaving a clean path for later features without prematurely building an ERP/accounting system.
