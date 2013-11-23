import os
import configparser
from sqlalchemy.orm import scoped_session, sessionmaker

import tornado.web
import tornado.template

import models

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/(?P<user>[a-zA-Z0-9]{32})", HomeHandler),
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
        # Have one global connection.
        self.db = scoped_session(sessionmaker(bind=models.engine))

class DBHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class AuthHandler(DBHandler):
    def decode_argument(self, value, name=None):
        if name=='user':
            user = self.db.query(models.User).filter_by(hash=value).first()
            if not user:
                raise tornado.web.HTTPError(403, 
                    "Veuillez utiliser le lien avec votre jeton d'authentification.")
            else:
                return user
        else:
            return value

class HomeHandler(AuthHandler):
    def get(self, user):
        self.render("template.html", user=user)


class ViewHandler(DBHandler):
    def get(self, hash):
        pass

application = Application()

if __name__ == "__main__":
    application.listen(8119)
    tornado.ioloop.IOLoop.instance().start()
