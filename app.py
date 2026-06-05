import os
import time
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
    # Healthcare / Pharma
    'Johnson & Johnson': 'JNJ', 'Pfizer': 'PFE', 'Moderna': 'MRNA',
    'AstraZeneca': 'AZN', 'Merck': 'MRK', 'Abbott': 'ABT',
    'UnitedHealth': 'UNH', 'Eli Lilly': 'LLY', 'Amgen': 'AMGN',
    'Gilead': 'GILD', 'Biogen': 'BIIB', 'CVS': 'CVS',
    # Energy
    'ExxonMobil': 'XOM', 'Exxon': 'XOM', 'Chevron': 'CVX',
    'ConocoPhillips': 'COP', 'Shell': 'SHEL', 'BP': 'BP',
    # Automotive
    'Ford': 'F', 'General Motors': 'GM', 'Rivian': 'RIVN', 'Lucid': 'LCID',
    # Industrial / Other
    'Boeing': 'BA', 'Lockheed Martin': 'LMT', 'Raytheon': 'RTX',
    'Caterpillar': 'CAT', 'General Electric': 'GE', '3M': 'MMM',
    'FedEx': 'FDX', 'UPS': 'UPS',
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
                 'DIS', 'CMCSA', 'ABNB', 'UBER', 'LYFT', 'DASH'},
    'energy': {'XOM', 'CVX', 'COP', 'SHEL', 'BP'},
    'healthcare': {'JNJ', 'PFE', 'MRNA', 'AZN', 'MRK', 'ABT', 'UNH', 'LLY', 'AMGN',
                   'GILD', 'BIIB', 'CVS'},
    'pharma': {'PFE', 'MRNA', 'AZN', 'MRK', 'LLY', 'AMGN', 'GILD', 'BIIB'},
    'semiconductor': {'NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'AMAT', 'MU', 'TXN'},
    'automotive': {'TSLA', 'F', 'GM', 'RIVN', 'LCID'},
    'ev': {'TSLA', 'RIVN', 'LCID'},
    'media': {'DIS', 'NFLX', 'META', 'CMCSA'},
    'industrial': {'BA', 'LMT', 'RTX', 'CAT', 'GE', 'MMM', 'FDX', 'UPS'},
    'cybersecurity': {'CRWD', 'PANW', 'FTNT', 'NET', 'DDOG'},
    'cloud': {'SNOW', 'NET', 'DDOG', 'MDB', 'NOW', 'WDAY', 'CRM', 'MSFT', 'AMZN', 'GOOGL'},
    'crypto': {'COIN', 'SQ', 'HOOD', 'PYPL'},
}

news_sources = [
    'https://feeds.reuters.com/reuters/businessNews',
    'https://finance.yahoo.com/rss/topstories',
    'http://rss.cnn.com/rss/money_news_international.rss',
    'https://feeds.marketwatch.com/marketwatch/topstories/',
    'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
]
custom_sources = []

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; NewsToStocks/1.0)'}

_news_cache = {'data': None, 'ts': 0}
CACHE_TTL = 900  # 15 minutes


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
    if _news_cache['data'] is not None and (now - _news_cache['ts']) < CACHE_TTL:
        return _news_cache['data'], _news_cache['ts']
    data = scrape_news()
    _news_cache['data'] = data
    _news_cache['ts'] = now
    return data, now


def process_news(text, url=''):
    scores = sia.polarity_scores(text)
    polarity = scores['compound']
    if polarity >= 0.05:
        label = 'POSITIVE'
    elif polarity <= -0.05:
        label = 'NEGATIVE'
    else:
        label = 'NEUTRAL'
    mentioned_symbols = list({
        symbol for company, symbol in company_to_symbol.items()
        if symbol and company.lower() in text.lower()
    })
    preview = text[:160].rstrip() + ('…' if len(text) > 160 else '')
    return {
        'preview': preview,
        'url': url,
        'sentiment': label,
        'score': polarity,
        'companies': mentioned_symbols,
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


def recommend_stocks(news_data, sector=None):
    allowed = sector_to_symbols.get(sector.lower().strip()) if sector else None
    stock_data = {}
    for item in news_data:
        if item['score'] < 0.05:
            continue
        for symbol in item['companies']:
            if allowed and symbol not in allowed:
                continue
            if symbol not in stock_data:
                stock_data[symbol] = {'total': 0.0, 'count': 0, 'articles': []}
            stock_data[symbol]['total'] += item['score']
            stock_data[symbol]['count'] += 1
            if len(stock_data[symbol]['articles']) < 3:
                stock_data[symbol]['articles'].append({
                    'preview': item['preview'],
                    'url': item['url'],
                })

    recommendations = sorted(
        [
            {
                'Symbol': sym,
                'Mentions': d['count'],
                'Avg Sentiment': round(d['total'] / d['count'], 3),
                'Articles': d['articles'],
                'Price': None,
            }
            for sym, d in stock_data.items()
        ],
        key=lambda x: (x['Mentions'], x['Avg Sentiment']),
        reverse=True,
    )[:6]

    if recommendations:
        prices = get_stock_prices([r['Symbol'] for r in recommendations])
        for rec in recommendations:
            rec['Price'] = prices.get(rec['Symbol'])

    return recommendations


@app.route('/', methods=['GET', 'POST'])
def home():
    sector = request.form.get('sector', '').strip()
    custom_url = request.form.get('custom_url', '').strip()
    if custom_url and custom_url not in custom_sources:
        custom_sources.append(custom_url)

    news_data, cache_ts = get_cached_news()
    recommendations = recommend_stocks(news_data, sector=sector or None)
    cache_age_min = int((time.time() - cache_ts) / 60)

    return render_template(
        'index.html',
        recommendations=recommendations,
        sector=sector,
        custom_sources=custom_sources,
        articles_count=len(news_data),
        cache_age_min=cache_age_min,
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
