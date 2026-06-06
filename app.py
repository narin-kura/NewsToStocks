# Copyright (c) 2025-2026 Kura Nagender Narin (github.com/narin-kura). All rights reserved.
# Non-commercial use only. Commercial use requires written permission: k.n.narin@gmail.com
# NOT financial advice. See LICENSE for full terms and important disclaimers.
import os
import re
import time
import threading
import requests
import concurrent.futures
from bs4 import BeautifulSoup
import yfinance as yf
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

sia = SentimentIntensityAnalyzer()

company_to_symbol = {
    # Big Tech
    'Apple': 'AAPL', 'Microsoft': 'MSFT', 'Tesla': 'TSLA', 'Amazon': 'AMZN',
    'Google': 'GOOGL', 'Alphabet': 'GOOGL', 'Meta': 'META', 'Facebook': 'META',
    'Netflix': 'NFLX', 'Nvidia': 'NVDA', 'AMD': 'AMD', 'IBM': 'IBM',
    'Intel': 'INTC', 'Cisco': 'CSCO', 'Oracle': 'ORCL', 'PayPal': 'PYPL',
    'Adobe': 'ADBE', 'Salesforce': 'CRM', 'Qualcomm': 'QCOM',
    'Texas Instruments': 'TXN', 'Broadcom': 'AVGO', 'Applied Materials': 'AMAT',
    'Micron': 'MU', 'Shopify': 'SHOP', 'Palantir': 'PLTR', 'Snowflake': 'SNOW',
    'Cloudflare': 'NET', 'CrowdStrike': 'CRWD', 'Palo Alto': 'PANW',
    'Fortinet': 'FTNT', 'Datadog': 'DDOG', 'MongoDB': 'MDB',
    'ServiceNow': 'NOW', 'Workday': 'WDAY', 'Zoom': 'ZM',
    # Finance
    'JPMorgan': 'JPM', 'JPMorgan Chase': 'JPM', 'Goldman Sachs': 'GS',
    'Morgan Stanley': 'MS', 'Bank of America': 'BAC', 'Wells Fargo': 'WFC',
    'Citigroup': 'C', 'Citi': 'C', 'BlackRock': 'BLK',
    'Visa': 'V', 'Mastercard': 'MA', 'American Express': 'AXP', 'Amex': 'AXP',
    'Berkshire Hathaway': 'BRK.B', 'Berkshire': 'BRK.B',
    'Charles Schwab': 'SCHW', 'Coinbase': 'COIN', 'Block': 'SQ',
    'Robinhood': 'HOOD',
    # Consumer / Retail
    'Walmart': 'WMT', 'Target': 'TGT', 'Costco': 'COST', 'Home Depot': 'HD',
    'Procter & Gamble': 'PG', 'Coca-Cola': 'KO', 'Pepsi': 'PEP', 'PepsiCo': 'PEP',
    "McDonald's": 'MCD', 'Starbucks': 'SBUX', 'Nike': 'NKE',
    'Disney': 'DIS', 'Comcast': 'CMCSA', 'Airbnb': 'ABNB',
    'Uber': 'UBER', 'Lyft': 'LYFT', 'DoorDash': 'DASH',
    'eBay': 'EBAY', 'Etsy': 'ETSY', 'Wayfair': 'W', 'Chewy': 'CHWY',
    'Instacart': 'CART', 'Carvana': 'CVNA',
    # Healthcare / Pharma
    'Johnson & Johnson': 'JNJ', 'Pfizer': 'PFE', 'Moderna': 'MRNA',
    'AstraZeneca': 'AZN', 'Merck': 'MRK', 'Abbott': 'ABT',
    'UnitedHealth': 'UNH', 'Eli Lilly': 'LLY', 'Amgen': 'AMGN',
    'Gilead': 'GILD', 'Biogen': 'BIIB', 'CVS': 'CVS',
    # Biotech
    'Regeneron': 'REGN', 'Vertex': 'VRTX', 'BioNTech': 'BNTX',
    'Illumina': 'ILMN', 'CRISPR Therapeutics': 'CRSP', 'Editas': 'EDIT',
    'Beam Therapeutics': 'BEAM', 'Intellia': 'NTLA',
    'Alnylam': 'ALNY', 'Arrowhead': 'ARWR', 'Exact Sciences': 'EXAS',
    'Pacific Biosciences': 'PACB', 'Repligen': 'RGEN',
    '10x Genomics': 'TXG', 'Recursion': 'RXRX',
    # Energy
    'ExxonMobil': 'XOM', 'Exxon': 'XOM', 'Chevron': 'CVX',
    'ConocoPhillips': 'COP', 'Shell': 'SHEL', 'BP': 'BP',
    # Clean Energy / Renewable
    'NextEra': 'NEE', 'NextEra Energy': 'NEE', 'Enphase': 'ENPH',
    'SolarEdge': 'SEDG', 'First Solar': 'FSLR', 'Sunrun': 'RUN',
    'Bloom Energy': 'BE', 'Plug Power': 'PLUG', 'Array Technologies': 'ARRY',
    'Ormat': 'ORA',
    # Automotive
    'Ford': 'F', 'General Motors': 'GM', 'Rivian': 'RIVN', 'Lucid': 'LCID',
    # Space
    'Virgin Galactic': 'SPCE', 'Rocket Lab': 'RKLB', 'Planet Labs': 'PL',
    'Intuitive Machines': 'LUNR', 'Redwire': 'RDW',
    'AST SpaceMobile': 'ASTS', 'AST': 'ASTS',
    'Northrop Grumman': 'NOC', 'L3Harris': 'LHX',
    # Defense
    'General Dynamics': 'GD', 'Leidos': 'LDOS',
    'Booz Allen': 'BAH', 'Huntington Ingalls': 'HII', 'SAIC': 'SAIC',
    # Hardware / Infrastructure
    'Dell': 'DELL', 'HP': 'HPQ', 'Hewlett Packard': 'HPE', 'HPE': 'HPE',
    'Western Digital': 'WDC', 'Seagate': 'STX', 'NetApp': 'NTAP',
    'Pure Storage': 'PSTG', 'Super Micro': 'SMCI', 'Supermicro': 'SMCI',
    'Logitech': 'LOGI', 'Zebra Technologies': 'ZBRA', 'Keysight': 'KEYS',
    # AI / ML
    'C3.ai': 'AI', 'UiPath': 'PATH', 'SoundHound': 'SOUN',
    'BigBear': 'BBAI', 'Symbotic': 'SYM', 'Veritone': 'VERI',
    # Telecom
    'AT&T': 'T', 'Verizon': 'VZ', 'T-Mobile': 'TMUS',
    'Charter': 'CHTR', 'Twilio': 'TWLO',
    # Gaming
    'Electronic Arts': 'EA', 'EA': 'EA', 'Take-Two': 'TTWO',
    'Unity': 'U', 'Roblox': 'RBLX', 'Sea Limited': 'SE',
    # Travel / Hospitality
    'Booking Holdings': 'BKNG', 'Booking.com': 'BKNG', 'Expedia': 'EXPE',
    'Marriott': 'MAR', 'Hilton': 'HLT', 'Hyatt': 'H',
    'Delta': 'DAL', 'Delta Air Lines': 'DAL', 'United Airlines': 'UAL',
    'American Airlines': 'AAL', 'Southwest': 'LUV',
    'Carnival': 'CCL', 'Royal Caribbean': 'RCL',
    # Industrial / Other
    'Boeing': 'BA', 'Lockheed Martin': 'LMT', 'Raytheon': 'RTX',
    'Caterpillar': 'CAT', 'General Electric': 'GE', '3M': 'MMM',
    'FedEx': 'FDX', 'UPS': 'UPS',
    # Real Estate
    'American Tower': 'AMT', 'Prologis': 'PLD', 'Equinix': 'EQIX',
    'Crown Castle': 'CCI', 'Public Storage': 'PSA',
    'Simon Property': 'SPG', 'Realty Income': 'O', 'CBRE': 'CBRE',
    # Food & Beverage
    'Mondelez': 'MDLZ', 'General Mills': 'GIS', 'Tyson': 'TSN',
    'Chipotle': 'CMG', 'Yum Brands': 'YUM', 'Yum': 'YUM',
}

