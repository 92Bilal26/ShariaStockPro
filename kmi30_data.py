import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tradingview_ta import TA_Handler, Interval

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
            print(f"Failed to fetch webpage. Status code: {response.status_code}")
            return []

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Webpage fetched and parsed successfully.")

        # Find all tables on the page
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on the page.")

        if not tables:
            print("No tables found on the webpage.")
            return []

        # Look for a table that likely contains stock symbols
        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue

            # Check header row for a clue (e.g., "Symbol", "Ticker", "Code")
            header = rows[0]
            header_cells = header.find_all('th')
            symbol_index = None

            # Possible header names for the symbol column
            symbol_keywords = ['symbol', 'ticker', 'code', 'company']
            for i, cell in enumerate(header_cells):
                cell_text = cell.text.strip().lower()
                if any(keyword in cell_text for keyword in symbol_keywords):
                    symbol_index = i
                    print(f"Found potential symbol column at index {symbol_index} with header: '{cell_text}'")
                    break

            # If no clear header, try to infer from data rows
            if symbol_index is None and len(rows) > 1:
                first_data_row = rows[1]
                cells = first_data_row.find_all('td')
                for i, cell in enumerate(cells):
                    # Look for a cell with a stock symbol pattern (e.g., uppercase letters, 2-5 chars)
                    if re.match(r'^[A-Z]{2,5}$', cell.text.strip()):
                        symbol_index = i
                        print(f"Inferred symbol column at index {symbol_index} based on data pattern.")
                        break

            # Extract symbols if we found a symbol column
            if symbol_index is not None:
                tickers = []
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) > symbol_index:
                        symbol = cells[symbol_index].text.strip()
                        # Validate symbol (basic check for uppercase letters)
                        if re.match(r'^[A-Z]{2,5}$', symbol):
                            tickers.append(symbol)  # Store base symbol without suffix
                if tickers:
                    print(f"Extracted {len(tickers)} tickers: {tickers[:5]}...")  # Show first 5 for brevity
                    return tickers

        print("No table with identifiable stock symbols found. Website structure might have changed.")
        return []

    except Exception as e:
        print(f"An error occurred while fetching tickers: {e}")
        return []

def get_technical_analysis(tickers):
    """
    Get comprehensive technical analysis for a list of tickers
    Args: tickers - List of ticker symbols
    Returns: DataFrame with technical analysis data
    """
    results = []
    
    print(f"\nFetching technical analysis for {len(tickers)} tickers...")
    
    for symbol in tickers:
        try:
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
            print(f"✓ {symbol} - Price: {result['Current Price']}, Recommendation: {result['Summary']}")
            
        except Exception as e:
            print(f"✗ Error fetching {symbol}: {e}")
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
    
    return pd.DataFrame(results)

def get_kmi30_analysis():
    """
    Main function to execute the complete workflow
    Returns: DataFrame with analysis results
    """
    print("=== KMI-30 Automated Analysis Tool ===\n")
    
    # Step 1: Get KMI-30 tickers from PSX website
    print("Step 1: Fetching KMI-30 tickers from PSX website...")
    tickers = get_kmi30_tickers()
    
    if not tickers:
        print("No tickers found. Using fallback list...")
        # Fallback to a known list if scraping fails
        tickers = ['ATRL', 'DGKC', 'EFERT', 'EPCL', 'FABL', 'HBL', 'MCB', 'UBL', 'LUCK', 'ENGRO']
        print(f"Using fallback tickers: {tickers}")
    
    print(f"Total tickers found: {len(tickers)}")
    
    # Step 2: Get technical analysis for all tickers
    print("\nStep 2: Fetching technical analysis data...")
    df = get_technical_analysis(tickers)
    
    return df 