from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError, InvalidRequestError
import tornado
from tornado.web import HTTPError
import models

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
