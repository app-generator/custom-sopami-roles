from flask import Flask
from extensions import init_extensions, db, api
from apps.authentication.controllers.auth_controller import auth_namespace
from apps.authentication.controllers.role_controller import role_namespace
from apps.authentication.controllers.permission_controller import permission_namespace
from apps.authentication.controllers.user_controller import user_namespace
from apps.post.controllers.post_controller import post_namespace
from apps.authentication.models.user_model import User
from utils.exceptions import register_error_handlers  # Import your error handlers
def create_app():
    app = Flask(__name__)
    # Initialize extensions with app
    init_extensions(app)
    # Register error handlers
    register_error_handlers(api)
    # Register blueprints/routes
    api.add_namespace(auth_namespace, path='/api/v1/auth')
    api.add_namespace(user_namespace, path='/api/v1/users')
    api.add_namespace(role_namespace, path='/api/v1/roles')
    api.add_namespace(permission_namespace, path='/api/v1/permissions')
    api.add_namespace(post_namespace, path='/api/v1/posts')
    # app.register_blueprint(post_blueprint, url_prefix='/posts')
    # Create database tables
    with app.app_context():
        db.create_all()
        User.create_temporary_superadmin()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
