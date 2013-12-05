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
import models

class HomeHandler(AuthHandler, BaseWebHandler):
    def get(self, user):
        users = self.db.query(models.User).all()
        user_dict = list(map(models.to_dict, users))
        # order by answered, then name
        user_dict.sort(key=(lambda u: (not u['answer'], locale.strxfrm(u['name']))))
        self.render("template.html", user=user, users=user_dict, settings=application.settings['eventer'])

class UpdateHandler(AuthHandler, BaseWebHandler):
    @tornado.web.asynchronous
    def post(self, user):
        callback = self.get_argument("callback", None)
        if (not callback):
            raise HTTPError(400, "No callback")
        try:
            callback = getattr(self, ("callback_" + callback.decode('utf-8')))
            message = callback(user)

        except Exception as e:
            raise HTTPError(400, "Invalid callback")
        self.write("ok");
        self.finish()
        if message:
            for listener in application.listeners:
                application.jobs.put((listener, message))

    def callback_presence(self, user):
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
            print(e)
            message = False
            self.write("error")
        finally:
            self.finish()
        if message:
            for listener in application.listeners:
                application.jobs.put((listener, message))

