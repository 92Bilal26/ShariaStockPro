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
import os

# Set page configuration
st.set_page_config(
    page_title="Sharia Stock Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open(os.path.join(os.path.dirname(__file__), 'style.css')) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
    # Progress indicator
    st.markdown(f"<p style='color: #64748b; font-size: 0.9rem;'>Question {question['id']} of {len(risk_questions)}</p>", unsafe_allow_html=True)
    st.progress(question['id'] / len(risk_questions))
    
    # Question styling
    st.markdown(f"<h3 style='margin-top: 1.5rem; margin-bottom: 1.5rem;'>{question['question']}</h3>", unsafe_allow_html=True)
    
    # Create a container for options with better styling
    options_container = st.container()
    
    with options_container:
        # Options with better styling
        options = [opt['label'] for opt in question['options']]
        selected_option = st.radio("Select your answer:", options, key=f"q{question['id']}", label_visibility="collapsed")
        
        # Get option descriptions based on question type
        option_descriptions = {}
        
        if question['id'] == 1:  # Investment goal
            option_descriptions = {
                'Capital preservation': 'Focus on protecting your principal investment with minimal risk.',
                'Regular income': 'Generate consistent income from your investments.',
                'Long-term growth': 'Grow your capital over time with moderate risk.',
                'Aggressive growth': 'Maximize returns with higher risk tolerance.'
            }
        elif question['id'] == 2:  # Time horizon
            option_descriptions = {
                'Less than 2 years': 'Short-term investments for near-future goals.',
                '2-5 years': 'Medium-term investments for goals in the next few years.',
                '5-10 years': 'Longer-term investments allowing for some market fluctuations.',
                'More than 10 years': 'Very long-term investments that can withstand market cycles.'
            }
        elif question['id'] == 3:  # Market drop reaction
            option_descriptions = {
                'Sell everything immediately': 'You prioritize capital preservation above all else.',
                'Sell some investments': 'You prefer to reduce risk when markets decline.',
                'Hold and wait for recovery': 'You understand market cycles and can tolerate temporary losses.',
                'Buy more at lower prices': 'You see market declines as buying opportunities.'
            }
        elif question['id'] == 4:  # Investment experience
            option_descriptions = {
                'No experience': 'You are new to investing and still learning the basics.',
                'Basic knowledge': 'You understand fundamental investment concepts.',
                'Intermediate experience': 'You have experience with various investment types.',
                'Advanced investor': 'You have extensive knowledge and experience in investing.'
            }
        elif question['id'] == 5:  # Income percentage
            option_descriptions = {
                'Less than 10%': 'Conservative allocation of your income to investments.',
                '10-20%': 'Moderate allocation of your income to investments.',
                '20-30%': 'Significant allocation of your income to investments.',
                'More than 30%': 'Substantial allocation of your income to investments.'
            }
        
        # Display description for selected option if available
        if selected_option and selected_option in option_descriptions:
            st.markdown(f"<div style='background-color: #f0f9ff; padding: 1rem; border-radius: 8px; margin-top: 1rem;'><p><strong>{selected_option}:</strong> {option_descriptions[selected_option]}</p></div>", unsafe_allow_html=True)
    
    # Store the answer
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
    # Create sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/mosque.png", width=80)
        st.title("Sharia Stock Pro")
        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "Sharia Stock Pro helps you find Shariah-compliant investments "
            "that match your risk profile using smart beta strategies and AI."
        )
        st.markdown("---")
        
        if st.session_state.risk_profile is not None:
            risk_color = {
                "conservative": "conservative",
                "moderate": "moderate",
                "aggressive": "aggressive"
            }[st.session_state.risk_profile]
            
            st.markdown(f"### Your Profile")
            st.markdown(f"<div class='risk-badge {risk_color}'>{st.session_state.risk_profile.capitalize()}</div>", unsafe_allow_html=True)
            
            if st.button("🔄 Start Over", key="sidebar_reset"):
                st.session_state.clear()
                st.rerun()
    
    # Main content area
    st.markdown("<h1>Investment Risk Assessment & Smart Beta Recommendations</h1>", unsafe_allow_html=True)
    
    # Create a container for the main content without empty div
    main_container = st.container()
    
    with main_container:
        if st.session_state.risk_profile is None:
            # Assessment phase - Remove empty div wrapper
            # Introduction text for first question
            if st.session_state.current_question == 0:
                st.markdown(
                    "<p style='font-size: 1.1rem; margin-bottom: 2rem;'>"
                    "Welcome to Sharia Stock Pro! Let's assess your investment risk profile "
                    "to provide you with personalized Shariah-compliant investment recommendations."
                    "</p>",
                    unsafe_allow_html=True
                )
            
            # Display current question
            current_q = risk_questions[st.session_state.current_question]
            display_question(current_q)
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.current_question > 0:
                    if st.button("⬅️ Previous"):
                        st.session_state.current_question -= 1
                        st.rerun()
            
            with col2:
                if st.session_state.current_question < len(risk_questions) - 1:
                    if st.button("Next ➡️"):
                        if st.session_state.current_question + 1 not in st.session_state.answers:
                            st.error("Please select an answer before proceeding.")
                        else:
                            st.session_state.current_question += 1
                            st.rerun()
                else:
                    if st.button("Complete Assessment ✅"):
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
            # Results phase
            # Profile summary card
            st.markdown("<div class='result-card'>", unsafe_allow_html=True)
            
            risk_color = {
                "conservative": "conservative",
                "moderate": "moderate",
                "aggressive": "aggressive"
            }[st.session_state.risk_profile]
            
            st.markdown(f"<h2>Your Investment Profile</h2>", unsafe_allow_html=True)
            st.markdown(f"<div class='risk-badge {risk_color}'>{st.session_state.risk_profile.capitalize()}</div>", unsafe_allow_html=True)
            
            profile_descriptions = {
                "conservative": "You prefer stability and capital preservation over high returns. Your portfolio should focus on low-risk, Shariah-compliant investments.",
                "moderate": "You seek a balance between growth and stability. Your portfolio should include a mix of growth-oriented and stable Shariah-compliant investments.",
                "aggressive": "You prioritize growth and can tolerate higher volatility. Your portfolio should focus on growth-oriented Shariah-compliant investments with higher return potential."
            }
            
            st.markdown(f"<p>{profile_descriptions[st.session_state.risk_profile]}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Create tabs for different sections
            tab1, tab2, tab3 = st.tabs(["📊 KMI-30 Analysis", "🧠 AI Recommendations", "📈 Smart Beta Strategies"])
            
            with tab1:
                # Display KMI-30 data
                if st.session_state.kmi30_data is not None:
                    st.markdown("<h3>KMI-30 Technical Analysis</h3>", unsafe_allow_html=True)
                    
                    # Style the dataframe
                    st.dataframe(
                        st.session_state.kmi30_data.style.apply(
                            lambda x: ['background-color: #dcfce7' if v == 'STRONG_BUY' else
                                      'background-color: #d1fae5' if v == 'BUY' else
                                      'background-color: #fef9c3' if v == 'NEUTRAL' else
                                      'background-color: #fee2e2' if v == 'SELL' else
                                      'background-color: #fecaca' if v == 'STRONG_SELL' else ''
                                      for v in x], subset=['Summary']
                        ),
                        use_container_width=True
                    )
                    
                    # Display recommendations summary
                    st.markdown("<h3>KMI-30 Summary</h3>", unsafe_allow_html=True)
                    recommendations = st.session_state.kmi30_data['Summary'].value_counts()
                    
                    # Create columns for recommendation counts
                    cols = st.columns(len([r for r in recommendations.items() if r[0] != 'N/A']))
                    
                    i = 0
                    for rec, count in recommendations.items():
                        if rec != 'N/A':
                            with cols[i]:
                                st.markdown(f"<div class='recommendation-item {rec}'><h4>{rec}</h4><p style='font-size: 1.5rem; font-weight: bold;'>{count}</p></div>", unsafe_allow_html=True)
                            i += 1
            
            with tab2:
                # Display AI recommendations
                if st.session_state.ai_recommendations:
                    st.markdown("<h3>AI-Powered Recommendations</h3>", unsafe_allow_html=True)
                    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                    st.markdown(st.session_state.ai_recommendations, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with tab3:
                # Display Smart Beta Strategies
                st.markdown("<h3>Smart Beta Strategies for Your Profile</h3>", unsafe_allow_html=True)
                
                # Filter strategies based on risk profile
                filtered_strategies = [s for s in strategies if s['riskProfile'] == st.session_state.risk_profile]
                
                if filtered_strategies:
                    # Create columns for strategies
                    strategy_cols = st.columns(min(len(filtered_strategies), 3))  # Limit to 3 columns per row for better display
                    
                    for i, strategy in enumerate(filtered_strategies):
                        with strategy_cols[i % len(strategy_cols)]:
                            st.markdown(f"<div class='result-card'>", unsafe_allow_html=True)
                            st.markdown(f"<h4>{strategy['name']}</h4>", unsafe_allow_html=True)
                            st.markdown(f"<p>{strategy['description']}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p><strong>Expected Return:</strong> {strategy['expectedReturn']}%</p>", unsafe_allow_html=True)
                            st.markdown(f"<p><strong>Volatility:</strong> {strategy['expectedVolatility']}%</p>", unsafe_allow_html=True)
                            
                            # Add factors used
                            factors_text = ", ".join([f.capitalize() for f in strategy['factors']])
                            st.markdown(f"<p><strong>Factors:</strong> {factors_text}</p>", unsafe_allow_html=True)
                            st.markdown(f"</div>", unsafe_allow_html=True)
                else:
                    st.info("No strategies available for your risk profile. Please complete the assessment again.")
    
    # Footer
    st.markdown("<div class='footer'>Sharia Stock Pro © 2025| Powered by AI and Smart Beta Strategies</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()