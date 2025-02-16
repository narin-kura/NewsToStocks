# Investment Recommendation AI Agent - Web App

## Step 1: Import Necessary Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from textblob import TextBlob
import yfinance as yf
import requests
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='.')

## Step 2: Set Up News Scraping
news_sources = [
    'https://www.cnbc.com',
    'https://www.bloomberg.com',
    'https://www.reuters.com'
]
custom_sources = []

def scrape_news():
    all_sources = news_sources + custom_sources
    news_data = []
    for source in all_sources:
        response = requests.get(source)
        if response.status_code == 200:
            print(f"Successfully fetched {source}")
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article')
            if not articles:
                print(f"Unable to extract articles from {source}")
                continue
            for article in articles:
                paragraphs = article.find_all('p')
                full_text = ' '.join([p.get_text() for p in paragraphs])
                article_url = article.find('a', href=True)
                url = article_url['href'] if article_url else 'URL not available'
                if not full_text:
                    print(f"AI could not read content from {url}")
                elif full_text:
                    processed_info = process_news(full_text)
                    if processed_info:
                        processed_info['url'] = url  # Include URL in processed data
                        news_data.append(processed_info)
    return news_data

def process_news(text):
    """
    Analyzes the news content, extracts relevant company mentions, and determines sentiment
    """
    analysis = TextBlob(text)
    sentiment_label = 'POSITIVE' if analysis.sentiment.polarity > 0 else 'NEGATIVE'
    
    # Extract potential company mentions from the text
    mentioned_companies = []
    for company in company_to_symbol.keys():
        if company.lower() in text.lower():
            mentioned_companies.append(company_to_symbol[company])
    
    return {'text': text, 'sentiment': sentiment_label, 'companies': mentioned_companies}

## Step 3: Sentiment Analysis


def analyze_sentiments(news_data):
    sentiments = []
    for news in news_data:
        text = news['text']
        sentiment_label = news['sentiment']
        companies = news['companies']
        url = news['url']  # Extract the URL
        sentiments.append((text, sentiment_label, companies, url))
    return sentiments

## Step 4: Historical Stock Price and Correlation

def get_stock_symbol(headline):
    company_to_symbol = {
        'Apple': 'AAPL', 'Microsoft': 'MSFT', 'Tesla': 'TSLA', 'Amazon': 'AMZN', 'Google': 'GOOGL',
        'Meta': 'META', 'Netflix': 'NFLX', 'Nvidia': 'NVDA', 'AMD': 'AMD', 'IBM': 'IBM',
        'Disney': 'DIS', 'Intel': 'INTC', 'Cisco': 'CSCO', 'Oracle': 'ORCL', 'PayPal': 'PYPL',
        'Adobe': 'ADBE', 'Salesforce': 'CRM', 'Berkshire Hathaway': 'BRK.B', 'Johnson & Johnson': 'JNJ',
        'JPMorgan Chase': 'JPM', 'Visa': 'V', 'Mastercard': 'MA', 'Walmart': 'WMT', 'Procter & Gamble': 'PG',
        'ExxonMobil': 'XOM', 'Chevron': 'CVX', 'Pfizer': 'PFE', 'Coca-Cola': 'KO', 'Pepsi': 'PEP'
    }
    for company, symbol in company_to_symbol.items():
        if company.lower() in headline.lower():
            return symbol
    return None

def calculate_correlation(sentiments):
    news_df = pd.DataFrame(sentiments, columns=['Headline', 'Sentiment', 'Score'])
    if news_df.empty:
        return pd.DataFrame([], columns=['Symbol', 'Correlation', 'Avg Sentiment'])
    
    positive_news = news_df[news_df['Sentiment'] == 'POSITIVE']
    positive_news['Symbol'] = positive_news['Headline'].apply(get_stock_symbol)
    positive_news = positive_news.dropna(subset=['Symbol'])

    correlations = []
    for symbol in positive_news['Symbol'].unique():
        try:
            stock_data = yf.download(symbol, period='1mo', interval='1d')
            if stock_data.empty:
                raise Exception("Empty data")
        except:
            api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=LCIIJFIRJO051VXB"
            response = requests.get(api_url)
            data = response.json()
            if 'Time Series (Daily)' in data:
                stock_data = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
                stock_data = stock_data.astype(float)
                stock_data['Returns'] = stock_data['4. close'].pct_change()
            else:
                continue
        
        sentiment_scores = positive_news[positive_news['Symbol'] == symbol]['Score']
        sentiment_avg = np.mean(sentiment_scores)
        correlation = stock_data['Returns'].corr(pd.Series([sentiment_avg] * len(stock_data)))
        correlations.append((symbol, correlation, sentiment_avg))
    
    if not correlations:
        return pd.DataFrame([], columns=['Symbol', 'Correlation', 'Avg Sentiment'])

    correlation_df = pd.DataFrame(correlations, columns=['Symbol', 'Correlation', 'Avg Sentiment'])
    recommendations = correlation_df.sort_values(by='Correlation', ascending=False).head(4)
    return recommendations

## Step 5: Web Interface
@app.route('/', methods=['GET', 'POST'])
def home():
    sector = request.form.get('sector')  # Get user input
    news_data = scrape_news()
    sentiments = analyze_sentiments(news_data)
    recommendations = calculate_correlation(sentiments)
    # Filter recommendations by sector if provided
    if sector and not recommendations.empty:
        recommendations = [rec for rec in recommendations.to_dict('records') if sector.lower() in rec['Symbol'].lower()]
    else:
        recommendations = recommendations.to_dict('records') if not recommendations.empty else []
    custom_url = request.form.get('custom_url')
    if custom_url:  # Add custom news website
        custom_sources.append(custom_url)
    return render_template('index.html', recommendations=recommendations, sector=sector, custom_sources=custom_sources)


import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=port, debug=True)
