def _setup(auth_client):
    acc = auth_client.post(
        "/api/accounts",
        json={"name": "BCA", "type": "bank", "initial_balance": 1000000},
    ).json()
    acc2 = auth_client.post(
        "/api/accounts",
        json={"name": "GoPay", "type": "e-wallet", "initial_balance": 0},
    ).json()
    cats = auth_client.get("/api/categories").json()
    food = next(c for c in cats if c["name"] == "Food")
    salary = next(c for c in cats if c["name"] == "Salary")
    return acc, acc2, food, salary


def test_transactions_and_balance(auth_client):
    acc, _acc2, food, salary = _setup(auth_client)
    tx = auth_client.post(
        "/api/transactions",
        json={
            "type": "expense",
            "amount": 50000,
            "category_id": food["id"],
            "account_id": acc["id"],
            "description": "Lunch",
            "transaction_date": "2026-09-23",
        },
    )
    assert tx.status_code == 201
    auth_client.post(
        "/api/transactions",
        json={
            "type": "income",
            "amount": 12000000,
            "category_id": salary["id"],
            "account_id": acc["id"],
            "description": "Salary",
            "transaction_date": "2026-09-01",
        },
    )
    wrong = auth_client.post(
        "/api/transactions",
        json={
            "type": "expense",
            "amount": 1000,
            "category_id": salary["id"],
            "account_id": acc["id"],
            "transaction_date": "2026-09-01",
        },
    )
    assert wrong.status_code == 400

    accounts = auth_client.get("/api/accounts").json()
    bca = next(a for a in accounts if a["name"] == "BCA")
    assert bca["balance"] == 1000000 - 50000 + 12000000

    filtered = auth_client.get("/api/transactions", params={"type": "expense", "q": "lunch"}).json()
    assert len(filtered) == 1
    updated = auth_client.put(f"/api/transactions/{filtered[0]['id']}", json={"amount": 60000})
    assert updated.status_code == 200 and updated.json()["amount"] == 60000
    deleted = auth_client.delete(f"/api/transactions/{filtered[0]['id']}")
    assert deleted.status_code == 200
    assert auth_client.get("/api/transactions").json() == [] or all(
        t["id"] != filtered[0]["id"] for t in auth_client.get("/api/transactions").json()
    )


def test_transfer_moves_money(auth_client):
    acc, acc2, _food, _salary = _setup(auth_client)
    resp = auth_client.post(
        "/api/transfers",
        json={
            "from_account_id": acc["id"],
            "to_account_id": acc2["id"],
            "amount": 250000,
            "transfer_date": "2026-09-20",
        },
    )
    assert resp.status_code == 201
    same = auth_client.post(
        "/api/transfers",
        json={
            "from_account_id": acc["id"],
            "to_account_id": acc["id"],
            "amount": 1,
            "transfer_date": "2026-09-20",
        },
    )
    assert same.status_code == 400
    accounts = auth_client.get("/api/accounts").json()
    assert next(a for a in accounts if a["id"] == acc["id"])["balance"] == 750000
    assert next(a for a in accounts if a["id"] == acc2["id"])["balance"] == 250000
    total = auth_client.get("/api/dashboard").json()["balance"]
    assert total == 1000000


def test_budget_and_dashboard(auth_client):
    acc, _acc2, food, salary = _setup(auth_client)
    auth_client.post(
        "/api/transactions",
        json={
            "type": "expense",
            "amount": 300000,
            "category_id": food["id"],
            "account_id": acc["id"],
            "transaction_date": "2026-09-23",
        },
    )
    from datetime import date

    today = date.today()
    budget = auth_client.post(
        "/api/budgets",
        json={
            "category_id": food["id"],
            "month": today.month,
            "year": today.year,
            "amount": 1500000,
        },
    )
    assert budget.status_code == 201
    b = budget.json()
    assert b["spent"] == 300000
    assert b["remaining"] == 1200000
    assert b["usage_percent"] == 20.0

    dash = auth_client.get("/api/dashboard", params={"period": "month"}).json()
    assert dash["expenses"] >= 300000
    assert dash["savings"] == dash["income"] - dash["expenses"]
    assert len(dash["budgets"]) == 1
    assert dash["expense_by_category"][0]["category_name"] == "Food"

    summary = auth_client.get("/api/reports/summary").json()
    assert "net" in summary
    trend = auth_client.get("/api/reports/trend", params={"months": 3}).json()
    assert len(trend) == 3