sector_to_symbols = {
    'tech': {'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'NVDA', 'AMD', 'IBM',
             'INTC', 'CSCO', 'ORCL', 'ADBE', 'CRM', 'QCOM', 'AVGO', 'AMAT', 'MU',
             'SHOP', 'PLTR', 'SNOW', 'NET', 'CRWD', 'PANW', 'FTNT', 'DDOG', 'MDB',
             'NOW', 'WDAY', 'ZM'},
    'technology': {'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'NVDA', 'AMD',
                   'IBM', 'INTC', 'CSCO', 'ORCL', 'ADBE', 'CRM', 'QCOM', 'AVGO'},
    'finance': {'JPM', 'GS', 'MS', 'BAC', 'WFC', 'C', 'BLK', 'V', 'MA', 'AXP',
                'BRK.B', 'SCHW', 'COIN', 'SQ', 'HOOD', 'PYPL'},
    'financial': {'JPM', 'GS', 'MS', 'BAC', 'WFC', 'C', 'BLK', 'V', 'MA', 'AXP',
                  'BRK.B', 'SCHW', 'PYPL'},
    'consumer': {'WMT', 'TGT', 'COST', 'HD', 'PG', 'KO', 'PEP', 'MCD', 'SBUX', 'NKE',
                 'DIS', 'CMCSA', 'ABNB', 'UBER', 'LYFT', 'DASH',
                 'EBAY', 'ETSY', 'W', 'CHWY', 'CART', 'CVNA'},
    'retail': {'WMT', 'TGT', 'COST', 'HD', 'EBAY', 'ETSY', 'W', 'CHWY',
               'CART', 'CVNA', 'SHOP', 'AMZN'},
    'ecommerce': {'AMZN', 'SHOP', 'EBAY', 'ETSY', 'W', 'CHWY', 'CART', 'CVNA'},
    'energy': {'XOM', 'CVX', 'COP', 'SHEL', 'BP'},
    'clean energy': {'NEE', 'ENPH', 'SEDG', 'FSLR', 'RUN', 'BE', 'PLUG', 'ARRY', 'ORA'},
    'renewable': {'NEE', 'ENPH', 'SEDG', 'FSLR', 'RUN', 'BE', 'PLUG', 'ARRY', 'ORA'},
    'solar': {'ENPH', 'SEDG', 'FSLR', 'RUN', 'ARRY'},
    'healthcare': {'JNJ', 'PFE', 'MRNA', 'AZN', 'MRK', 'ABT', 'UNH', 'LLY', 'AMGN',
                   'GILD', 'BIIB', 'CVS'},
    'pharma': {'PFE', 'MRNA', 'AZN', 'MRK', 'LLY', 'AMGN', 'GILD', 'BIIB'},
    'biotech': {'REGN', 'VRTX', 'BNTX', 'ILMN', 'CRSP', 'EDIT', 'BEAM', 'NTLA',
                'ALNY', 'ARWR', 'EXAS', 'PACB', 'RGEN', 'TXG', 'RXRX',
                'MRNA', 'BIIB', 'AMGN'},
    'biotechnology': {'REGN', 'VRTX', 'BNTX', 'ILMN', 'CRSP', 'EDIT', 'BEAM', 'NTLA',
                      'ALNY', 'ARWR', 'EXAS', 'PACB', 'RGEN', 'TXG', 'RXRX'},
    'genomics': {'ILMN', 'CRSP', 'EDIT', 'BEAM', 'NTLA', 'PACB', 'TXG'},
    'semiconductor': {'NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'AMAT', 'MU', 'TXN'},
    'automotive': {'TSLA', 'F', 'GM', 'RIVN', 'LCID'},
    'ev': {'TSLA', 'RIVN', 'LCID'},
    'media': {'DIS', 'NFLX', 'META', 'CMCSA'},
    'gaming': {'EA', 'TTWO', 'U', 'RBLX', 'SE'},
    'industrial': {'BA', 'LMT', 'RTX', 'CAT', 'GE', 'MMM', 'FDX', 'UPS'},
    'cybersecurity': {'CRWD', 'PANW', 'FTNT', 'NET', 'DDOG'},
    'cloud': {'SNOW', 'NET', 'DDOG', 'MDB', 'NOW', 'WDAY', 'CRM', 'MSFT', 'AMZN', 'GOOGL'},
    'crypto': {'COIN', 'SQ', 'HOOD', 'PYPL'},
    'space': {'SPCE', 'RKLB', 'PL', 'LUNR', 'RDW', 'ASTS', 'NOC', 'LHX', 'LMT', 'BA'},
    'defense': {'LMT', 'RTX', 'NOC', 'GD', 'LHX', 'LDOS', 'BAH', 'HII', 'SAIC', 'BA'},
    'hardware': {'DELL', 'HPQ', 'HPE', 'WDC', 'STX', 'NTAP', 'PSTG', 'SMCI',
                 'LOGI', 'ZBRA', 'KEYS', 'AAPL', 'INTC', 'AMD', 'NVDA'},
    'storage': {'WDC', 'STX', 'NTAP', 'PSTG', 'SMCI'},
    'ai': {'NVDA', 'MSFT', 'GOOGL', 'META', 'AMZN', 'PLTR', 'AI', 'PATH',
           'SOUN', 'BBAI', 'SYM', 'VERI', 'RXRX', 'IBM'},
    'telecom': {'T', 'VZ', 'TMUS', 'CMCSA', 'CHTR', 'TWLO', 'ASTS'},
    'telecommunications': {'T', 'VZ', 'TMUS', 'CMCSA', 'CHTR'},
    'travel': {'ABNB', 'BKNG', 'EXPE', 'MAR', 'HLT', 'H', 'DAL', 'UAL', 'AAL', 'LUV',
               'CCL', 'RCL'},
    'airline': {'DAL', 'UAL', 'AAL', 'LUV'},
    'hospitality': {'MAR', 'HLT', 'H', 'ABNB', 'CCL', 'RCL'},
    'reit': {'AMT', 'PLD', 'EQIX', 'CCI', 'PSA', 'SPG', 'O', 'CBRE'},
    'real estate': {'AMT', 'PLD', 'EQIX', 'CCI', 'PSA', 'SPG', 'O', 'CBRE'},
    'food': {'KO', 'PEP', 'MCD', 'SBUX', 'MDLZ', 'GIS', 'TSN', 'CMG', 'YUM'},
    'restaurant': {'MCD', 'SBUX', 'CMG', 'YUM'},
}

news_sources = [
    # Reuters
    'https://feeds.reuters.com/reuters/businessNews',
    'https://feeds.reuters.com/reuters/technologyNews',
    # Yahoo Finance
    'https://finance.yahoo.com/rss/topstories',
    'https://finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US',
    # CNN Money
    'http://rss.cnn.com/rss/money_news_international.rss',
    'http://rss.cnn.com/rss/money_technology.rss',
    # MarketWatch
    'https://feeds.marketwatch.com/marketwatch/topstories/',
    'https://feeds.marketwatch.com/marketwatch/marketpulse/',
    # Wall Street Journal
    'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
    'https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml',
    # CNBC
    'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'https://www.cnbc.com/id/15839135/device/rss/rss.html',
    'https://www.cnbc.com/id/20910258/device/rss/rss.html',
    # TechCrunch (good for tech/AI stocks)
    'https://techcrunch.com/feed/',
    # Fortune
    'https://fortune.com/feed/',
    # Business Insider
    'https://markets.businessinsider.com/rss/news',
    # Investing.com
    'https://www.investing.com/rss/news.rss',
    'https://www.investing.com/rss/stock_stock_picks.rss',
    # Nasdaq
    'https://www.nasdaq.com/feed/rssoutbound?category=Markets',
    # Reddit community sentiment
    'https://www.reddit.com/r/stocks/hot/.rss',
    'https://www.reddit.com/r/investing/hot/.rss',
    'https://www.reddit.com/r/wallstreetbets/hot/.rss',
]
custom_sources = []

# Build a set of all known ticker symbols for fast $TICKER matching
_all_symbols = set(company_to_symbol.values())

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; NewsToStocks/1.0)'}

