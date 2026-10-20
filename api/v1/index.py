from api.v1.routes.routes import routes


def init(app, db):
    routes(app, db)
