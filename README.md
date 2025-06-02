# Investment Risk Assessment & Smart Beta Recommendations

This Streamlit application helps users assess their investment risk profile and receive personalized stock recommendations based on smart beta strategies.

## Features

- Interactive risk assessment questionnaire with 5 questions
- Progress tracking and navigation between questions
- Risk profile calculation (Conservative, Moderate, or Aggressive)
- Smart beta stock recommendations based on risk profile
- Detailed stock analysis with reasons for recommendations

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To run the application, use the following command:
```bash
streamlit run app.py
```

The application will open in your default web browser.

## How to Use

1. Answer the risk assessment questions by selecting one option for each question
2. Use the "Previous" and "Next" buttons to navigate between questions
3. Click "Complete" after answering all questions
4. View your risk profile and personalized stock recommendations
5. Click "Start Over" to begin a new assessment

## Smart Beta Strategies

The application uses the following smart beta strategies:
- Quality: High-quality companies with strong fundamentals
- Value: Undervalued companies trading below intrinsic value
- Momentum: Companies with strong price momentum
- Growth: Companies with high growth potential
- Low Volatility: Stable companies with lower price volatility
- Quality Value: High-quality companies at attractive valuations
- Quality Momentum: High-quality companies with positive momentum

## Note

This application uses mock stock data for demonstration purposes. In a production environment, it should be connected to real market data sources. 