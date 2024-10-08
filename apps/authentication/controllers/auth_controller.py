from flask_restx import Namespace, Resource, fields
from flask import request
from apps.authentication.models.user_model import User
from flask_jwt_extended import create_access_token, jwt_required

auth_namespace = Namespace('Auth (Both Admin-Panel & Frontend)', description="Authentication Operations")

# Define Swagger models for request validation
user_request_model = auth_namespace.model('UserRequest', {
    'username': fields.String(required=True, description='The username'),
    'password': fields.String(required=True, description='The password'),
})

login_request_model = auth_namespace.model('LoginRequest', {
    'username': fields.String(required=True, description='The username'),
    'password': fields.String(required=True, description='The password'),
})

# Define Swagger models for response serialization
access_token_response_model = auth_namespace.model('AccessTokenResponse', {
    'access_token': fields.String(description='The access token for authentication'),
})


@auth_namespace.route('/login')
class Login(Resource):
    @auth_namespace.expect(login_request_model, validate=True)
    def post(self):
        """Login - use username=superadmin and password=superpassword for a dummy superuser"""
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Validate input data
        if not username or not password:
            return {'message': 'Username and password are required'}, 400

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            try:
                access_token = create_access_token(identity=user.id)
                if access_token:
                    return {'access_token': access_token}, 200
                else:
                    return {'message': 'Failed to generate access token'}, 500
            except Exception as e:
                return {'message': f'An error occurred while generating the access token: {str(e)}'}, 500

        return {'message': 'Invalid username or password. Please check your credentials and try again.'}, 401


