from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from apps.authentication.models.user_model import User, auth
from apps.authentication.models.role_model import Role
from apps.authentication.controllers.permission_controller import permission_response_model

role_namespace = Namespace('Roles', description="Role Management Operations")

# Define Swagger models for request validation
role_request_model = role_namespace.model('RoleRequest', {
    'name': fields.String(required=True, description='The role name'),
})

assign_role_model = role_namespace.model('AssignRoles', {
    'user_role_assignments': fields.List(fields.Nested(role_namespace.model('UserRoleAssignment', {
        'user_id': fields.Integer(required=True, description='The user ID'),
        'role_ids': fields.List(fields.Integer, required=True, description='List of role IDs'),
    })), description='List of user-role assignments (can be empty for individual assignments)'),
})


# Define Swagger models for response serialization
role_response_model = role_namespace.model('RoleResponse', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a role'),
    'name': fields.String(description='The role name'),
    'permissions': fields.List(fields.Nested(permission_response_model),
                               description='List of permissions associated with the role'),
})

# Define Swagger model for deleting roles
delete_roles_model = role_namespace.model('DeleteRoles', {
    'role_ids': fields.List(fields.Integer, required=True, description='List of role IDs to delete')
})


@role_namespace.route('/')
class RoleList(Resource):
    @role_namespace.marshal_list_with(role_response_model)
    @auth('role_list')
    def get(self):
        """List all roles"""
        roles = Role.query.all()
        for role in roles:
            role.permissions = role.permissions  # Ensure permissions are loaded
        return roles  # `marshal_list_with` handles serialization

    @role_namespace.expect(role_request_model, validate=True)
    @auth('role_create')
    def post(self):
        """Create a new role"""
        data = request.get_json()
        name = data['name']
        if Role.query.filter_by(name=name).first():
            return {'message': 'Role already exists'}, 409
        new_role = Role(name=name)
        db.session.add(new_role)
        db.session.commit()
        return {'message': 'Role created successfully'}, 201


@role_namespace.route('/<int:role_id>')
class RoleDetail(Resource):
    @role_namespace.marshal_with(role_response_model)
    @auth('role_detail')
    def get(self, role_id):
        """Get a specific role by ID"""
        role = Role.query.get_or_404(role_id)
        role.permissions = role.permissions  # Ensure permissions are loaded
        return role  # `marshal_with` handles serialization

    @role_namespace.expect(role_request_model, validate=True)
    @auth('role_update')
    def put(self, role_id):
        """Update a specific role by ID"""
        data = request.get_json()
        role = Role.query.get_or_404(role_id)
        role.name = data['name']
        db.session.commit()
        return {'message': 'Role updated successfully'}, 200


@role_namespace.route('/delete')
class BulkDeleteRoles(Resource):
    @role_namespace.expect(delete_roles_model, validate=True)
    @auth('role_delete')
    def delete(self):
        """Single or Bulk delete roles by ID"""
        data = request.get_json()
        role_ids = data['role_ids']

        if not role_ids:
            return {'message': 'No role IDs provided'}, 400

        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        if len(roles) != len(role_ids):
            return {'message': 'One or more roles not found'}, 404

        for role in roles:
            db.session.delete(role)

        db.session.commit()
        return {'message': 'Roles deleted successfully'}, 200


@role_namespace.route('/assign-roles')
class AssignRoles(Resource):
    @role_namespace.expect(assign_role_model, validate=True)
    @auth('role_assign')
    def post(self):
        """Assign roles to one or multiple users"""
        data = request.get_json()
        user_role_assignments = data.get('user_role_assignments', [])

        def is_valid_id(id):
            return id > 0

        def are_valid_role_ids(ids):
            return all(is_valid_id(role_id) for role_id in ids)

        def process_assignment(user_id, role_ids):
            if not is_valid_id(user_id) or not are_valid_role_ids(role_ids):
                return {'message': 'Invalid data provided'}, 400

            user = User.query.get(user_id)
            if not user:
                return {'message': f'User with ID {user_id} not found'}, 404

            roles = Role.query.filter(Role.id.in_(role_ids)).all()
            if len(roles) != len(role_ids):
                return {'message': f'One or more roles not found for user {user_id}'}, 404

            user.roles = roles
            db.session.commit()
            return {'message': f'Roles assigned successfully to user with ID {user_id}'}, 200

        if user_role_assignments:
            for assignment in user_role_assignments:
                user_id = assignment.get('user_id')
                role_ids = assignment.get('role_ids')

                response = process_assignment(user_id, role_ids)
                if response[1] != 200:
                    return response

            return {'message': 'Roles assigned successfully to all users'}, 200

        return {'message': 'No valid data provided for role assignment'}, 400