# ── S&P 500 auto-loader ───────────────────────────────────────────────────────
_SP500_SECTOR_MAP = {
    'Information Technology': ['tech'],
    'Financials':             ['finance'],
    'Health Care':            ['healthcare'],
    'Consumer Discretionary': ['consumer', 'retail'],
    'Consumer Staples':       ['consumer', 'food'],
    'Industrials':            ['industrial'],
    'Communication Services': ['media', 'telecom'],
    'Energy':                 ['energy'],
    'Materials':              ['industrial'],
    'Real Estate':            ['reit'],
    'Utilities':              ['energy'],
}
_SP500_SUBSECTOR_MAP = {
    'Semiconductors':                          ['semiconductor'],
    'Semiconductor Materials & Equipment':     ['semiconductor'],
    'Application Software':                    ['tech', 'cloud'],
    'Systems Software':                        ['tech'],
    'Data Processing & Outsourced Services':   ['tech', 'cloud'],
    'Internet Services & Infrastructure':      ['cloud'],
    'IT Consulting & Other Services':          ['tech'],
    'Electronic Equipment & Instruments':      ['hardware'],
    'Technology Hardware, Storage & Peripherals': ['hardware'],
    'Biotechnology':                           ['biotech'],
    'Pharmaceuticals':                         ['pharma'],
    'Life Sciences Tools & Services':          ['biotech'],
    'Health Care Equipment & Supplies':        ['healthcare'],
    'Health Care Facilities':                  ['healthcare'],
    'Managed Health Care':                     ['healthcare'],
    'Aerospace & Defense':                     ['defense', 'space'],
    'Ground Transportation':                   ['automotive'],
    'Automobile Manufacturers':                ['automotive', 'ev'],
    'Auto Parts & Equipment':                  ['automotive'],
    'Movies & Entertainment':                  ['media', 'gaming'],
    'Interactive Media & Services':            ['media'],
    'Interactive Home Entertainment':          ['gaming'],
    'Wireless Telecommunication Services':     ['telecom'],
    'Diversified Telecommunication Services':  ['telecom'],
    'Cable & Satellite':                       ['media', 'telecom'],
    'Internet Retail':                         ['retail', 'ecommerce'],
    'Broadline Retail':                        ['retail'],
    'Specialty Retail':                        ['retail'],
    'Hotels, Restaurants & Leisure':           ['travel', 'food', 'hospitality'],
    'Restaurants':                             ['food', 'restaurant'],
    'Airlines':                                ['airline', 'travel'],
    'Cruise Lines':                            ['travel', 'hospitality'],
    'Lodging':                                 ['hospitality', 'travel'],
    'Electric Utilities':                      ['energy', 'renewable'],
    'Renewable Electricity':                   ['energy', 'renewable'],
    'Oil, Gas & Consumable Fuels':             ['energy'],
    'Banks':                                   ['finance'],
    'Diversified Banks':                       ['finance'],
    'Investment Banking & Brokerage':          ['finance'],
    'Asset Management & Custody Banks':        ['finance'],
    'Consumer Finance':                        ['finance'],
    'Insurance':                               ['finance'],
}


