import streamlit as st
import pandas as pd
import numpy as np
import random
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import re
from tradingview_ta import TA_Handler, Interval
from kmi30_data import get_kmi30_analysis
from ai_agent import get_stock_recommendations
import asyncio

# Initialize session state
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'risk_profile' not in st.session_state:
    st.session_state.risk_profile = None
if 'analysis_df' not in st.session_state:
    st.session_state.analysis_df = None
if 'kmi30_data' not in st.session_state:
    st.session_state.kmi30_data = None
if 'ai_recommendations' not in st.session_state:
    st.session_state.ai_recommendations = None

# Risk assessment questions
risk_questions = [
    {
        'id': 1,
        'question': "What is your primary investment goal?",
        'options': [
            {'value': 'preservation', 'label': 'Capital preservation', 'points': 1},
            {'value': 'income', 'label': 'Regular income', 'points': 2},
            {'value': 'growth', 'label': 'Long-term growth', 'points': 3},
            {'value': 'aggressive', 'label': 'Aggressive growth', 'points': 4}
        ]
    },
    {
        'id': 2,
        'question': "What is your investment time horizon?",
        'options': [
            {'value': 'short', 'label': 'Less than 2 years', 'points': 1},
            {'value': 'medium', 'label': '2-5 years', 'points': 2},
            {'value': 'long', 'label': '5-10 years', 'points': 3},
            {'value': 'very_long', 'label': 'More than 10 years', 'points': 4}
        ]
    },
    {
        'id': 3,
        'question': "How would you react to a 20% drop in your portfolio?",
        'options': [
            {'value': 'panic', 'label': 'Sell everything immediately', 'points': 1},
            {'value': 'worry', 'label': 'Sell some investments', 'points': 2},
            {'value': 'hold', 'label': 'Hold and wait for recovery', 'points': 3},
            {'value': 'buy', 'label': 'Buy more at lower prices', 'points': 4}
        ]
    },
    {
        'id': 4,
        'question': "What is your experience with investing?",
        'options': [
            {'value': 'none', 'label': 'No experience', 'points': 1},
            {'value': 'basic', 'label': 'Basic knowledge', 'points': 2},
            {'value': 'intermediate', 'label': 'Intermediate experience', 'points': 3},
            {'value': 'advanced', 'label': 'Advanced investor', 'points': 4}
        ]
    },
    {
        'id': 5,
        'question': "What percentage of your income can you invest?",
        'options': [
            {'value': 'low', 'label': 'Less than 10%', 'points': 1},
            {'value': 'medium', 'label': '10-20%', 'points': 2},
            {'value': 'high', 'label': '20-30%', 'points': 3},
            {'value': 'very_high', 'label': 'More than 30%', 'points': 4}
        ]
    }
]

# Smart beta strategies
strategies = [
    {
        'name': "Quality",
        'description': "High-quality companies with strong fundamentals",
        'factors': ["quality"],
        'riskProfile': "conservative",
        'expectedReturn': 8.5,
        'expectedVolatility': 12.0
    },
    {
        'name': "Value",
        'description': "Undervalued companies trading below intrinsic value",
        'factors': ["value"],
        'riskProfile': "moderate",
        'expectedReturn': 9.2,
        'expectedVolatility': 15.5
    },
    {
        'name': "Momentum",
        'description': "Companies with strong price momentum",
        'factors': ["momentum"],
        'riskProfile': "aggressive",
        'expectedReturn': 11.0,
        'expectedVolatility': 18.0
    },
    {
        'name': "Growth",
        'description': "Companies with high growth potential",
        'factors': ["growth"],
        'riskProfile': "aggressive",
        'expectedReturn': 12.5,
        'expectedVolatility': 20.0
    },
    {
        'name': "Low Volatility",
        'description': "Stable companies with lower price volatility",
        'factors': ["lowVolatility"],
        'riskProfile': "conservative",
        'expectedReturn': 7.8,
        'expectedVolatility': 9.5
    },
    {
        'name': "Quality Value",
        'description': "High-quality companies at attractive valuations",
        'factors': ["quality", "value"],
        'riskProfile': "moderate",
        'expectedReturn': 9.8,
        'expectedVolatility': 13.5
    },
    {
        'name': "Quality Momentum",
        'description': "High-quality companies with positive momentum",
        'factors': ["quality", "momentum"],
        'riskProfile': "moderate",
        'expectedReturn': 10.5,
        'expectedVolatility': 14.8
    }
]

