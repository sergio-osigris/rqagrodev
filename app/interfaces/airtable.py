import os
from dotenv import load_dotenv
import asyncpg
from threading import Lock
from typing import List, Dict, Any
from app.models.fitosanitario import Fitosanitario
from app.models.user import User
from app.models.record import Record
# Load environment variables
load_dotenv()

class PostgresClient:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PostgresClient, cls).__new__(cls)
                cls._instance._pool = None
            return cls._instance

    async def initialize(self):
        """Create a connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                user=os.getenv("PG_USER"),
                password=os.getenv("PG_PASSWORD"),
                database=os.getenv("PG_DATABASE"),
                host=os.getenv("PG_HOST"),
                port=os.getenv("PG_PORT", 5432),
                min_size=1,
                max_size=10,
                statement_cache_size=0  # ✅ Disable prepared statement cache
            )

    async def read_users(self) -> List[User]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM crm_contacts")
            return [User(**dict(row)).dict() for row in rows]

    async def read_records(self) -> List[Record]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM rqagro")
            # print(rows)
            # return [Record(**dict(row)).dict() for row in rows]
            return [dict(row) for row in rows]

    async def find_user(self, phone_number: str) -> List[Dict[str, Any]]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM crm_contacts WHERE phone = $1",
                phone_number
            )
            return [dict(row) for row in rows]

    async def create_record(
        self, user_id: str, incident_type: str, treatment: str, problem: str,
        amount: str, location: str, size: int, date: str, caldo: str, aplicador: str,name: str = "",parcelas:str =""
    ) -> Dict[str, Any]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO rqagro (
                    user_id,
                    "Tipo de incidencia",
                    "Tratamiento/ fertilizante / labor",
                    "Problema en campo",
                    "Dosis",
                    "Cultivo",
                    "Superficie",
                    "Fecha",
                    "Caldo",
                    "Aplicador",
                    "Nombre",
                    "parcelas"
                )
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
                RETURNING *
                """,
                user_id, incident_type, treatment, problem,
                amount, location, size, date, caldo, aplicador,name,parcelas
            )

            return dict(row)
        
    async def read_fitosanitarios(self) -> List[Fitosanitario]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM fitosanitarios")
            return [Fitosanitario(**dict(row)).dict() for row in rows]


if __name__ == "__main__":
    import asyncio
    import datetime
    async def main():
        client = PostgresClient()
        await client.initialize()
        # print("Fetching fitosanitarios from the database...")
        # fitosanitarios = await client.read_fitosanitarios()
        # for fitosanitario in fitosanitarios:
        #     print(fitosanitario)
        # print("Fetching users from the database...")
        # users = await client.read_users()
        # for user in users:
        #     print(user)
        #     break

        print("Fetching records from the database...")
        records = await client.read_records()
        print(records[-1])
        # for record in records:
        #     print(record)
        #     break

        # print("Generating random record")
        # await client.create_record(user_id = str(users[0]['id']), incident_type="prueba", treatment="Prueba", problem="prr",
        # amount="560", location="ss", size="5", date=datetime.datetime.now(), caldo="23", aplicador="WW",name=users[0]['name'])

    asyncio.run(main())