def _load_wiki_index(url, label):
    """Generic loader: fetches a Wikipedia index table and merges tickers/sectors."""
    try:
        resp = requests.get(url, timeout=15, headers=HEADERS)
        soup = BeautifulSoup(resp.content, 'lxml')
        table = soup.find('table', {'id': 'constituents'})
        if not table:
            # fallback: first large wikitable
            tables = soup.find_all('table', {'class': 'wikitable'})
            table = next((t for t in tables if len(t.find_all('tr')) > 50), None)
        if not table:
            print(f'{label}: table not found')
            return
        count = 0
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
            ticker = cols[0].get_text(strip=True)
            name   = cols[1].get_text(strip=True)
            gics   = cols[2].get_text(strip=True) if len(cols) > 2 else ''
            sub    = cols[3].get_text(strip=True) if len(cols) > 3 else ''

            if not ticker or not name:
                continue
            company_to_symbol[name] = ticker
            _all_symbols.add(ticker)

            target_sectors = set()
            for s in _SP500_SECTOR_MAP.get(gics, []):
                target_sectors.add(s)
            for s in _SP500_SUBSECTOR_MAP.get(sub, []):
                target_sectors.add(s)
            for s in target_sectors:
                if s in sector_to_symbols:
                    sector_to_symbols[s].add(ticker)
            count += 1
        print(f'{label}: loaded {count} components')
    except Exception as e:
        print(f'{label} load failed: {e}')


