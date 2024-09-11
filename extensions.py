# -- configuration and extension management in one place for better code management -- #
# Extensions
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
api = Api(
    title="Sopami-Flask APIs",
    version="1.0",
    security='BearerAuth',  # Default security definition for all endpoints
    authorizations={
        'BearerAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
        }
    }
)

jwt = JWTManager()
mail = Mail()


def init_extensions(app):
    # Set configuration directly on the app object
    app.config.update({
        # secrete key
        'SECRET_KEY': 'your_secret_key',
        # flask_jwt_extended
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///sopami-flask.db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        # flask_jwt_extended
        'JWT_SECRET_KEY': 'c847f85238de4896ace70957901f6fb6be6709971547cba8523c1f9d8e236b3a',
        # Replace with your own secret key
        'JWT_ACCESS_TOKEN_EXPIRES': 86400,  # Token expiration time in seconds (24 hours)
        # flask_mail
        'MAIL_SERVER': 'smtp.example.com',
        'MAIL_PORT': 587,
        'MAIL_USERNAME': 'your_email@example.com',
        'MAIL_PASSWORD': 'your_password',
        'MAIL_USE_TLS': True,
        'MAIL_USE_SSL': False
    })

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
