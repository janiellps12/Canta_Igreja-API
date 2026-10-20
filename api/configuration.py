import os


class Configuration:
    google_client_id_android = os.environ.get(
        'GOOGLE_CLIENT_ID',
        '1065907842958-nsjjc70td56vaan40kr754qfcp066ui2.apps.googleusercontent.com'
    )
    google_client_id_web = os.environ.get(
        'GOOGLE_CLIENT_ID_WEB',
        '1065907842958-l3qvn1ep06hu68u0pj5uu55guolaf60m.apps.googleusercontent.com'
    )

    posgres_path = os.environ.get('POSTGRES_PATH',
                                  'postgresql://admin:admin@localhost:5432/canta_igreja')
    sentry_dsn = os.environ.get('SENTRY_DSN')

    cors = ["https://canta.app", "https://livreto.canta.app", "https://meu.canta.app"] if os.environ.get('VERCEL_GIT_COMMIT_REF', None) == "main" else \
           (r"(https://preview\.canta\.app)"
            r"|(https://preview\.meu\.canta\.app)"
            r"|(https://\w[\w\-]*-srmourasilvas-projects\.vercel\.app)"
            r"|(http://localhost:4321)"
            r"|(http://localhost:5173)")
