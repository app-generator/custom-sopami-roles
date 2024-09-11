from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify, make_response
import logging

logger = logging.getLogger(__name__)


# User model
class User(db.Model):
    __tablename__ = 'users'  # Set the table name to 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column('password', db.String(120), nullable=False)  # Store hashed password
    is_superadmin = db.Column(db.Boolean, default=False)  # Field for SuperAdmin status
    roles = db.relationship('Role', secondary='user_roles', back_populates='users')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, raw_password):
        self._password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self._password_hash, raw_password)

    @classmethod
    def create_user(cls, username, password, is_superadmin=False):
        if cls.query.filter_by(username=username).first():
            raise ValueError('Username already exists')

        new_user = cls(username=username, is_superadmin=is_superadmin)
        new_user.password = password
        new_user.save()
        return new_user

    def save(self):
        db.session.add(self)
        db.session.commit()

    def has_permission(self, permission_name):
        if self.is_superadmin:
            return True
        for role in self.roles:
            print("role----", role.id)

            for permission in role.permissions:
                print("permission----", permission)

                if permission.name == permission_name:
                    return True
        return False

    @classmethod
    def create_temporary_superadmin(cls):
        super_admin = cls.query.filter_by(is_superadmin=True).first()
        if not super_admin:
            try:
                # You can set default username and password for the temporary SuperAdmin
                super_admin = cls.create_user(username="superadmin", password="superpassword", is_superadmin=True)
                print("Temporary SuperAdmin created.")
            except ValueError as e:
                print(f"Failed to create SuperAdmin: {e}")
        else:
            print("SuperAdmin already exists.")


# Check user login and as well permissions
def auth(permission_name):
    def decorator(f):
        @jwt_required()  # Step1. Ensure the user is authenticated
        @wraps(f)
        # Step2. Check permissions
        def check_permission(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            print("1----------------------", user.has_permission(permission_name))
            if not user or not user.has_permission(permission_name):
                response = jsonify({'message': 'You do not have permission to access this resource'})
                return make_response(response, 403)
            return f(*args, **kwargs)

        return check_permission

    return decorator




# Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNjA2MTc2OCwianRpIjoiMjc1ODk2NWMtYTExNS00YjQxLWJiZjgtNWM2MTUyM2M0N2NiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzI2MDYxNzY4LCJjc3JmIjoiNWMyY2UzMzMtM2NhMi00ZjRmLWExNmEtMWEzZDNhZTJhOGRjIiwiZXhwIjoxNzI2MTQ4MTY4fQ.Y4VFtPVoxKT5MYpuux4pFZP4_qLuyIgDx7MFb_AmVao

# Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcyNjA3OTYxMSwianRpIjoiOTUyMDIyNjUtM2MyZS00OTIyLTk2YWItZWZhMTE0Mzk3NDZlIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MiwibmJmIjoxNzI2MDc5NjExLCJjc3JmIjoiOGQ4NzExODUtZjZmNi00ZmYzLTllZWMtMDM1M2I5NjUwMGVmIiwiZXhwIjoxNzI2MTY2MDExfQ.gJ5s2Ke081vjx5Tbo0_iBcQm6utb3hTGSbU-OaWuwXA