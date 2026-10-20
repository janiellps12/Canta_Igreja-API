from typing import Optional, Tuple

from google.auth.exceptions import InvalidValue
from google.auth.transport import requests
from google.oauth2 import id_token
from werkzeug.exceptions import Unauthorized, Forbidden

from api.configuration import Configuration
from api.v1.data.model.conta import Conta
from api.v1.repository.conta_repository import ContaRepository


class AuthService:
    def __init__(self, db):
        self.repository = ContaRepository(db)

    def auth(self, authorization: str, origin: Optional[str]) -> Conta:
        subject, email, nome = self._parse(authorization, origin)

        conta = self.repository.find_by(subject)
        if conta is not None:
            return conta

        if conta is None and email is not None and nome is not None:
            return self.repository.create(subject, email, nome)

        raise Unauthorized()

    def _parse(self, authorization, origin: Optional[str]) -> Tuple[str, Optional[str], Optional[str]]:
        _, account_id_token = authorization.split(' ', maxsplit=2)

        try:
            token_data: dict = id_token.verify_oauth2_token(
                account_id_token,
                requests.Request(),
                Configuration.google_client_id_web if origin == 'web' else Configuration.google_client_id_android
            )
            return token_data['sub'], token_data.get('email', None), token_data.get('name', None)
        except InvalidValue as e:
            raise Forbidden('Invalid token')