class SmartBetaEngine:
    def __init__(self):
        self.stocks = self._generate_mock_stocks()
    
    def _generate_mock_stocks(self) -> List[Dict[str, Any]]:
        stocks = []
        for i in range(50):
            stock = {
                'symbol': f'STK{i+1:03d}',
                'name': f'Company {i+1}',
                'roe': random.uniform(5, 25),
                'pe_ratio': random.uniform(5, 30),
                'pb_ratio': random.uniform(0.5, 5),
                'revenue_growth': random.uniform(-10, 30),
                'momentum': random.uniform(-20, 40),
                'volatility': random.uniform(5, 30)
            }
            stocks.append(stock)
        return stocks
    
    def calculate_quality_score(self, stock: Dict[str, Any]) -> float:
        roe_score = min(100, max(0, (stock['roe'] - 5) * 5))
        return roe_score
    
    def calculate_value_score(self, stock: Dict[str, Any]) -> float:
        pe_score = min(100, max(0, (30 - stock['pe_ratio']) * 4))
        pb_score = min(100, max(0, (5 - stock['pb_ratio']) * 20))
        return (pe_score + pb_score) / 2
    
    def calculate_momentum_score(self, stock: Dict[str, Any]) -> float:
        return min(100, max(0, (stock['momentum'] + 20) * 1.67))
    
    def calculate_growth_score(self, stock: Dict[str, Any]) -> float:
        return min(100, max(0, (stock['revenue_growth'] + 10) * 2.5))
    
    def calculate_low_volatility_score(self, stock: Dict[str, Any]) -> float:
        return min(100, max(0, (30 - stock['volatility']) * 4))
    
    def get_stock_recommendations(self, risk_profile: str, num_recommendations: int = 10) -> List[Dict[str, Any]]:
        # Filter strategies based on risk profile
        suitable_strategies = [s for s in strategies if s['riskProfile'] == risk_profile]
        
        # Calculate scores for each stock
        scored_stocks = []
        for stock in self.stocks:
            scores = {}
            for strategy in suitable_strategies:
                strategy_score = 0
                for factor in strategy['factors']:
                    if factor == 'quality':
                        strategy_score += self.calculate_quality_score(stock)
                    elif factor == 'value':
                        strategy_score += self.calculate_value_score(stock)
                    elif factor == 'momentum':
                        strategy_score += self.calculate_momentum_score(stock)
                    elif factor == 'growth':
                        strategy_score += self.calculate_growth_score(stock)
                    elif factor == 'lowVolatility':
                        strategy_score += self.calculate_low_volatility_score(stock)
                
                strategy_score /= len(strategy['factors'])
                scores[strategy['name']] = strategy_score
            
            # Find best strategy for this stock
            best_strategy = max(scores.items(), key=lambda x: x[1])
            scored_stocks.append({
                'stock': stock,
                'strategy': best_strategy[0],
                'score': best_strategy[1]
            })
        
        # Sort by score and return top recommendations
        scored_stocks.sort(key=lambda x: x['score'], reverse=True)
        return scored_stocks[:num_recommendations]

def calculate_risk_profile(answers: Dict[str, int]) -> str:
    total_points = sum(answers.values())
    if total_points <= 8:
        return "conservative"
    elif total_points <= 15:
        return "moderate"
    else:
        return "aggressive"

def display_question(question: Dict[str, Any]):
    st.write(f"Question {question['id']} of {len(risk_questions)}")
    st.progress(question['id'] / len(risk_questions))
    
    st.write(question['question'])
    
    options = [opt['label'] for opt in question['options']]
    selected_option = st.radio("Select your answer:", options, key=f"q{question['id']}")
    
    if selected_option:
        selected_points = next(opt['points'] for opt in question['options'] if opt['label'] == selected_option)
        st.session_state.answers[question['id']] = selected_points

def get_kmi30_tickers():
    """
    Scrape KMI-30 tickers from PSX website
    Returns: List of ticker symbols
    """
    url = 'https://dps.psx.com.pk/indices/KMI30'
    try:
        # Fetch the webpage
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"Failed to fetch webpage. Status code: {response.status_code}")
            return []

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        st.success("Webpage fetched and parsed successfully.")

        # Find all tables on the page
        tables = soup.find_all('table')
        st.info(f"Found {len(tables)} tables on the page.")

        if not tables:
            st.warning("No tables found on the webpage.")
            return []

        # Look for a table that likely contains stock symbols
        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue

            # Check header row for a clue
            header = rows[0]
            header_cells = header.find_all('th')
            symbol_index = None

            # Possible header names for the symbol column
            symbol_keywords = ['symbol', 'ticker', 'code', 'company']
            for i, cell in enumerate(header_cells):
                cell_text = cell.text.strip().lower()
                if any(keyword in cell_text for keyword in symbol_keywords):
                    symbol_index = i
                    break

            # If no clear header, try to infer from data rows
            if symbol_index is None and len(rows) > 1:
                first_data_row = rows[1]
                cells = first_data_row.find_all('td')
                for i, cell in enumerate(cells):
                    if re.match(r'^[A-Z]{2,5}$', cell.text.strip()):
                        symbol_index = i
                        break

            # Extract symbols if we found a symbol column
            if symbol_index is not None:
                tickers = []
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) > symbol_index:
                        symbol = cells[symbol_index].text.strip()
                        if re.match(r'^[A-Z]{2,5}$', symbol):
                            tickers.append(symbol)
                if tickers:
                    st.success(f"Extracted {len(tickers)} tickers")
                    return tickers

        st.warning("No table with identifiable stock symbols found.")
        return []

    except Exception as e:
        st.error(f"An error occurred while fetching tickers: {e}")
        return []

