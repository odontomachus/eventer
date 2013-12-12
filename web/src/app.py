import os
import configparser
import locale
import threading
import json
import queue

locale.setlocale(locale.LC_ALL, "fr_CA.UTF-8")

from sqlalchemy.orm import scoped_session, sessionmaker

import tornado.web
import tornado.websocket
import tornado.template

import models
import controllers
from controllers import (
    ChatHandler,
    UserHandler,
    MessageHandler,
    UpdatesHandler,
    HomeHandler,
)

class Application(tornado.web.Application):
    def __init__(self):
        controllers.application = self

        cp = configparser.ConfigParser()
        cp.read('site.cfg');
        (db_name, db_user, db_pass) = map(lambda x: cp.get('db', x), ('db', 'user', 'pass'))

        settings = {
            'cookie_secret':cp.get('app', 'cookie_secret'),
            'template_path':os.path.join(os.path.dirname(__file__), "templates"),
            'debug':cp.get('app', 'debug').strip().lower() == "true",
            'xsrf_cookies':True,
            'eventer': {
                'padId': cp.get('etherpad', 'padId'),
            }
        }

        handlers = [
            (r"/(?P<user>[a-zA-Z0-9]{32})", HomeHandler),
            (r"/(?P<user>[a-zA-Z0-9]{32})/user/(?P<action>presence)", UserHandler),
            (r"/(?P<user>[a-zA-Z0-9]{32})/message/(?P<action>new|reply)", MessageHandler),
            (r"/(?P<user>[a-zA-Z0-9]{32})/message/(?P<action>view)/(?P<thread_id>\d+)", MessageHandler),
            (r"/(?P<user>[a-zA-Z0-9]{32})/updates", UpdatesHandler),
            (r"/(?P<user>[a-zA-Z0-9]{32})/chat", ChatHandler),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)
        self.listeners = []
        self.jobs = queue.Queue()
        # Have one global connection.
        self.db = scoped_session(sessionmaker(bind=models.engine))
        self.publishers = []
        for i in range(4):
            t = Publisher(self.jobs)
            self.publishers.append(t)
            t.start()



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
