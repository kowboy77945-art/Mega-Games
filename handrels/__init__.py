# handlers/__init__.py

from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.shop import router as shop_router
from handlers.games import router as games_router
from handlers.promo import router as promo_router
from handlers.referral import router as referral_router
from handlers.daily import router as daily_router
from handlers.settings import router as settings_router
from handlers.admin import router as admin_router
from handlers.support import router as support_router

all_routers = [
    start_router,
    profile_router,
    shop_router,
    games_router,
    promo_router,
    referral_router,
    daily_router,
    settings_router,
    admin_router,
    support_router
]
