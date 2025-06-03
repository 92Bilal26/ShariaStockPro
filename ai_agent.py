import os
from dotenv import load_dotenv
from typing import Dict, Any, List
import google.generativeai as genai
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash')

def get_stock_recommendations(
    risk_profile: str,
    kmi30_data: pd.DataFrame,
    user_answers: Dict[str, int]
) -> str:
    """
    Get AI-powered stock recommendations based on user's risk profile and KMI-30 data
    """
    try:
        # Filter stocks based on risk profile
        if risk_profile == "conservative":
            filtered_stocks = kmi30_data[kmi30_data['Summary'].isin(['STRONG_BUY', 'BUY'])]
        elif risk_profile == "moderate":
            filtered_stocks = kmi30_data[kmi30_data['Summary'].isin(['STRONG_BUY', 'BUY', 'NEUTRAL'])]
        else:  # aggressive
            filtered_stocks = kmi30_data[kmi30_data['Summary'].isin(['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL'])]

        # Sort stocks by technical indicators
        filtered_stocks = filtered_stocks.sort_values(by=['RSI', 'MACD'], ascending=[False, False])

        # Prepare stock data for analysis
        stock_data = filtered_stocks.head(5).to_dict('records')
        
        # Create a detailed prompt for the AI
        prompt = f"""As an Islamic finance expert and AI-driven fund manager, analyze these KMI-30 stocks for a {risk_profile} investor:

User Profile:
- Investment Goal: {get_investment_goal(user_answers)}
- Time Horizon: {get_time_horizon(user_answers)}
- Risk Tolerance: {get_risk_tolerance(user_answers)}
- Investment Experience: {get_experience(user_answers)}
- Investment Capacity: {get_capacity(user_answers)}

Top 5 Stocks Based on Technical Analysis:
{format_stock_data(stock_data)}

Please provide recommendations in both English and Urdu, following these principles:

1. Shariah Compliance:
   - Business Screening: Ensure companies are not involved in prohibited industries
   - Financial Ratio Screening: Debt/Total Assets < 33%, Cash+Interest-Bearing Securities/Total Assets < 33%
   - Non-permissible Income < 5%

2. Smart Beta Strategy Application:
   - Value: Low P/E or P/B ratios
   - Momentum: Strong recent price trends
   - Quality: High profitability (ROE, margin) and low debt
   - Low Volatility: Low beta or price swings
   - Size: Consider market capitalization

3. Portfolio Construction:
   - Diversification across sectors
   - Limit concentration in any single stock
   - Consider market fundamentals (Market Cap, P/E, Dividend Yield, ROE, Beta, Volume)
   - Factor-based weighting (Value: 30%, Quality: 30%, Momentum: 20%, Low Volatility: 20%)

4. Rebalancing Strategy:
   - Quarterly rebalancing
   - Trigger rebalancing if:
     * Asset weight drifts >10% from target
     * Stock becomes non-compliant
     * Factor scores change significantly
   - Consider transaction costs

Format your response as:
1. Overall Market Analysis
2. Shariah Compliance Check
3. Top 3 Stock Recommendations with:
   - Factor Analysis
   - Technical Indicators
   - Risk Assessment
   - Suggested Portfolio Weight
4. Diversification Strategy
5. Rebalancing Recommendations
6. Risk Management Advice

Focus on stocks that match the user's risk profile while maintaining Shariah compliance and optimal diversification."""

        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2000,
                top_p=0.8,
                top_k=40
            )
        )
        
        return response.text
        
    except Exception as e:
        return f"Error getting AI recommendations: {str(e)}"

def format_stock_data(stocks: List[Dict[str, Any]]) -> str:
    """Format stock data for the AI prompt"""
    formatted = []
    for stock in stocks:
        formatted.append(f"""
Stock: {stock['Ticker']}
Price: {stock['Current Price']}
Summary: {stock['Summary']}
RSI: {stock['RSI']}
MACD: {stock['MACD']} (Signal: {stock['MACD Signal']})
ADX: {stock['ADX']}
Volume: {stock['Volume']}
---""")
    return "\n".join(formatted)

def get_investment_goal(answers: Dict[str, int]) -> str:
    """Get investment goal from user answers"""
    goal_points = answers.get(1, 0)
    if goal_points <= 1:
        return "Capital Preservation"
    elif goal_points == 2:
        return "Regular Income"
    elif goal_points == 3:
        return "Long-term Growth"
    else:
        return "Aggressive Growth"

def get_time_horizon(answers: Dict[str, int]) -> str:
    """Get investment time horizon from user answers"""
    horizon_points = answers.get(2, 0)
    if horizon_points <= 1:
        return "Short-term (Less than 2 years)"
    elif horizon_points == 2:
        return "Medium-term (2-5 years)"
    elif horizon_points == 3:
        return "Long-term (5-10 years)"
    else:
        return "Very Long-term (More than 10 years)"

def get_risk_tolerance(answers: Dict[str, int]) -> str:
    """Get risk tolerance from user answers"""
    risk_points = answers.get(3, 0)
    if risk_points <= 1:
        return "Very Conservative"
    elif risk_points == 2:
        return "Conservative"
    elif risk_points == 3:
        return "Moderate"
    else:
        return "Aggressive"

def get_experience(answers: Dict[str, int]) -> str:
    """Get investment experience from user answers"""
    exp_points = answers.get(4, 0)
    if exp_points <= 1:
        return "Beginner"
    elif exp_points == 2:
        return "Intermediate"
    elif exp_points == 3:
        return "Advanced"
    else:
        return "Expert"

def get_capacity(answers: Dict[str, int]) -> str:
    """Get investment capacity from user answers"""
    capacity_points = answers.get(5, 0)
    if capacity_points <= 1:
        return "Low (Less than 10% of income)"
    elif capacity_points == 2:
        return "Medium (10-20% of income)"
    elif capacity_points == 3:
        return "High (20-30% of income)"
    else:
        return "Very High (More than 30% of income)" 