_load_wiki_index(
    'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', 'S&P 500'
)
_load_wiki_index(
    'https://en.wikipedia.org/wiki/Nasdaq-100', 'NASDAQ-100'
)
# ─────────────────────────────────────────────────────────────────────────────

_article_store = {}  # url/preview-key -> processed article (accumulated, never cleared)
_news_cache = {'ts': 0}
_sector_cache = {}   # sector_key -> {'recs': [...], 'ts': float}
CACHE_TTL = 900  # 15 minutes — how often we scrape for new articles


def scrape_source(source):
    items_out = []
    try:
        response = requests.get(source, timeout=10, headers=HEADERS)
        if response.status_code != 200:
            return items_out
        try:
            soup = BeautifulSoup(response.content, 'lxml-xml')
            items = soup.find_all('item')
        except Exception:
            soup = BeautifulSoup(response.content, 'lxml')
            items = soup.find_all('article')
        for item in items:
            title_tag = item.find('title')
            desc_tag = item.find('description') or item.find('summary')
            text = ' '.join(filter(None, [
                title_tag.get_text(strip=True) if title_tag else '',
                BeautifulSoup(desc_tag.decode_contents(), 'lxml').get_text(strip=True) if desc_tag else '',
            ])).strip()
            link_tag = item.find('link')
            url = (link_tag.get_text(strip=True) if link_tag else '') or source
            if text:
                items_out.append({'text': text, 'url': url})
    except Exception as e:
        print(f"Error scraping {source}: {e}")
    return items_out


