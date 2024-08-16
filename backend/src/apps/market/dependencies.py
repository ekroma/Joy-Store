from fastapi import Request
from .market_service import MarketService
from .exeptions import MarketNotFoundException
from .model import Market
from config.settings import settings

async def get_market(request:Request)-> Market|None:
    referer = request.headers.get("Referer")
    print("Referer:",referer)
    if not referer or not request.client:
        raise MarketNotFoundException
    domain = referer.split("//")[-1].split("/")[0]
    print("Domain:",domain)
    if not domain:
        raise MarketNotFoundException
    elif domain == settings.BASE_DOMAIN:
        return None
    market = await MarketService.get_by_domain_or_ip(domain)
    print("Market:",market)
    if not market:
        raise MarketNotFoundException
    return market