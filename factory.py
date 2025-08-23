from flask import Flask
from celery import Celery, Task


def make_app():
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://redis:6379/0",
            result_backend="redis://redis:6379/0",
        ),
        SQLALCHEMY_DATABASE_URI="sqlite:///images.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    return app

def make_celery(app):
    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            # important : exécuter dans le contexte Flask
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(app.name, task_cls=ContextTask)
    celery.config_from_object(app.config["CELERY"])
    celery.set_default()
    app.extensions["celery"] = celery

    return celery

