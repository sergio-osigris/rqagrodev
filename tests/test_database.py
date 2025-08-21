import pytest
import datetime
from unittest.mock import AsyncMock
from app.interfaces.airtable import PostgresClient  # Adjust path if renamed

@pytest.fixture
async def postgres_client():
    client = PostgresClient()
    client._pool = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_read_users(postgres_client):
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [
        {"user_id": "abc123", "name": "John Doe"}
    ]
    postgres_client._pool.acquire.return_value.__aenter__.return_value = mock_conn

    users = await postgres_client.read_users()

    assert isinstance(users, list)
    assert users[0]["name"] == "John Doe"
    mock_conn.fetch.assert_called_once_with("SELECT * FROM crm_contacts")

@pytest.mark.asyncio
async def test_read_records(postgres_client):
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [
        {"id": "rec123", "Tipo de incidencia": "Plaga"}
    ]
    postgres_client._pool.acquire.return_value.__aenter__.return_value = mock_conn

    records = await postgres_client.read_records()

    assert isinstance(records, list)
    assert records[0]["Tipo de incidencia"] == "Plaga"
    mock_conn.fetch.assert_called_once_with("SELECT * FROM rqagro")

@pytest.mark.asyncio
async def test_find_user(postgres_client):
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [
        {"user_id": "abc123", "phone": "123456789"}
    ]
    postgres_client._pool.acquire.return_value.__aenter__.return_value = mock_conn

    result = await postgres_client.find_user("123456789")

    assert len(result) == 1
    assert result[0]["phone"] == "123456789"
    mock_conn.fetch.assert_called_once_with(
        "SELECT * FROM crm_contacts WHERE phone = $1", "123456789"
    )

@pytest.mark.asyncio
async def test_create_record(postgres_client):
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {
        "id": "rec999", "user_id": "usr123", "Caldo": 23
    }
    postgres_client._pool.acquire.return_value.__aenter__.return_value = mock_conn

    result = await postgres_client.create_record(
        user_id="usr123",
        incident_type="Weed Control",
        treatment="Herbicide",
        problem="Overgrowth",
        amount="1L",
        location="Field A",
        size="10",
        date=datetime.date.today(),
        caldo=23,
        aplicador="Manolo"
    )

    assert isinstance(result, dict)
    assert result["user_id"] == "usr123"
    assert result["Caldo"] == 23
    mock_conn.fetchrow.assert_called_once()
