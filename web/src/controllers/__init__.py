import json
import locale
import functools
import datetime

import tornado.escape
import tornado.web
from tornado.web import HTTPError

from .base import (
    AuthHandler, 
    BaseWebHandler,
)
from models import (
    User,
    Comment,
    to_dict
)

class HomeHandler(AuthHandler, BaseWebHandler):
    """ Handler for home page. """
    def get(self, user):
        """ Write home page. """
        # Get content
        # Get user
        users = self.db.query(User).all()
        user_dict = list(map(to_dict, users))

        # Get messages
        messages = self.db.query(Comment)\
                          .filter_by(original=None)\
                          .order_by(Comment.last_response.desc())\
                          .limit(11).all()
        # For pagination
        more_messages = (len(messages) == 11)
        # We only need 10
        if more_messages:
            messages.pop()
        messages = list(map(to_dict,messages))
        # order by answered, then name
        user_dict.sort(key=(lambda u: (not u['answer'], locale.strxfrm(u['name']))))
        self.render("template.html", user=user, users=user_dict, 
                    messages=messages,
                    more_messages=more_messages,
                    settings=application.settings['eventer'])

class ActionHandler(AuthHandler, BaseWebHandler):
    @tornado.web.asynchronous
    def post(self, user, action, *args, **kwargs):
        self.call(user, "post", action, *args, **kwargs)

    @tornado.web.asynchronous
    def get(self, user, action, *args, **kwargs):
        self.call(user, "get", action, *args, **kwargs)

    def call(self, user, method, action, *args, **kwargs):
        try:
            callback = getattr(self, ("_".join(["",method,action.decode("utf-8")])))
            message = callback(user, *args, **kwargs)

        except Exception as e:
            print(e)
            raise HTTPError(404)
        self.finish()
        if message:
            for listener in application.listeners:
                application.jobs.put((listener, message))


class UserHandler(ActionHandler):
    def _post_presence(self, user, *args):
        presence = self.request.arguments.get("presence[]", None)
        if presence:
            try:
                if not (len(presence)==4 and \
                        functools.reduce(lambda x,y: x and (int(y) in (-1,0,1,2)), [True] + presence)):
                    raise HTTPError(400, "Invalid presence argument.")
            except Exception as e:
                raise HTTPError(400, "Invalid presence format.")
            (user.V, user.S, user.D, user.L) = map(lambda x: x if x>=0 else None, map(int, presence))
        self.db.add(user)
        self.db.commit()
        return json.dumps({"UpdateUser": user.to_dict()})


class MessageHandler(ActionHandler):
    def _post_new(self, user, *args):
        """ Record a new comment. """
        try:
            comment = self.get_argument("comment")
            title = self.get_argument("title")
            now = datetime.datetime.now()
            comment = Comment(user=user, title=title, comment=comment,
                              created=now, updated=now, last_response=now)
            self.db.add(comment)
            self.db.commit()
        except Exception as e:
            print(e)
            pass

    def _post_reply(self, user, *args):
        """ Record a reply. """
        try:
            original_id = self.get_argument("thread_id")
            comment = self.get_argument("reply")
            now = datetime.datetime.now()
            original = self.db.query(Comment).filter_by(id=original_id).first()
            comment = Comment(user=user, comment=comment,
                              created=now, updated=now, last_response=now, original=original_id)
            original.replies.append(comment)
            original.last_response = now
            self.db.add(original)
            self.db.commit()

        except Exception as e:
            print(e)
            pass

    def _get_view(self, user, thread_id, *args):
        """ Send a json reply with the whole message thread. """
        thread = self.db.query(Comment).filter_by(id=thread_id).first()
        thread_dict = thread.to_dict(True)
        self.write(thread_dict)

class UpdatesHandler(AuthHandler, tornado.websocket.WebSocketHandler):
    def open(self, user):
        try:
            user = self.decode_argument(user, 'user')
            application.listeners.append(self)
        except:
            self.close()

    def on_close(self):
        application.listeners.remove(self)

class ChatHandler(AuthHandler, BaseWebHandler):
    @tornado.web.asynchronous
    def post(self, user):
        try:
            message = self.get_argument("message", None)
            message = json.dumps({
                'ChatMessage': {
                    'text': tornado.escape.linkify(tornado.escape.xhtml_escape(message)),
                    'nickname': user.name,
                    'date': datetime.datetime.now().strftime('%c'),
                    'userId': user.id,
                },
            });
            self.write("ok")
        except Exception as e:
            message = False
            self.write("error")
        finally:
            self.finish()
        if message:
            for listener in application.listeners:
                application.jobs.put((listener, message))

