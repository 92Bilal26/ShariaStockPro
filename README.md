# Sharia Stock Pro

![Sharia Stock Pro](https://img.icons8.com/color/96/000000/mosque.png)

Sharia Stock Pro is a modern web application that helps investors find Shariah-compliant investments that match their risk profile using smart beta strategies and AI recommendations.

## Features

- **Risk Profile Assessment**: Answer a series of questions to determine your investment risk profile (conservative, moderate, or aggressive)
- **KMI-30 Technical Analysis**: Real-time technical analysis of KMI-30 (Karachi Meezan Index 30) stocks
- **AI-Powered Recommendations**: Get personalized investment recommendations based on your risk profile
- **Smart Beta Strategies**: Access to various smart beta investment strategies tailored to your risk profile
- **Modern UI**: Clean, responsive interface with intuitive navigation

## Technologies Used

- **Streamlit**: For the web application framework
- **Pandas & NumPy**: For data manipulation and analysis
- **TradingView TA**: For technical analysis of stocks
- **Google Gemini AI**: For generating personalized investment recommendations
- **BeautifulSoup**: For web scraping stock data

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sharia_stock_pro.git
   cd sharia_stock_pro
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   Create a `.env` file in the root directory with your Google Gemini API key:
   ```
   GEMINI_API_KEY="your_api_key_here"
   ```

## Running the Application

### Local Development

Run the application locally with:

```bash
streamlit run app.py
```

The application will be available at http://localhost:8501

### Deployment on Railway

This application is configured for deployment on Railway. The `railway.toml` file contains the necessary configuration:

```toml
[build]
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"
healthcheckPath = "/"
healthcheckTimeout = 100
restartPolicyType = "on_failure"

[env]
PYTHON_VERSION = "3.12.0"
PORT = "8080"
```

To deploy to Railway:

1. Push your code to a GitHub repository
2. Connect your repository to Railway
3. Add your `GEMINI_API_KEY` as an environment variable in Railway
4. Deploy the application

## Project Structure

- `app.py`: Main application file with the Streamlit UI
- `ai_agent.py`: Contains the AI recommendation engine using Google Gemini
- `kmi30_data.py`: Functions for fetching and analyzing KMI-30 stocks
- `style.css`: Custom styling for the application
- `requirements.txt`: List of required Python packages
- `railway.toml`: Configuration for Railway deployment

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.