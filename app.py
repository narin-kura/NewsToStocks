##app.run(host='0.0.0.0', port=7860)
    
    
    # Investment Recommendation AI Agent - Web App

## Step 1: Import Necessary Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from textblob import TextBlob
import yfinance as yf
from flask import Flask, render_template, request
import json
import os

app = Flask(__name__, template_folder='.')

## Step 2: Set Up News Scraping
news_sources = [
    'https://www.cnbc.com',
    'https://www.bloomberg.com',
    'https://www.reuters.com'
]
company_to_symbol = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "Meta": "META",
    "Netflix": "NFLX",
    "Nvidia": "NVDA",
    "AMD": "AMD",
    "IBM": "IBM"
}
custom_sources = []

def scrape_news():
    all_sources = news_sources + custom_sources
    news_data = []
    for source in all_sources:
        response = requests.get(source)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            headlines = soup.find_all('h2')
            for headline in headlines:
                news_data.append(headline.text)
    return news_data

## Step 3: Sentiment Analysis


def analyze_sentiments(news_data):
    sentiments = []
    for news in news_data:
        analysis = TextBlob(news)
        sentiment_label = 'POSITIVE' if analysis.sentiment.polarity > 0 else 'NEGATIVE'
        sentiments.append((news, sentiment_label, analysis.sentiment.polarity))
    return sentiments

## Step 4: Historical Stock Price and Correlation

def get_stock_symbol(headline):
    # Placeholder function for entity recognition
    """
    Extracts stock symbols based on company mentions in news headlines.
    """
    for company, symbol in company_to_symbol.items():
        if company.lower() in headline.lower():
            return symbol
    return None  

def calculate_correlation(sentiments):
 #   news_df = pd.DataFrame(sentiments, columns=['Headline', 'Sentiment', 'Score'])
 #   positive_news = news_df[news_df['Sentiment'] == 'POSITIVE']
 #   positive_news['Symbol'] = positive_news['Headline'].apply(get_stock_symbol)
 #   positive_news = positive_news.dropna(subset=['Symbol'])

#    if positive_news.empty:
#        return pd.DataFrame([{"Symbol": "AAPL", "Correlation": 0.8, "Avg Sentiment": 0.7},  # Default suggestions
 #                            {"Symbol": "MSFT", "Correlation": 0.75, "Avg Sentiment": 0.65},
  #                           {"Symbol": "TSLA", "Correlation": 0.72, "Avg Sentiment": 0.6},
  #                           {"Symbol": "NVDA", "Correlation": 0.7, "Avg Sentiment": 0.55}])

#    correlations = []
#    for symbol in positive_news['Symbol'].unique():
#        stock_data = yf.download(symbol, period='1mo', interval='1d')
#        stock_data['Returns'] = stock_data['Close'].pct_change()
#        sentiment_scores = positive_news[positive_news['Symbol'] == symbol]['Score']
#        sentiment_avg = np.mean(sentiment_scores)
#        correlation = stock_data['Returns'].corr(pd.Series([sentiment_avg] * len(stock_data)))
#        correlations.append((symbol, correlation, sentiment_avg))

 #   correlation_df = pd.DataFrame(correlations, columns=['Symbol', 'Correlation', 'Avg Sentiment'])
 #   recommendations = correlation_df.sort_values(by='Correlation', ascending=False).head(4)

  #  return recommendations


def calculate_correlation(sentiments):
    news_df = pd.DataFrame(sentiments, columns=['Headline', 'Sentiment', 'Score'])
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
            # Use an alternative API if yfinance fails
            api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=LCIIJFIRJO051VXB'
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
    if sector:
        recommendations = [rec for rec in recommendations if sector.lower() in rec['Symbol'].lower()]

    custom_url = request.form.get('custom_url')
    if custom_url and custom_url not in custom_sources:  # Avoid duplicates
        custom_sources.append(custom_url)

    response = render_template(
        'index.html',
        recommendations=recommendations,
        sector=sector,
        custom_sources=custom_sources
    )
    
    # Set Content-Type explicitly to avoid issues in Hugging Face
    return resp


if __name__ == '__main__':
  
    port = int(os.environ.get("PORT", 7860))
    app.run(host='0.0.0.0', port=7860, debug=True)


