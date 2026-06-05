import os
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

company_to_symbol = {
    'Apple': 'AAPL', 'Microsoft': 'MSFT', 'Tesla': 'TSLA', 'Amazon': 'AMZN', 'Google': 'GOOGL',
    'Meta': 'META', 'Netflix': 'NFLX', 'Nvidia': 'NVDA', 'AMD': 'AMD', 'IBM': 'IBM',
    'Disney': 'DIS', 'Intel': 'INTC', 'Cisco': 'CSCO', 'Oracle': 'ORCL', 'PayPal': 'PYPL',
    'Adobe': 'ADBE', 'Salesforce': 'CRM', 'Berkshire Hathaway': 'BRK.B', 'Johnson & Johnson': 'JNJ',
    'JPMorgan Chase': 'JPM', 'Visa': 'V', 'Mastercard': 'MA', 'Walmart': 'WMT', 'Procter & Gamble': 'PG',
    'ExxonMobil': 'XOM', 'Chevron': 'CVX', 'Pfizer': 'PFE', 'Coca-Cola': 'KO', 'Pepsi': 'PEP',
    'Alphabet': 'GOOGL', 'OpenAI': None, 'SpaceX': None,
}

sector_to_symbols = {
    'tech': {'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'NVDA', 'AMD', 'IBM', 'INTC', 'CSCO', 'ORCL', 'ADBE', 'CRM'},
    'technology': {'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'NVDA', 'AMD', 'IBM', 'INTC', 'CSCO', 'ORCL', 'ADBE', 'CRM'},
    'finance': {'JPM', 'V', 'MA', 'PYPL', 'BRK.B'},
    'financial': {'JPM', 'V', 'MA', 'PYPL', 'BRK.B'},
    'consumer': {'WMT', 'KO', 'PEP', 'PG', 'DIS'},
    'energy': {'XOM', 'CVX'},
    'healthcare': {'JNJ', 'PFE'},
    'pharma': {'JNJ', 'PFE'},
    'automotive': {'TSLA'},
    'ev': {'TSLA'},
    'media': {'DIS', 'NFLX', 'META'},
    'semiconductor': {'NVDA', 'AMD', 'INTC'},
}

news_sources = [
    'https://feeds.reuters.com/reuters/businessNews',
    'https://finance.yahoo.com/rss/topstories',
    'http://rss.cnn.com/rss/money_news_international.rss',
    'https://feeds.marketwatch.com/marketwatch/topstories/',
]
custom_sources = []

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'}


def scrape_news():
    all_sources = news_sources + custom_sources
    news_data = []
    for source in all_sources:
        try:
            response = requests.get(source, timeout=10, headers=HEADERS)
            if response.status_code != 200:
                continue
            # Try XML/RSS first, fall back to HTML
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
                    desc_tag.get_text(strip=True) if desc_tag else '',
                ]))
                link_tag = item.find('link')
                url = link_tag.get_text(strip=True) if link_tag else ''
                if text:
                    processed = process_news(text, url)
                    news_data.append(processed)
        except Exception as e:
            print(f"Error scraping {source}: {e}")
    return news_data


def process_news(text, url=''):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    sentiment_label = 'POSITIVE' if polarity > 0 else 'NEGATIVE'
    mentioned_symbols = []
    for company, symbol in company_to_symbol.items():
        if symbol and company.lower() in text.lower():
            mentioned_symbols.append(symbol)
    return {
        'text': text,
        'url': url,
        'sentiment': sentiment_label,
        'score': polarity,
        'companies': list(set(mentioned_symbols)),
    }


def recommend_stocks(news_data, sector=None):
    allowed_symbols = sector_to_symbols.get(sector.lower().strip(), None) if sector else None

    stock_scores = {}
    for item in news_data:
        if item['score'] <= 0:
            continue
        for symbol in item['companies']:
            if allowed_symbols and symbol not in allowed_symbols:
                continue
            if symbol not in stock_scores:
                stock_scores[symbol] = {'total': 0.0, 'count': 0}
            stock_scores[symbol]['total'] += item['score']
            stock_scores[symbol]['count'] += 1

    recommendations = [
        {
            'Symbol': symbol,
            'Mentions': data['count'],
            'Avg Sentiment': round(data['total'] / data['count'], 3),
        }
        for symbol, data in stock_scores.items()
    ]
    recommendations.sort(key=lambda x: (x['Mentions'], x['Avg Sentiment']), reverse=True)
    return recommendations[:5]


@app.route('/', methods=['GET', 'POST'])
def home():
    sector = request.form.get('sector', '').strip()
    custom_url = request.form.get('custom_url', '').strip()
    if custom_url and custom_url not in custom_sources:
        custom_sources.append(custom_url)

    news_data = scrape_news()
    recommendations = recommend_stocks(news_data, sector=sector or None)
    articles_count = len(news_data)

    return render_template(
        'index.html',
        recommendations=recommendations,
        sector=sector,
        custom_sources=custom_sources,
        articles_count=articles_count,
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)
