from app import db
import app.models as models
from app.exceptions import post_exceptions as exc

def like_post(post: models.Post, user: models.User):
    if post.likes.filter_by(user_id = user.id).first() is None:
        new_like = models.Like(
            user_id = user.id,
            post_id = post.id,
        )

        db.session.add(new_like)
        db.session.commit()
    else:
        raise exc.AlreadyLiked(post, user)

def unlike_post(post: models.Post, user: models.User):

    found_like = post.likes.filter_by(user_id = user.id).first()

    if found_like is not None:
        db.session.delete(found_like)
        db.session.commit()
    else:
        raise exc.NotLiked(post, user)