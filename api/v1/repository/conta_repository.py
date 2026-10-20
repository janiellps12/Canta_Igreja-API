from typing import Optional

from nanoid import generate
from sqlalchemy import text

from api.v1.data.model.conta import Conta


class ContaRepository:
    def __init__(self, db):
        self.db = db

    def find_by(self, subject) -> Optional[Conta]:
        query = text("""
        SELECT id, slug, email, nome, subject, provider
          FROM auth.conta
         WHERE conta.subject = :subject
         LIMIT 1
        """)

        with self.db.engine.connect() as connection:
            result = connection.execute(query, {"subject": subject})

        if result.rowcount == 0:
            return None

        return Conta(**result.mappings().all()[0])

    def create(self, subject: str, email: str, nome: str) -> Conta:
        query = text("""
        INSERT INTO auth.conta (slug, email, nome, subject)
             VALUES (:slug, :email, :nome, :subject)
          RETURNING id
        """)

        conta = {
            "slug": generate(size=10),
            "email": email,
            "nome": nome,
            "subject": subject,
            "provider": "google_api"
        }

        with self.db.engine.connect() as connection:
            result = connection.execute(query, conta)
            connection.commit()

        return Conta(
            id=result.fetchone()[0],
            **conta
        )
