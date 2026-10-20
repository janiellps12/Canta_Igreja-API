import datetime

from nanoid import non_secure_generate

from sqlalchemy import text

from api.v1.data.model.conta import Conta
from api.v1.data.rest.repertorio_rest import RepertorioRequest, ContaReference, RepertorioResponse


class RepertorioRepository:
    def __init__(self, db):
        self.db = db

    def create(self, conta: Conta, repertorio: RepertorioRequest):
        query = text("""
        INSERT INTO repertorio.repertorio (slug, repertorio, criado_por)
             VALUES (:slug, :repertorio, :criado_por)
          RETURNING criado_em
        """)

        parametros = {
            "slug": non_secure_generate(size=10),
            "repertorio": repertorio.model_dump_json(),
            "criado_por": conta.id,
        }

        with self.db.engine.connect() as connection:
            result = connection.execute(query, parametros)
            connection.commit()

        data = result.fetchone()[0]
        return RepertorioResponse(
            slug=parametros["slug"],
            conta=ContaReference(nome=conta.nome, slug=conta.slug),
            criado_em=data.isoformat() if data is not None else None,
            atualizado_em=None,
            **repertorio.model_dump(),
        )

    def select_repertorio_publico(self, conta_slug, repertorio_slug):
        query = text("""
        SELECT repertorio.repertorio, repertorio.criado_em, repertorio.atualizado_em,
               conta.nome as conta_nome
          FROM repertorio.repertorio
          JOIN auth.conta ON (repertorio.criado_por = conta.id)
         WHERE conta.slug = :conta_slug
           AND repertorio.slug = :repertorio_slug
           AND repertorio.estado = 'publico'
         LIMIT 1
        """)

        with self.db.engine.connect() as connection:
            result = connection.execute(query, {
                "conta_slug": conta_slug,
                "repertorio_slug": repertorio_slug,
            })

        if result.rowcount == 0:
            return None

        response = result.mappings().all()[0]

        return RepertorioResponse(
            slug=repertorio_slug,
            conta=ContaReference(nome=response['conta_nome'], slug=conta_slug),
            **response['repertorio'],
            criado_em=response['criado_em'].isoformat() if response['criado_em'] is not None else None,
            atualizado_em=response['atualizado_em'].isoformat() if response['atualizado_em'] is not None else None,
        )

    def update(self, conta: Conta, repertorio_slug: str, repertorio: RepertorioRequest):
        query = text("""
           UPDATE repertorio.repertorio
              SET repertorio=:repertorio,
                  atualizado_em=now()
            WHERE criado_por = :id_conta
              AND repertorio.slug = :slug
        RETURNING criado_em, atualizado_em
        """)

        parametros = {
            "id_conta": conta.id,
            "slug": repertorio_slug,
            "repertorio": repertorio.model_dump_json()
        }

        with self.db.engine.connect() as connection:
            result = connection.execute(query, parametros)
            connection.commit()

        if result.rowcount == 0:
            return None

        criado_em, atualizado_em = result.fetchone()

        return RepertorioResponse(
            **repertorio.model_dump(),
            slug=repertorio_slug,
            conta=ContaReference(nome=conta.nome, slug=conta.slug),
            criado_em=criado_em.isoformat() if criado_em is not None else None,
            atualizado_em=atualizado_em.isoformat() if atualizado_em is not None else None,
        )