def scrape_news():
    all_sources = news_sources + custom_sources
    raw_items = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(scrape_source, src): src for src in all_sources}
        for future in concurrent.futures.as_completed(futures):
            raw_items.extend(future.result())
    return [process_news(item['text'], item['url']) for item in raw_items]


def get_cached_news():
    now = time.time()
    if _news_cache['ts'] and (now - _news_cache['ts']) < CACHE_TTL:
        return list(_article_store.values()), _news_cache['ts']

    fresh = scrape_news()
    # Merge into the rolling store — deduplicate by URL (or preview prefix)
    for item in fresh:
        key = item['url'] if item['url'] else item['preview'][:80]
        _article_store[key] = item

    _news_cache['ts'] = now
    all_articles = list(_article_store.values())
    # Re-rank all sectors from the full accumulated article set (no clear)
    threading.Thread(target=_precompute_all_sectors, args=(all_articles,), daemon=True).start()
    return all_articles, now


_DOLLAR_TICKER = re.compile(r'\$([A-Z]{1,5})\b')

def process_news(text, url=''):
    scores = sia.polarity_scores(text)
    polarity = scores['compound']
    if polarity >= 0.05:
        label = 'POSITIVE'
    elif polarity <= -0.05:
        label = 'NEGATIVE'
    else:
        label = 'NEUTRAL'

    # Company name matching
    mentioned = {
        symbol for company, symbol in company_to_symbol.items()
        if symbol and company.lower() in text.lower()
    }
    # $TICKER pattern matching — unambiguous in financial text
    for m in _DOLLAR_TICKER.finditer(text):
        t = m.group(1)
        if t in _all_symbols:
            mentioned.add(t)

    preview = text[:160].rstrip() + ('…' if len(text) > 160 else '')
    return {
        'preview': preview,
        'url': url,
        'sentiment': label,
        'score': polarity,
        'companies': list(mentioned),
    }


