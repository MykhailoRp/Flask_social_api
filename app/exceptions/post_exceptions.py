class AlreadyLiked(Exception):
    def __init__(self, post, user, message="{} is already liked by {}"):
        self.user = user
        self.post = post
        self.message = message.format(post.__repr__(), user.__repr__())
        super().__init__(self.message)

class NotLiked(Exception):
    def __init__(self, post, user, message="{} is not liked by {}"):
        self.user = user
        self.post = post
        self.message = message.format(post.__repr__(), user.__repr__())
        super().__init__(self.message)