import configparser
from sqlalchemy.orm import scoped_session, sessionmaker

import tornado.web

from models import *  # import the engine to bind

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/([a-zA-Z0-9]{32})", HomeHandler),
        ]
        cp = configparser.ConfigParser()
        cp.read('site.cfg');
        (db_name, db_user, db_pass) = map(lambda x: cp.get('db', x), ('db', 'user', 'pass'))

        settings = dict(
            cookie_secret=cp.get('app', 'cookie_secret'),
            debug=cp.get('app', 'debug').strip().lower() == "true"
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        # Have one global connection.
        self.db = scoped_session(sessionmaker(bind=engine))

class DBHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class HomeHandler(DBHandler):
    def get(self, hash):
        user = self.db.query(User).filter_by(hash=hash).one()
        self.write(user.name)
    

class ViewHandler(DBHandler):
    def get(self, hash):
        pass

application = Application()

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
