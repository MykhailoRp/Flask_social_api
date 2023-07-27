from datetime import datetime
from flask import redirect, url_for, request, jsonify
from app import db
import app.models as models
from app.back import bp as app
from app.authentication import auth_decorators as auth
from app.utility import utility_decorators as util
from app.back import actions
from app.exceptions import post_exceptions as post_exc

from flask import json
from werkzeug.exceptions import HTTPException

api_path = "/api_v1"

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.route(api_path + '/signup', methods = ['POST'])
@util.required_variables({
    "login":str,
    "password":str,
    "username":str,
})
def user_signup(login, password, username):

    if models.User.query.filter(models.User.username == username).first() is not None:
        return jsonify(
            message=f"Username '{username}' is taken",
            code=409
        ), 409

    if models.User.query.filter(models.User.login == login).first() is not None:
        return jsonify(
            message=f"login '{login}' is taken",
            code=409
        ), 409

    new_user = models.User(
        username = username,
        login = login,
    )

    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("main.user_login", login = login, password = password))

@app.route(api_path + '/login', methods = ['POST', 'GET'])
@util.required_variables({
    "login":str,
    "password":str
})
def user_login(login, password):

    log_user = models.User.query.filter_by(login=login).first()

    if log_user is not None:
        res_token = log_user.login_account(login = login, password = password)

        return jsonify(
            token = res_token
        ), 200
    else:
        return jsonify(
            message="User not found",
            code=404
        ), 404

@app.route(api_path + '/logout', methods = ['POST'])
@auth.requires_token
@auth.log_request
@util.required_variables({
    "auth_token":str
})
def user_logout(user, token, auth_token, *args, **kwargs):

    found_token = models.Token.query.get(auth_token)

    if found_token is None:
        return jsonify(
            message="Token not found",
            code=404
        ), 404

    db.session.delete(found_token)
    db.session.commit()

    return jsonify(
            status=True
        ), 200

@app.route(api_path + '/create_post', methods = ['POST'])
@auth.requires_token
@auth.log_request
@util.required_variables({
    "content":str
})
def create_post(user: models.User, content, *args, **kwargs):
    new_post = models.Post(
        user_id = user.id,
        content = content
    )

    db.session.add(new_post)
    db.session.commit()

    return redirect(f"/post/{new_post.id}")

@app.route(api_path + '/post/<int:post_id>/delete', methods = ['DELETE'])
@auth.requires_token
@auth.log_request
def delete_post(post_id, user: models.User, *args, **kwargs):
    post_to_delete = user.posts.filter_by(id = post_id).first()

    if post_to_delete is not None:
        db.session.delete(post_to_delete)
        db.session.commit()
        return jsonify(
            status=True
        ), 200

    return jsonify(
            message="Post not found",
            code=404
    ), 404

@app.route(api_path + '/post/<int:post_id>', methods = ['GET'])
@auth.optional_token
@auth.log_request
def post_info(post_id, *args, **kwargs):

    found_post = models.Post.query.get(post_id)

    if found_post is None: jsonify(
            message="Post not found",
            code=404
        ), 404

    return jsonify(found_post.dict()), 200

@app.route(api_path + '/new_posts', methods = ['GET'])
@auth.optional_token
@auth.log_request
@util.required_variables({
    "limit":int
})
def get_new_posts(limit, *args, **kwargs):

    if limit > 100:
        return jsonify(
            message="Limit can't be more than 100",
            code=401
        ), 401
    if limit <= 0:
        return jsonify(
            message="Limit can't be less than 1",
            code=401
        ), 401

    found_posts = models.Post.query.order_by(models.Post.timestamp).limit(limit).all()

    return jsonify(
        post_number=len(list(found_posts)),
        posts = [
            p.dict() for p in found_posts
        ]
    ), 200

@app.route(api_path + '/posts', methods = ['GET'])
@auth.optional_token
@auth.log_request
def get_new_posts(*args, **kwargs):
    found_posts = models.Post.query.order_by(models.Post.timestamp).all()

    return jsonify(
        post_number = len(list(found_posts)),
        posts = [
            p.id for p in found_posts
        ]
    ), 200

@app.route(api_path + '/post/<int:post_id>/like_post', methods = ['POST'])
@auth.requires_token
@auth.log_request
def like_post(post_id, user, *args, **kwargs):

    found_post = models.Post.query.get(post_id)

    if found_post is None:
        return jsonify(
            message="Post not found",
            code=404
        ), 404

    try:
        actions.like_post(models.Post.query.get(post_id), user)
    except post_exc.AlreadyLiked as e:
        return jsonify(
            message=e.message,
            code=400
        ), 400

    return jsonify(
            status=True
        ), 200

@app.route(api_path + '/post/<int:post_id>/unlike_post', methods = ['POST'])
@auth.requires_token
@auth.log_request
def unlike_post(post_id, user, *args, **kwargs):
    found_post = models.Post.query.get(post_id)

    if found_post is None:
        return jsonify(
            message="Post not found",
            code=404
        ), 404

    try:
        actions.unlike_post(models.Post.query.get(post_id), user)
    except post_exc.NotLiked as e:
        return jsonify(
            message=e.message,
            code=400
        ), 400

    return jsonify(
        status=True
    ), 200

@app.route(api_path + '/user/<int:user_id>/activity', methods = ['GET'])
@auth.optional_token
@auth.log_request
def user_activity(user_id, *args, **kwargs):

    desired_user = models.User.query.get(user_id)

    if desired_user is None:
        return jsonify(
            message="User not found",
            code=404
        ), 404

    return jsonify(
        id = desired_user.id,
        username = desired_user.username,
        last_login = desired_user.last_login,
        last_request = desired_user.last_request,
    ), 200

@app.route(api_path + '/user/<int:user_id>', methods = ['GET'])
@auth.optional_token
@auth.log_request
def user_info(user_id, *args, **kwargs):

    desired_user = models.User.query.get(user_id)

    if desired_user is None:
        return jsonify(
            message="User not found",
            code=404
        ), 404

    return jsonify(
        id = desired_user.id,
        username = desired_user.username,
        posts = [
            p.id for p in desired_user.posts
        ]
    ), 200

@app.route(api_path + '/analytics', methods = ['GET'])
@auth.optional_token
@auth.log_request
def analytics(*args, **kwargs):
    date_from_s = request.values.get('date_from', '2000-01-01')
    date_to_s = request.values.get('date_to', datetime.utcnow().strftime("%Y-%m-%d"))

    if date_from_s is None or date_to_s is None:
        return jsonify(
            message="Date_to or date_from is empty ",
            code=400
        ), 400

    try:
        date_from_t = int(round(datetime.strptime(date_from_s, "%Y-%m-%d").timestamp()))
        date_to_t = int(round(datetime.strptime(date_to_s, "%Y-%m-%d").timestamp()))
    except ValueError:
        return jsonify(
            message="Wrong date format, expected: 'year-month-day'",
            code=400
        ), 400
    except OSError:
        return jsonify(
            message="Wrong or non-existent date",
            code=400
        ), 400

    found_likes = models.Like.query.filter(models.Like.timestamp >= date_from_t, models.Like.timestamp <= date_to_t).all()

    return jsonify(
        number_of_likes = len(list(found_likes)),
        liked_posts = [
            l.post_id for l in found_likes
        ]
    ), 200