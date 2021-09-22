from core.models import WeedmapsShop, GmapsBusiness

ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_EMPLOYEE = "employee"
ROLES_PRIORITY = [ROLE_ADMIN, ROLE_MANAGER, ROLE_EMPLOYEE]

LISTING_CLASSES = [WeedmapsShop, GmapsBusiness]