def fetch_price(symbol):
    try:
        hist = yf.Ticker(symbol).history(period='2d')
        if len(hist) >= 2:
            prev = float(hist['Close'].iloc[-2])
            curr = float(hist['Close'].iloc[-1])
            return symbol, {
                'price': round(curr, 2),
                'change_pct': round(((curr - prev) / prev) * 100, 2),
            }
        elif len(hist) == 1:
            return symbol, {'price': round(float(hist['Close'].iloc[-1]), 2), 'change_pct': None}
    except Exception:
        pass
    return symbol, None


def get_stock_prices(symbols):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        return {sym: data for sym, data in ex.map(fetch_price, symbols) if data}


def _rank_sector(news_data, sector=None):
    """Pure ranking — no yfinance calls. Fast, pure Python."""
    allowed = sector_to_symbols.get(sector.lower().strip()) if sector else None
    stock_data = {}
    for item in news_data:
        for symbol in item['companies']:
            if allowed and symbol not in allowed:
                continue
            if symbol not in stock_data:
                stock_data[symbol] = {
                    'pos_total': 0.0, 'pos_count': 0,
                    'pos_articles': [], 'neg_articles': [],
                }
            if item['score'] >= 0.05:
                stock_data[symbol]['pos_total'] += item['score']
                stock_data[symbol]['pos_count'] += 1
                if len(stock_data[symbol]['pos_articles']) < 3:
                    stock_data[symbol]['pos_articles'].append(
                        {'preview': item['preview'], 'url': item['url']}
                    )
            elif item['score'] <= -0.05:
                if len(stock_data[symbol]['neg_articles']) < 3:
                    stock_data[symbol]['neg_articles'].append(
                        {'preview': item['preview'], 'url': item['url']}
                    )
    return sorted(
        [
            {
                'Symbol': sym,
                'Mentions': d['pos_count'],
                'Avg Sentiment': round(d['pos_total'] / d['pos_count'], 3),
                'Articles': d['pos_articles'],
                'NegArticles': d['neg_articles'],
                'Price': None,
            }
            for sym, d in stock_data.items() if d['pos_count'] > 0
        ],
        key=lambda x: (x['Mentions'], x['Avg Sentiment']),
        reverse=True,
    )[:50]


def _precompute_all_sectors(news_data):
    """Background thread: rank every sector in parallel, then fetch all prices once."""
    all_keys = [key for key, _ in TABS]

    # Rank all sectors simultaneously (pure Python, no I/O)
    sector_recs = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(all_keys)) as ex:
        futures = {ex.submit(_rank_sector, news_data, key or None): key for key in all_keys}
        for future in concurrent.futures.as_completed(futures):
            sector_recs[futures[future]] = future.result()

    # Collect every unique symbol across all sectors
    all_syms = {rec['Symbol'] for recs in sector_recs.values() for rec in recs}

    # One batched price fetch for all symbols
    all_prices = get_stock_prices(list(all_syms))

    # Attach prices and write to sector cache
    now = time.time()
    for key, recs in sector_recs.items():
        for rec in recs:
            rec['Price'] = all_prices.get(rec['Symbol'])
        _sector_cache[key] = {'recs': recs, 'ts': now}


def recommend_stocks(news_data, sector=None):
    """On-demand fallback used only before the background pre-compute finishes."""
    recs = _rank_sector(news_data, sector)
    if recs:
        prices = get_stock_prices([r['Symbol'] for r in recs])
        for rec in recs:
            rec['Price'] = prices.get(rec['Symbol'])
    return recs


TABS = [
    ('',              'All'),
    ('tech',          'Tech'),
    ('ai',            'AI'),
    ('hardware',      'Hardware'),
    ('semiconductor', 'Chips'),
    ('cloud',         'Cloud'),
    ('cybersecurity', 'Cyber'),
    ('finance',       'Finance'),
    ('crypto',        'Crypto'),
    ('healthcare',    'Healthcare'),
    ('biotech',       'Biotech'),
    ('pharma',        'Pharma'),
    ('space',         'Space'),
    ('defense',       'Defense'),
    ('energy',        'Energy'),
    ('renewable',     'Clean Energy'),
    ('automotive',    'Auto / EV'),
    ('gaming',        'Gaming'),
    ('media',         'Media'),
    ('telecom',       'Telecom'),
    ('retail',        'Retail'),
    ('travel',        'Travel'),
    ('industrial',    'Industrial'),
    ('food',          'Food'),
    ('reit',          'REIT'),
]


