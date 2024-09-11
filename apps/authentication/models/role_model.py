from extensions import db


class Role(db.Model):
    __tablename__ = 'roles'  # Explicitly set the table name to 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    users = db.relationship('User', secondary='user_roles', back_populates='roles')
    permissions = db.relationship('Permission', secondary='role_permissions', back_populates='roles')


# Association tables
user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer, db.ForeignKey('users.id')),  # Reference to 'users' table
                      db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))  # Updated reference to 'roles' table
                      )

role_permissions = db.Table('role_permissions',
                            db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),  # Reference to 'roles' table
                            db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
                            )
