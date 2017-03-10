import requests_cache

def install_cache():
    requests_cache.install_cache('pbr_mlb')

SEASONS_TO_SCRAPE = reversed(range(2011, 2017))
