from flask_restx import Api
from werkzeug.exceptions import BadRequest, NotFound
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTExtendedException
import jwt  # Import the jwt module for DecodeError and ExpiredSignatureError

api = Api()  # Define your Api instance

def handle_bad_request(e):
    return {'message': 'Bad request: {}'.format(e.description)}, 400

def handle_not_found(e):
    return {'message': 'Resource not found: {}'.format(e.description)}, 404

def handle_internal_server_error(e):
    return {'message': 'An unexpected error occurred'}, 500

def handle_sqlalchemy_error(e):
    return {'message': 'Database error: {}'.format(str(e))}, 500

def handle_no_authorization_error(e):
    return {'message': 'Authentication required'}, 401

def handle_jwt_extended_exception(e):
    return {'message': 'JWT error: {}'.format(str(e))}, 401

def handle_jwt_decode_error(e):
    return {'message': 'Invalid token'}, 401

def handle_jwt_expired_signature_error(e):
    return {'message': 'Token has expired'}, 401

def register_error_handlers(api):
    api.errorhandler(BadRequest)(handle_bad_request)
    api.errorhandler(NotFound)(handle_not_found)
    api.errorhandler(SQLAlchemyError)(handle_sqlalchemy_error)
    api.errorhandler(NoAuthorizationError)(handle_no_authorization_error)
    api.errorhandler(JWTExtendedException)(handle_jwt_extended_exception)
    api.errorhandler(jwt.exceptions.DecodeError)(handle_jwt_decode_error)
    api.errorhandler(jwt.exceptions.ExpiredSignatureError)(handle_jwt_expired_signature_error)
    api.errorhandler(Exception)(handle_internal_server_error)