SORT_OPTIONS = [
    ('score', 'Top Picks'),
    ('alpha', 'A → Z'),
    ('gainers', '▲ Gainers'),
    ('losers',  '▼ Losers'),
]


def _apply_sort(recs, sort):
    if sort == 'alpha':
        return sorted(recs, key=lambda r: r['Symbol'])
    if sort == 'gainers':
        return sorted(
            recs,
            key=lambda r: r['Price']['change_pct'] if r['Price'] and r['Price']['change_pct'] is not None else -999,
            reverse=True,
        )
    if sort == 'losers':
        return sorted(
            recs,
            key=lambda r: r['Price']['change_pct'] if r['Price'] and r['Price']['change_pct'] is not None else 999,
        )
    return recs  # default: score (pre-sorted by rank)


def _perf_summary(recs):
    up = sum(1 for r in recs if r['Price'] and r['Price'].get('change_pct') is not None and r['Price']['change_pct'] > 0)
    down = sum(1 for r in recs if r['Price'] and r['Price'].get('change_pct') is not None and r['Price']['change_pct'] < 0)
    flat = len(recs) - up - down
    return {'up': up, 'down': down, 'flat': flat, 'total': len(recs)}


@app.route('/', methods=['GET', 'POST'])
def home():
    sector = (request.args.get('sector') or request.form.get('sector', '')).strip()
    sort   = request.args.get('sort', 'score').strip()
    custom_url = request.form.get('custom_url', '').strip()
    if custom_url and custom_url not in custom_sources:
        custom_sources.append(custom_url)

    news_data, cache_ts = get_cached_news()

    cache_entry = _sector_cache.get(sector)
    recs = list(cache_entry['recs']) if cache_entry is not None else recommend_stocks(news_data, sector=sector or None)

    recommendations = _apply_sort(recs, sort)
    perf = _perf_summary(recommendations)
    cache_age_min = int((time.time() - cache_ts) / 60)

    return render_template(
        'index.html',
        recommendations=recommendations,
        perf=perf,
        sector=sector,
        sort=sort,
        sort_options=SORT_OPTIONS,
        tabs=TABS,
        custom_sources=custom_sources,
        articles_count=len(_article_store),
        cache_age_min=cache_age_min,
    )


@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    q_upper = q.upper()
    q_lower = q.lower()

    # Resolve query to a ticker symbol
    symbol = None
    if q_upper in _all_symbols:
        symbol = q_upper
    else:
        for company, sym in company_to_symbol.items():
            if q_lower == company.lower() or q_lower in company.lower():
                symbol = sym
                break

    # Ensure news store is populated
    news_data, cache_ts = get_cached_news()
    cache_age_min = int((time.time() - cache_ts) / 60)

    search_result = None
    if symbol:
        pos_articles, neg_articles = [], []
        pos_total, pos_count = 0.0, 0
        for item in _article_store.values():
            if symbol in item['companies']:
                if item['score'] >= 0.05:
                    pos_total += item['score']
                    pos_count += 1
                    pos_articles.append({'preview': item['preview'], 'url': item['url']})
                elif item['score'] <= -0.05:
                    neg_articles.append({'preview': item['preview'], 'url': item['url']})

        _, price_data = fetch_price(symbol)

        # Find a human-readable name for the symbol
        company_name = next(
            (name for name, sym in company_to_symbol.items() if sym == symbol and len(name) > 3),
            symbol
        )

        search_result = {
            'Symbol': symbol,
            'CompanyName': company_name,
            'Mentions': pos_count,
            'AvgSentiment': round(pos_total / pos_count, 3) if pos_count else 0,
            'Articles': pos_articles,
            'NegArticles': neg_articles,
            'Price': price_data,
        }

    return render_template(
        'index.html',
        search_query=q,
        search_result=search_result,
        symbol_not_found=(q and symbol is None),
        tabs=TABS,
        sector='',
        recommendations=[],
        custom_sources=custom_sources,
        articles_count=len(_article_store),
        cache_age_min=cache_age_min,
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
