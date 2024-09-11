from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from apps.authentication.models.user_model import User, auth
from apps.authentication.models.role_model import Role

user_namespace = Namespace('Users (Admin-Panel)', description="User Management Operations for Admins | Create User API can be used at both end ")

# Define Swagger models for request validation
user_request_model = user_namespace.model('UserRequest', {
    'username': fields.String(required=True, description='The username'),
    'password': fields.String(required=True, description='The user password'),
    'role_ids': fields.List(fields.Integer, description='List of role IDs assigned to the user')
})

# Define Swagger models for response serialization
user_response_model = user_namespace.model('UserResponse', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a user'),
    'is_superadmin': fields.Boolean(readOnly=True, description='Check if'),
    'username': fields.String(description='Whether the user is superadmin'),
    'roles': fields.List(fields.Nested(user_namespace.model('RoleResponse', {
        'id': fields.Integer(readOnly=True, description='The unique identifier of a role'),
        'name': fields.String(description='The role name'),
    })), description='List of roles assigned to the user')
})


delete_users_model = user_namespace.model('DeleteUsers', {
    'user_ids': fields.List(fields.Integer, required=True, description='List of user IDs to delete')
})


@user_namespace.route('/')
class UserList(Resource):
    @user_namespace.marshal_list_with(user_response_model)
    @auth('user_list')
    def get(self):
        """List all users with their roles"""
        users = User.query.all()
        return users  # `marshal_list_with` handles serialization

    @user_namespace.expect(user_request_model, validate=True)
    @auth('user_create')
    def post(self):
        """Create a new user"""
        data = request.get_json()
        username = data['username']
        password = data['password']
        role_ids = data.get('role_ids', [])

        if User.query.filter_by(username=username).first():
            return {'message': 'Username already exists'}, 409

        # Check if all provided roles exist
        existing_roles = Role.query.filter(Role.id.in_(role_ids)).all()
        existing_role_ids = {role.id for role in existing_roles}
        missing_role_ids = set(role_ids) - existing_role_ids

        if missing_role_ids:
            return {'message': f"Roles with IDs {', '.join(map(str, missing_role_ids))} do not exist - Please create role first"}, 400

        # Create and add the new user
        new_user = User.create_user(username=username, password=password)

        # Add roles to the new user
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        new_user.roles.extend(roles)
        db.session.commit()

        return {'message': 'User created successfully'}, 201


@user_namespace.route('/<int:user_id>')
class UserDetail(Resource):
    @user_namespace.marshal_with(user_response_model)
    @auth('user_detail')
    def get(self, user_id):
        """Get a specific user by ID with their roles"""
        user = User.query.get_or_404(user_id)
        user.roles = [role for role in Role.query.filter(Role.users.any(User.id == user.id)).all()]
        return user  # `marshal_with` handles serialization

    @user_namespace.expect(user_request_model, validate=True)
    @auth('user_update')
    def put(self, user_id):
        """Update a specific user by ID"""
        data = request.get_json()
        user = User.query.get_or_404(user_id)
        user.username = data.get('username', user.username)
        if 'password' in data:
            user._password_hash = data['password']  # Update the hashed password

        role_ids = data.get('role_ids', [])
        user.roles = Role.query.filter(Role.id.in_(role_ids)).all()

        db.session.commit()
        return {'message': 'User updated successfully'}, 200


@user_namespace.route('/delete')
class BulkDeleteUsers(Resource):
    @user_namespace.expect(delete_users_model, validate=True)
    @auth('user_delete')
    def delete(self):
        """Single or Bulk delete users by IDs"""
        data = request.get_json()
        user_ids = data['user_ids']

        if not user_ids:
            return {'message': 'No user IDs provided'}, 400

        users = User.query.filter(User.id.in_(user_ids)).all()

        if len(users) != len(user_ids):
            return {'message': 'One or more users not found'}, 404

        # Prevent deletion of users with the 'superadmin' role
        users_to_delete = []
        for user in users:
            if any(role.name == 'superadmin' for role in user.roles):
                return {'message': f'User with ID {user.id} is a superadmin and cannot be deleted'}, 403
            users_to_delete.append(user)

        for user in users_to_delete:
            db.session.delete(user)

        db.session.commit()
        return {'message': 'Users deleted successfully'}, 200
