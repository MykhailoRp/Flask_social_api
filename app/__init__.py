from threading import Timer
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from time import time

db = SQLAlchemy(session_options={"autoflush": False})


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    def clear_expired_tokens():
        with app.app_context():
            expired_tokens = models.Token.query.filter(models.Token.expires < int(round(time()))).all()

            for t in expired_tokens:
                db.session.delete(t)

            db.session.commit()

        timer = Timer(60, clear_expired_tokens)
        timer.daemon = True
        timer.start()

    from app.back import bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    clear_expired_tokens()

    return app


from app import models