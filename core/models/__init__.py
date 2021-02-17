from sqlalchemy.orm import scoped_session, sessionmaker

from .business import Business
from .r2g_business import R2GBusiness
from .car_product import CarProduct
from .gmaps_business import GmapsBusiness
from .third_party import ThirdParty
from .user import User
from .weed_mapping import WeedMapping
from .weedmaps_product import WeedmapsProduct
from .weedmaps_shop import WeedmapsShop


class DbAbsLayer(object):
    def createSession(self):
        Session = sessionmaker()
        self.session = Session.configure(bind=self.engine)


def import_db_models():
    pass
