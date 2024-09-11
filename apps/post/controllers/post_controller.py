from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from apps.authentication.models.user_model import User, auth
from apps.post.models.post_model import Post

post_namespace = Namespace('Posts (Can Mimic a Frontend and Admin Both)', description="Operations related to posts")

# Define the post model for request validation
post_request_model = post_namespace.model('PostRequest', {
    'title': fields.String(required=True, description='The title of the post'),
    'content': fields.String(required=True, description='The content of the post'),
})

# Define the post model for response serialization
post_response_model = post_namespace.model('PostResponse', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of a post'),
    'title': fields.String(description='The title of the post'),
    'content': fields.String(description='The content of the post'),
    'author_id': fields.Integer(description='The ID of the post author'),
    'created_at': fields.DateTime(description='The creation date of the post')
})

@post_namespace.route('/')
class PostList(Resource):
    @auth('post_list')
    @post_namespace.marshal_list_with(post_response_model)
    def get(self):
        """Get all posts"""
        posts = Post.query.all()
        return posts  # `marshal_list_with` handles serialization

    @post_namespace.expect(post_request_model, validate=True)
    @auth('post_create')
    def post(self):
        """Create a new post"""
        data = request.get_json()
        user_id = get_jwt_identity()

        new_post = Post(
            title=data['title'],
            content=data['content'],
            author_id=user_id
        )
        db.session.add(new_post)
        db.session.commit()
        return {'message': 'Post created successfully'}, 201


@post_namespace.route('/<int:post_id>')
class PostDetail(Resource):
    @auth('post_detail')
    @post_namespace.marshal_with(post_response_model)
    def get(self, post_id):
        """Get a specific post by ID"""
        post = Post.query.get_or_404(post_id)
        return post  # `marshal_with` handles serialization

    @post_namespace.expect(post_request_model, validate=True)
    @auth('post_update')
    def put(self, post_id):
        """Update a post"""
        post = Post.query.get_or_404(post_id)
        data = request.get_json()

        post.title = data['title']
        post.content = data['content']
        db.session.commit()

        return {'message': 'Post updated successfully'}, 200

    @auth('post_delete')
    def delete(self, post_id):
        """Delete a post"""
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()

        return {'message': 'Post deleted successfully'}, 200
