# Agents module - Consolidated scrapers

# Central Government Portals
from .scrapers import scrape_etenders, scrape_gem, scrape_ireps, scrape_defproc

# State Government Portals
from .scrapers import scrape_mahatenders, scrape_rajasthan, scrape_up, scrape_tntenders
from .scrapers import scrape_kerala, scrape_wb, scrape_jharkhand, scrape_assam

# Private Aggregators
from .scrapers import scrape_tendertiger, scrape_bidassist, scrape_tendersinfo