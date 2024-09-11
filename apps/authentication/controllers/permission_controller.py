from flask_restx import Namespace, Resource, fields
from flask import request
from extensions import db
from apps.authentication.models.permission_model import Permission
from apps.authentication.models.role_model import Role
from apps.authentication.models.user_model import User, auth

permission_namespace = Namespace('Permissions (Admin-Panel)', description="Permission Management Operations for Admins")

# Define Swagger models for request validation
permission_request_model = permission_namespace.model('PermissionRequest', {
    'name': fields.String(required=True, description='The name of the permission'),
    'description': fields.String(description='A brief description of the permission')
})

assign_permission_model = permission_namespace.model('AssignPermissions', {
    'role_permission_assignments': fields.List(fields.Nested(permission_namespace.model('RolePermissionAssignment', {
        'role_id': fields.Integer(required=True, description='The role ID'),
        'permission_ids': fields.List(fields.Integer, required=True, description='List of permission IDs'),
    })), description='List of role-permission assignments'),
})


# Define Swagger models for response serialization
permission_response_model = permission_namespace.model('PermissionResponse', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a permission'),
    'name': fields.String(description='The name of the permission'),
    'description': fields.String(description='A brief description of the permission')
})

delete_permissions_model = permission_namespace.model('DeletePermissions', {
    'permission_ids': fields.List(fields.Integer, required=True, description='List of permission IDs to delete')
})

@permission_namespace.route('/')
class PermissionList(Resource):
    @permission_namespace.marshal_list_with(permission_response_model)
    @auth('permission_list')
    def get(self):
        """List all permissions"""
        permissions = Permission.query.all()
        return permissions

    @permission_namespace.expect(permission_request_model, validate=True)
    @permission_namespace.response(201, 'Permission created successfully')
    @auth('permission_create')
    def post(self):
        """Create a new permission"""
        data = request.get_json()
        name = data['name']
        description = data.get('description', '')

        if Permission.query.filter_by(name=name).first():
            return {'message': 'Permission already exists'}, 409

        new_permission = Permission(name=name, description=description)
        db.session.add(new_permission)
        db.session.commit()
        return {'message': 'Permission created successfully'}, 201


@permission_namespace.route('/<int:id>')
class PermissionDetail(Resource):
    @permission_namespace.marshal_with(permission_response_model)
    @auth('permission_detail')
    def get(self, id):
        """Fetch a permission by ID"""
        permission = Permission.query.get_or_404(id)
        return permission

    @permission_namespace.expect(permission_request_model, validate=True)
    @permission_namespace.response(200, 'Permission updated successfully')
    @auth('permission_update')
    def put(self, id):
        """Update a permission"""
        data = request.get_json()
        permission = Permission.query.get_or_404(id)
        permission.name = data['name']
        permission.description = data.get('description', permission.description)
        db.session.commit()
        return {'message': 'Permission updated successfully'}, 200


@permission_namespace.route('/delete')
class BulkDeletePermissions(Resource):
    @permission_namespace.expect(delete_permissions_model, validate=True)
    @auth('permission_delete')
    def delete(self):
        """Single or Bulk delete permissions by ID"""
        data = request.get_json()
        permission_ids = data['permission_ids']

        if not permission_ids:
            return {'message': 'No permission IDs provided'}, 400

        permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()

        if len(permissions) != len(permission_ids):
            return {'message': 'One or more permissions not found'}, 404

        for permission in permissions:
            db.session.delete(permission)

        db.session.commit()
        return {'message': 'Permissions deleted successfully'}, 200


@permission_namespace.route('/assign-permissions')
class AssignPermissions(Resource):
    @permission_namespace.expect(assign_permission_model, validate=True)
    @permission_namespace.response(200, 'Permissions assigned successfully')
    @auth('permission_assign')
    def post(self):
        """Assign permissions to one or multiple roles"""
        data = request.get_json()
        role_permission_assignments = data.get('role_permission_assignments', [])

        def is_valid_id(id):
            return id > 0

        def are_valid_permission_ids(ids):
            return all(is_valid_id(permission_id) for permission_id in ids)

        def process_assignment(role_id, permission_ids):
            if not is_valid_id(role_id) or not are_valid_permission_ids(permission_ids):
                return {'message': 'Invalid data provided'}, 400

            role = Role.query.get(role_id)
            if not role:
                return {'message': f'Role with ID {role_id} not found'}, 404

            permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
            if len(permissions) != len(permission_ids):
                return {'message': f'One or more permissions not found for role with ID {role_id}'}, 404

            role.permissions = permissions
            db.session.commit()
            return {'message': f'Permissions assigned successfully to role with ID {role_id}'}, 200

        if role_permission_assignments:
            for assignment in role_permission_assignments:
                role_id = assignment.get('role_id')
                permission_ids = assignment.get('permission_ids')

                response = process_assignment(role_id, permission_ids)
                if response[1] != 200:
                    return response

            return {'message': 'Permissions assigned successfully to all roles'}, 200

        return {'message': 'No valid data provided for permission assignment'}, 400