def get_technical_analysis(tickers):
    """
    Get comprehensive technical analysis for a list of tickers
    """
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(tickers):
        try:
            status_text.text(f"Analyzing {symbol}...")
            handler = TA_Handler(
                symbol=symbol,
                screener="pakistan",
                exchange="PSX",
                interval=Interval.INTERVAL_1_DAY
            )
            analysis = handler.get_analysis()

            result = {
                'Ticker': f"{symbol}.KAR",
                'Current Price': analysis.indicators.get('close', 'N/A'),
                'Summary': analysis.summary.get('RECOMMENDATION', 'N/A'),
                'RSI': round(analysis.indicators.get('RSI', 0), 2) if analysis.indicators.get('RSI') else 'N/A',
                'MACD': round(analysis.indicators.get('MACD.macd', 0), 2) if analysis.indicators.get('MACD.macd') else 'N/A',
                'MACD Signal': round(analysis.indicators.get('MACD.signal', 0), 2) if analysis.indicators.get('MACD.signal') else 'N/A',
                'ADX': round(analysis.indicators.get('ADX', 0), 2) if analysis.indicators.get('ADX') else 'N/A',
                'Volume': round(analysis.indicators.get('volume', 0), 2) if analysis.indicators.get('volume') else 'N/A',
            }
            results.append(result)
            
        except Exception as e:
            st.warning(f"Error analyzing {symbol}: {e}")
            results.append({
                'Ticker': f"{symbol}.KAR",
                'Current Price': 'N/A',
                'Summary': 'N/A',
                'RSI': 'N/A',
                'MACD': 'N/A',
                'MACD Signal': 'N/A',
                'ADX': 'N/A',
                'Volume': 'N/A',
            })
        
        progress_bar.progress((i + 1) / len(tickers))
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(results)

def analyze_kmi30_stocks():
    """
    Analyze KMI-30 stocks and return recommendations based on risk profile
    """
    st.write("### Analyzing KMI-30 Stocks...")
    
    # Get KMI-30 tickers
    tickers = get_kmi30_tickers()
    
    if not tickers:
        st.warning("No tickers found. Using fallback list...")
        tickers = ['ATRL', 'DGKC', 'EFERT', 'EPCL', 'FABL', 'HBL', 'MCB', 'UBL', 'LUCK', 'ENGRO']
    
    # Get technical analysis
    df = get_technical_analysis(tickers)
    
    # Filter recommendations based on risk profile
    if st.session_state.risk_profile == "conservative":
        df = df[df['Summary'].isin(['STRONG_BUY', 'BUY'])]
    elif st.session_state.risk_profile == "moderate":
        df = df[df['Summary'].isin(['STRONG_BUY', 'BUY', 'NEUTRAL'])]
    else:  # aggressive
        df = df[df['Summary'].isin(['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL'])]
    
    return df

def main():
    st.title("Investment Risk Assessment & Smart Beta Recommendations")
    
    if st.session_state.risk_profile is None:
        # Display current question
        current_q = risk_questions[st.session_state.current_question]
        display_question(current_q)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.current_question > 0:
                if st.button("Previous"):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            if st.session_state.current_question < len(risk_questions) - 1:
                if st.button("Next"):
                    if st.session_state.current_question + 1 not in st.session_state.answers:
                        st.error("Please select an answer before proceeding.")
                    else:
                        st.session_state.current_question += 1
                        st.rerun()
            else:
                if st.button("Complete"):
                    if len(st.session_state.answers) < len(risk_questions):
                        st.error("Please answer all questions before completing.")
                    else:
                        with st.spinner("Calculating your risk profile and analyzing KMI-30 stocks..."):
                            # Calculate risk profile
                            st.session_state.risk_profile = calculate_risk_profile(st.session_state.answers)
                            
                            # Fetch KMI-30 data
                            st.session_state.kmi30_data = get_kmi30_analysis()
                            
                            # Get AI recommendations
                            st.session_state.ai_recommendations = get_stock_recommendations(
                                st.session_state.risk_profile,
                                st.session_state.kmi30_data,
                                st.session_state.answers
                            )
                        st.rerun()
    else:
        # Display results
        st.write(f"Your risk profile is: {st.session_state.risk_profile.capitalize()}")
        
        # Display KMI-30 data
        if st.session_state.kmi30_data is not None:
            st.write("### KMI-30 Technical Analysis")
            st.dataframe(st.session_state.kmi30_data)
            
            # Display recommendations summary
            st.write("### KMI-30 Summary")
            recommendations = st.session_state.kmi30_data['Summary'].value_counts()
            for rec, count in recommendations.items():
                if rec != 'N/A':
                    st.write(f"{rec}: {count}")
        
        # Display AI recommendations
        if st.session_state.ai_recommendations:
            st.write("### AI-Powered Recommendations")
            st.write(st.session_state.ai_recommendations)
        
        if st.button("Start Over"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main() 