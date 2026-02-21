"""
Test type: Integration test
Validation: Full API endpoint round-trips against spec examples
Command: pytest test/test_endpoints.py -v
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestParseEndpoint:
    """Integration tests for POST /transactions:parse."""

    def test_spec_example(self, client):
        """Validate parse output matches requirements.md example."""
        response = client.post(
            "/blackrock/challenge/v1/transactions:parse",
            json=[
                {"date": "2023-10-12 20:15:30", "amount": 250},
                {"date": "2023-02-28 15:49:20", "amount": 375},
                {"date": "2023-07-01 21:59:00", "amount": 620},
                {"date": "2023-12-17 08:09:45", "amount": 480},
            ],
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        assert data[0] == {
            "date": "2023-10-12 20:15:30",
            "amount": 250.0,
            "ceiling": 300.0,
            "remanent": 50.0,
        }
        assert data[2] == {
            "date": "2023-07-01 21:59:00",
            "amount": 620.0,
            "ceiling": 700.0,
            "remanent": 80.0,
        }

    def test_empty_list(self, client):
        response = client.post("/blackrock/challenge/v1/transactions:parse", json=[])
        assert response.status_code == 200
        assert response.json() == []


class TestValidatorEndpoint:
    """Integration tests for POST /transactions:validator."""

    def test_spec_example(self, client):
        """Validate validator output matches requirements.md example."""
        response = client.post(
            "/blackrock/challenge/v1/transactions:validator",
            json={
                "wage": 50000,
                "transactions": [
                    {
                        "date": "2023-01-15 10:30:00",
                        "amount": 2000,
                        "ceiling": 300,
                        "remanent": 50,
                    },
                    {
                        "date": "2023-03-20 14:45:00",
                        "amount": 3500,
                        "ceiling": 400,
                        "remanent": 70,
                    },
                    {
                        "date": "2023-06-10 09:15:00",
                        "amount": 1500,
                        "ceiling": 200,
                        "remanent": 30,
                    },
                    {
                        "date": "2023-07-10 09:15:00",
                        "amount": -250,
                        "ceiling": 200,
                        "remanent": 30,
                    },
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["valid"]) == 3
        assert len(data["invalid"]) == 1
        assert data["invalid"][0]["message"] == "Negative amounts are not allowed"


class TestFilterEndpoint:
    """Integration tests for POST /transactions:filter."""

    def test_spec_example(self, client):
        """Validate filter output matches requirements.md example."""
        response = client.post(
            "/blackrock/challenge/v1/transactions:filter",
            json={
                "q": [
                    {
                        "fixed": 0,
                        "start": "2023-07-01 00:00:00",
                        "end": "2023-07-31 23:59:59",
                    }
                ],
                "p": [
                    {
                        "extra": 30,
                        "start": "2023-10-01 00:00:00",
                        "end": "2023-12-31 23:59:59",
                    }
                ],
                "k": [{"start": "2023-01-01 00:00:00", "end": "2023-12-31 23:59:59"}],
                "wage": 50000,
                "transactions": [
                    {"date": "2023-02-28 15:49:20", "amount": 375},
                    {"date": "2023-07-15 10:30:00", "amount": 620},
                    {"date": "2023-10-12 20:15:30", "amount": 250},
                    {"date": "2023-10-12 20:15:30", "amount": 250},
                    {"date": "2023-12-17 08:09:45", "amount": -480},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Duplicate and negative should be invalid
        assert len(data["invalid"]) == 2
        messages = [inv["message"] for inv in data["invalid"]]
        assert "Duplicate transaction" in messages
        assert "Negative amounts are not allowed" in messages


class TestReturnsNPSEndpoint:
    """Integration tests for POST /returns:nps."""

    def test_spec_example(self, client):
        """Validate NPS returns output matches requirements.md example."""
        response = client.post(
            "/blackrock/challenge/v1/returns:nps",
            json={
                "age": 29,
                "wage": 50000,
                "inflation": 5.5,
                "q": [
                    {
                        "fixed": 0,
                        "start": "2023-07-01 00:00:00",
                        "end": "2023-07-31 23:59:59",
                    }
                ],
                "p": [
                    {
                        "extra": 25,
                        "start": "2023-10-01 08:00:00",
                        "end": "2023-12-31 19:59:59",
                    }
                ],
                "k": [
                    {"start": "2023-01-01 00:00:00", "end": "2023-12-31 23:59:59"},
                    {"start": "2023-03-01 00:00:00", "end": "2023-11-30 23:59:59"},
                ],
                "transactions": [
                    {"date": "2023-02-28 15:49:20", "amount": 375},
                    {"date": "2023-07-01 21:59:00", "amount": 620},
                    {"date": "2023-10-12 20:15:30", "amount": 250},
                    {"date": "2023-12-17 08:09:45", "amount": 480},
                    {"date": "2023-12-17 08:09:45", "amount": -10},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["totalTransactionAmount"] == 1725.0
        assert data["totalCeiling"] == 1900.0
        assert len(data["savingsByDates"]) == 2
        assert data["savingsByDates"][0]["amount"] == 145.0
        assert data["savingsByDates"][0]["profit"] == 86.88
        assert data["savingsByDates"][0]["taxBenefit"] == 0.0
        assert data["savingsByDates"][1]["amount"] == 75.0
        assert data["savingsByDates"][1]["profit"] == 44.94


class TestPerformanceEndpoint:
    """Integration tests for GET /performance."""

    def test_returns_metrics(self, client):
        response = client.get("/blackrock/challenge/v1/performance")
        assert response.status_code == 200
        data = response.json()
        assert "time" in data
        assert "MB" in data["memory"]
        assert isinstance(data["threads"], int)
