from extensions import db


class Permission(db.Model):
    __tablename__ = 'permissions'  # Explicitly set the table name to 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)  # Add description field
    roles = db.relationship('Role', secondary='role_permissions', back_populates='permissions')

