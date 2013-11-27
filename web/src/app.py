import os
import configparser
import locale
import functools
import threading
import json
import queue
import datetime

locale.setlocale(locale.LC_ALL, "fr_CA.UTF-8")

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError, InvalidRequestError

import tornado.escape
import tornado.web
import tornado.websocket
import tornado.template
from tornado.web import HTTPError

import models

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/(?P<user>[a-zA-Z0-9]{32})", HomeHandler),
            (r"/(?P<user>[a-zA-Z0-9]{32})/update", UpdateHandler),
            (r"/(?P<user>[a-zA-Z0-9]{32})/updates", UpdatesHandler),
            (r"/(?P<user>[a-zA-Z0-9]{32})/chat", ChatHandler),
        ]
        cp = configparser.ConfigParser()
        cp.read('site.cfg');
        (db_name, db_user, db_pass) = map(lambda x: cp.get('db', x), ('db', 'user', 'pass'))

        settings = {
            'cookie_secret':cp.get('app', 'cookie_secret'),
            'template_path':os.path.join(os.path.dirname(__file__), "templates"),
            'debug':cp.get('app', 'debug').strip().lower() == "true",
            'xsrf_cookies':True,
        }
        tornado.web.Application.__init__(self, handlers, **settings)
        self.listeners = []
        self.jobs = queue.Queue()
        # Have one global connection.
        self.db = scoped_session(sessionmaker(bind=models.engine))
        for i in range(4):
            t = Publisher(self.jobs)
        t.start()


class DBHandler:
    @property
    def db(self):
        return self.application.db

class BaseWebHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        token = (self.get_argument("_xsrf", None) or
                 self.request.headers.get("X-Xsrftoken") or
                 self.request.headers.get("X-Csrftoken"))
        byteToken = bytes(self.xsrf_token, encoding="utf-8")
        if not token:
            raise HTTPError(403, "'_xsrf' argument missing from POST")
        if byteToken != token:
            raise HTTPError(403, "XSRF cookie does not match POST argument")


class AuthHandler(DBHandler):
    def decode_argument(self, value, name=None):
        if name=='user':
            try:
                user = self.db.query(models.User).filter_by(hash=value).first()
            # Rather a hack, but this is the first database request on any query,
            # so renew the connection if it has died.
            except (OperationalError, InvalidRequestError) as e:
                self.application.db = scoped_session(sessionmaker(bind=models.engine))
                user = self.db.query(models.User).filter_by(hash=value).first()
            if not user:
                raise HTTPError(403, 
                    "Veuillez utiliser le lien avec votre jeton d'authentification.")
            else:
                return user
        else:
            return value



def model2dict(row):
    return dict((col, getattr(row, col)) for col in row.__table__.columns.keys())

def user2dict(user):
    return {
        'name': user.name,
        'presence' : (
            ('V', user.V),
            ('S', user.S),
            ('D', user.D),
            ('L', user.L),
        ),
        'answer': not (user.S is None and user.V is None and user.D is None and user.L is None)
    }

class HomeHandler(AuthHandler, BaseWebHandler):
    def get(self, user):
        users = self.db.query(models.User).all()
        #user_dict = list(map(user2dict, filter(lambda u: u.name != user.name, users)))
        user_dict = list(map(user2dict, users))
        # order by answered, then name
        user_dict.sort(key=(lambda u: (not u['answer'], locale.strxfrm(u['name']))))
        self.render("template.html", user=user, users=user_dict)

class UpdateHandler(AuthHandler, BaseWebHandler):
    @tornado.web.asynchronous
    def post(self, user):
        presence = self.request.arguments.get("presence[]", None)
        if presence:
            try:
                if not (len(presence)==4 and \
                        functools.reduce(lambda x,y: x and (int(y) in (0,1,2)), [True] + presence)):
                    raise HTTPError(400, "Invalid presence argument.")
            except Exception as e:
                raise HTTPError(400, "Invalid presence format.")
            (user.V, user.S, user.D, user.L) = map(int,presence)
        self.db.add(user)
        self.db.commit()
        message = json.dumps({"UpdateUser": user2dict(user)})
        self.write("ok");
        self.finish()
        for listener in application.listeners:
            application.jobs.put((listener, message))

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
        except Exception as e:
            message = False
        self.write("ok")
        self.finish()
        if message:
            for listener in application.listeners:
                application.jobs.put((listener, message))


class UpdatesHandler(AuthHandler, tornado.websocket.WebSocketHandler):
    def open(self, user):
        try:
            user = self.decode_argument(user, 'user')
            application.listeners.append(self)
        except:
            self.close()

    def on_close(self):
        application.listeners.remove(self)

class Publisher(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            try:
                listener, message = self.queue.get(True, 1)
            except queue.Empty:
                continue
            try:
                listener.write_message(message)
            except:
                pass
            self.queue.task_done()

application = Application()

if __name__ == "__main__":
    application.listen(8119)
    tornado.ioloop.IOLoop.instance().start()
