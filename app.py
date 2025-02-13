# Investment Recommendation AI Agent - Web App

## Step 1: Import Necessary Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from transformers import pipeline
import yfinance as yf
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
            soup = BeautifulSoup(response.content, 'html.parser')
            headlines = soup.find_all('h2')
            for headline in headlines:
                news_data.append(headline.text)
    return news_data

## Step 3: Sentiment Analysis
sentiment_analyzer = pipeline('sentiment-analysis')

def analyze_sentiments(news_data):
    sentiments = []
    for news in news_data:
        result = sentiment_analyzer(news)
        sentiments.append((news, result[0]['label'], result[0]['score']))
    return sentiments

## Step 4: Historical Stock Price and Correlation

def get_stock_symbol(headline):
    # Placeholder function for entity recognition
    return 'AAPL' if 'Apple' in headline else None

def calculate_correlation(sentiments):
    news_df = pd.DataFrame(sentiments, columns=['Headline', 'Sentiment', 'Score'])
    positive_news = news_df[news_df['Sentiment'] == 'POSITIVE']
    positive_news['Symbol'] = positive_news['Headline'].apply(get_stock_symbol)
    positive_news = positive_news.dropna(subset=['Symbol'])

    correlations = []
    for symbol in positive_news['Symbol'].unique():
        stock_data = yf.download(symbol, period='1mo', interval='1d')
        stock_data['Returns'] = stock_data['Close'].pct_change()
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
    custom_url = request.form.get('custom_url')  # Get custom news website
    
    # Add custom source if provided
    if custom_url and custom_url not in custom_sources:
        custom_sources.append(custom_url)

    news_data = scrape_news()
    sentiments = analyze_sentiments(news_data)
    recommendations = calculate_correlation(sentiments)

    # Filter recommendations by sector if provided
    if sector:
        recommendations = [rec for rec in recommendations.to_dict('records') if sector.lower() in rec['Symbol'].lower()]
    else:
        recommendations = recommendations.to_dict('records')

    return render_template('index.html', recommendations=recommendations, sector=sector, custom_sources=custom_sources)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)
