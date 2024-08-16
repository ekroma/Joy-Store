import sentry_sdk
import uvicorn

from fastapi import FastAPI
from fastapi_versioning import VersionedFastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from fastapi.staticfiles import StaticFiles
from config.settings import settings
from config.lifecycle import on_shutdown, on_startup

from apps.base.router_v1.router import router as router_base

from apps.market.router_v1.global_router import router as router_global_market
from apps.market.router_v1.admin_router import router as router_admin_market
from apps.market.router_v1.client_router import router as router_client_market

from apps.GJ_control_system.statistics_system.router_v1.router import router as router_global_statistics

from apps.user_management.router_v1.admin_router import router as router_admin_auth
from apps.user_management.router_v1.auth_router import router as router_client_auth
from apps.user_management.router_v1.global_router import router as router_global_auth

from apps.e_commerce.product.router_v1.admin_router import router as router_product_admin
from apps.e_commerce.product.router_v1.client_router import router as router_product_client

from apps.e_commerce.category.router_v1.admin_router import router as router_category_admin
from apps.e_commerce.category.router_v1.client_router import router as router_category_client

from apps.e_commerce.subcategory.router_v1.admin_router import router as router_subcategory_admin
from apps.e_commerce.subcategory.router_v1.client_router import router as router_subcategory_client

from apps.e_commerce.brand.router_v1.admin_router import router as router_admin_brand
from apps.e_commerce.brand.router_v1.client_router import router as router_client_brand

from apps.e_commerce.order.router_v1.admin_router import router as router_order_admin
from apps.e_commerce.order.router_v1.client_router import router as router_order_client

from apps.e_commerce.promocode.router_v1.admin_router import router as router_promocode_admin

from apps.newsletters.notifications.router_v1.admin_router import router as routes_notifications_admin
from apps.newsletters.notifications.router_v1.client_router import router as routes_notifications_client
from apps.newsletters.notifications.router_v1.global_router import router as routes_notifications_global

app = FastAPI(
    title="Online store API",
    summary="Пример приложения, показывающего, как использовать FastAPI для добавления ReST API в коллекцию MongoDB.",
)

app.include_router(router_base)
app.include_router(router_global_statistics)

app.include_router(router_global_market)
app.include_router(router_admin_market)
app.include_router(router_client_market)

app.include_router(router_client_auth)
app.include_router(router_admin_auth)
app.include_router(router_global_auth)

app.include_router(router_category_admin)
app.include_router(router_category_client)

app.include_router(router_subcategory_admin)
app.include_router(router_subcategory_client)

app.include_router(router_admin_brand)
app.include_router(router_client_brand)

app.include_router(router_product_admin)
app.include_router(router_product_client)

app.include_router(router_order_admin)
app.include_router(router_order_client)

app.include_router(router_promocode_admin)

app.include_router(routes_notifications_global)
app.include_router(routes_notifications_admin)
app.include_router(routes_notifications_client)

origins = [
    "http://localhost:3000",
    "http://192.168.1.12:8000",
    "34.226.140.11"
]
allowed_hosts=[
    "34.226.140.11",
    "localhost",
    "ec2-34-226-140-11.compute-1.amazonaws.com",
    "0.0.0.0",
    "192.168.1.12",
    ]

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

sentry_sdk.init(
    dsn="https://0d46ebf650b7775be8634eb6b06f1989@o4506364877144064.ingest.sentry.io/4506364884025344",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


versioned_app = VersionedFastAPI(
    app,
    enable_latest=True,
    prefix_format="/online_store/v{major}",
    version_format="{major}",
)

versioned_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", 'Set-Cookie', "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
    max_age=3600,
)
versioned_app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)
versioned_app.add_event_handler("startup", on_startup)
versioned_app.add_event_handler("shutdown", on_shutdown)

versioned_app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")


if __name__ == "__main__":
    uvicorn.run("main:versioned_app", host="0.0.0.0", port=8000, reload=True, proxy_headers=True)