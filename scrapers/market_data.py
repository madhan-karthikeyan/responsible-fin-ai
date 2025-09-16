# scrapers/market_data.py

import yfinance as yf
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from config import INDIAN_TICKERS, PROCESSED_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataCollector:
    def __init__(self):
        self.tickers = INDIAN_TICKERS
        
    def fetch_historical_data(self, period: str = "2y") -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for Indian stocks using yfinance
        """
        stock_data = {}
        
        for ticker in self.tickers:
            try:
                logger.info(f"Fetching data for {ticker}")
                
                # Fetch stock data
                stock = yf.Ticker(ticker)
                hist_data = stock.history(period=period)
                
                if not hist_data.empty:
                    stock_data[ticker] = hist_data
                    logger.info(f"Fetched {len(hist_data)} records for {ticker}")
                else:
                    logger.warning(f"No data found for {ticker}")
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error fetching data for {ticker}: {e}")
                
        return stock_data
    
    def get_stock_info(self) -> List[Dict[str, Any]]:
        """
        Get basic information about Indian stocks
        """
        stock_info = []
        
        for ticker in self.tickers:
            try:
                logger.info(f"Fetching info for {ticker}")
                
                stock = yf.Ticker(ticker)
                info = stock.info
                
                stock_info.append({
                    'ticker': ticker,
                    'company_name': info.get('longName', 'N/A'),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'market_cap': info.get('marketCap', 0),
                    'currency': info.get('currency', 'INR'),
                    'exchange': info.get('exchange', 'NSI'),
                    'description': info.get('longBusinessSummary', 'N/A')[:500],
                    'website': info.get('website', 'N/A'),
                    'employees': info.get('fullTimeEmployees', 'N/A'),
                    'fetched_date': datetime.now().strftime('%Y-%m-%d')
                })
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching info for {ticker}: {e}")
                
        return stock_info
    
    def save_market_data(self, stock_data: Dict[str, pd.DataFrame], stock_info: List[Dict[str, Any]]) -> str:
        """
        Save market data to CSV files
        """
        # Save historical data
        for ticker, data in stock_data.items():
            csv_file = PROCESSED_DATA_DIR / f"market_data_{ticker.replace('.', '_')}.csv"
            data.to_csv(csv_file)
            logger.info(f"Saved {ticker} data to {csv_file}")
        
        # Save combined data
        combined_file = PROCESSED_DATA_DIR / "market_data_combined.csv"
        all_data = []
        
        for ticker, data in stock_data.items():
            data_copy = data.copy()
            data_copy['ticker'] = ticker
            data_copy['date'] = data_copy.index
            all_data.append(data_copy)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df.to_csv(combined_file, index=False)
            logger.info(f"Saved combined market data to {combined_file}")
        
        # Save stock info
        info_file = PROCESSED_DATA_DIR / "stock_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(stock_info, f, indent=2, ensure_ascii=False)
        
        return str(combined_file)
    
    def collect_market_data(self) -> Dict[str, Any]:
        """
        Main method to collect market data
        """
        logger.info("Starting market data collection...")
        
        # Fetch historical data
        stock_data = self.fetch_historical_data()
        
        # Fetch stock information
        stock_info = self.get_stock_info()
        
        # Save data
        output_file = self.save_market_data(stock_data, stock_info)
        
        return {
            'tickers_collected': list(stock_data.keys()),
            'total_tickers': len(stock_data),
            'date_range': f"{stock_data[list(stock_data.keys())[0]].index[0]} to {stock_data[list(stock_data.keys())[0]].index[-1]}" if stock_data else "N/A",
            'output_file': output_file
        }


class BudgetingRulesCollector:
    """
    Collect and organize budgeting heuristics and financial planning rules
    """
    
    def get_budgeting_rules(self) -> List[Dict[str, Any]]:
        """
        Compile comprehensive budgeting rules and financial heuristics
        """
        budgeting_rules = [
            {
                'rule_name': '50/30/20 Rule',
                'category': 'Basic Budgeting',
                'description': 'Allocate 50% of after-tax income to needs, 30% to wants, and 20% to savings and debt repayment.',
                'detailed_explanation': 'Needs include rent, groceries, utilities, minimum loan payments. Wants include entertainment, dining out, shopping. Savings include emergency fund, retirement, investments.',
                'applicability': 'General population, middle-income earners',
                'pros': ['Simple to follow', 'Balanced approach', 'Forces saving habit'],
                'cons': ['May not suit high-income earners', 'Rigid categories', 'Doesnt account for irregular income'],
                'source': 'Elizabeth Warren - All Your Worth',
                'popularity_score': 9
            },
            {
                'rule_name': '60% Solution',
                'category': 'Advanced Budgeting',
                'description': 'Put 60% of gross income toward committed expenses, divide remaining 40% into four 10% buckets.',
                'detailed_explanation': '60% for taxes, fixed expenses, essentials. 10% each for retirement, long-term savings, short-term savings, and fun money.',
                'applicability': 'High-income earners, detailed planners',
                'pros': ['Comprehensive coverage', 'Forces retirement saving', 'Flexible fun money'],
                'cons': ['Complex to implement', 'High committed expense ratio', 'Requires discipline'],
                'source': 'Richard Jenkins - MSN Money',
                'popularity_score': 6
            },
            {
                'rule_name': 'Emergency Fund Rule',
                'category': 'Emergency Planning',
                'description': 'Maintain 3-6 months of living expenses in liquid savings.',
                'detailed_explanation': 'Emergency fund should cover 3 months expenses for dual-income households, 6 months for single-income. Keep in high-yield savings account or liquid fund.',
                'applicability': 'All income levels and life stages',
                'pros': ['Financial security', 'Reduces debt dependency', 'Peace of mind'],
                'cons': ['Opportunity cost', 'Inflation erosion', 'Requires discipline'],
                'source': 'Financial Planning Association',
                'popularity_score': 10
            },
            {
                'rule_name': 'Age in Bonds Rule',
                'category': 'Asset Allocation',
                'description': 'Percentage of portfolio in bonds should equal your age.',
                'detailed_explanation': 'A 30-year-old should have 30% bonds, 70% stocks. Adjusts risk as you age. Modern variants suggest age minus 10 or 20.',
                'applicability': 'Retirement planning, conservative investors',
                'pros': ['Automatic risk adjustment', 'Simple to implement', 'Time-tested'],
                'cons': ['Too conservative for some', 'Ignores individual circumstances', 'Low returns in current environment'],
                'source': 'Traditional investment wisdom',
                'popularity_score': 7
            },
            {
                'rule_name': 'House Affordability Rule',
                'category': 'Real Estate',
                'description': 'House price should not exceed 3-5 times annual gross income.',
                'detailed_explanation': 'Traditional rule is 3x income. Modern versions allow up to 5x for high-income earners. Consider EMI not exceeding 40% of take-home income.',
                'applicability': 'Home buyers, real estate investors',
                'pros': ['Prevents overextension', 'Simple calculation', 'Risk management'],
                'cons': ['Varies by location', 'Ignores other debts', 'May limit in expensive cities'],
                'source': 'Banking industry standards',
                'popularity_score': 8
            },
            {
                'rule_name': 'India-Specific: PPF Maximum',
                'category': 'Tax Planning',
                'description': 'Maximize PPF contribution of ₹1.5 lakh annually for tax benefits and long-term wealth.',
                'detailed_explanation': 'PPF offers EEE tax benefit, 15-year lock-in, current rate ~7.1%. Start early to benefit from compounding.',
                'applicability': 'Indian taxpayers, long-term planners',
                'pros': ['Triple tax benefit', 'Government backing', 'Forced long-term saving'],
                'cons': ['Long lock-in', 'Interest rate risk', 'Liquidity constraints'],
                'source': 'Indian tax planning best practices',
                'popularity_score': 9
            },
            {
                'rule_name': 'Credit Card Payment Rule',
                'category': 'Debt Management',
                'description': 'Always pay credit card bills in full, on time. If you cannot, pay minimum and prioritize paying off.',
                'detailed_explanation': 'Credit card interest rates in India range 36-48% annually. Never carry a balance if possible. Use only for convenience and rewards.',
                'applicability': 'All credit card users',
                'pros': ['Avoids high interest', 'Builds credit score', 'Maximizes rewards'],
                'cons': ['Requires cash flow management', 'Temptation to overspend'],
                'source': 'Credit counseling organizations',
                'popularity_score': 10
            },
            {
                'rule_name': 'SIP Consistency Rule',
                'category': 'Investment',
                'description': 'Start SIP early, increase by 10-15% annually, never stop during market downturns.',
                'detailed_explanation': 'Systematic Investment Plans benefit from rupee cost averaging. Increase SIP with salary hikes. Continue during bear markets for better long-term returns.',
                'applicability': 'Mutual fund investors, regular income earners',
                'pros': ['Disciplined investing', 'Rupee cost averaging', 'Wealth creation'],
                'cons': ['Requires regular income', 'May miss lump sum opportunities', 'Emotional discipline needed'],
                'source': 'Indian mutual fund industry',
                'popularity_score': 9
            },
            {
                'rule_name': 'Health Insurance Rule',
                'category': 'Insurance Planning',
                'description': 'Health insurance should cover 10-15 times annual income, including family floater and critical illness.',
                'detailed_explanation': 'Rising healthcare costs require adequate coverage. Combine employer insurance with top-up and personal policies. Include parents if needed.',
                'applicability': 'All income levels, especially families',
                'pros': ['Financial protection', 'Tax benefits', 'Peace of mind'],
                'cons': ['Premium cost', 'Claim hassles', 'Waiting periods'],
                'source': 'Insurance industry guidelines',
                'popularity_score': 8
            },
            {
                'rule_name': 'Retirement Corpus Rule',
                'category': 'Retirement Planning',
                'description': 'Target retirement corpus should be 25-30 times annual expenses at retirement.',
                'detailed_explanation': 'Use 4% withdrawal rate assumption. If you need ₹10 lakh annually, target ₹2.5-3 crore corpus. Account for inflation and healthcare costs.',
                'applicability': 'Long-term planners, retirement preparation',
                'pros': ['Clear target', 'Sustainable withdrawals', 'Financial independence'],
                'cons': ['Large corpus needed', 'Market risk', 'Inflation assumptions'],
                'source': 'Retirement planning research',
                'popularity_score': 7
            }
        ]
        
        return budgeting_rules
    
    def get_indian_specific_rules(self) -> List[Dict[str, Any]]:
        """
        Additional India-specific financial rules and heuristics
        """
        indian_rules = [
            {
                'rule_name': 'Section 80C Optimization',
                'category': 'Tax Planning',
                'description': 'Prioritize ELSS > PPF > EPF > Insurance > NSC for 80C deductions based on liquidity and returns.',
                'detailed_explanation': 'ELSS has shortest lock-in (3 years) and highest return potential. PPF for long-term. EPF if employer matching available.',
                'applicability': 'Indian taxpayers',
                'pros': ['Tax savings', 'Wealth creation', 'Forced saving'],
                'cons': ['Lock-in periods', 'Market risk in ELSS'],
                'source': 'Indian tax planning experts',
                'popularity_score': 8
            },
            {
                'rule_name': 'Gold Allocation Rule',
                'category': 'Asset Allocation',
                'description': 'Limit gold allocation to 5-10% of portfolio through Gold ETFs or Digital Gold.',
                'detailed_explanation': 'Gold hedge against inflation and currency devaluation. Prefer digital formats over physical for convenience and cost.',
                'applicability': 'Indian investors, portfolio diversification',
                'pros': ['Inflation hedge', 'Cultural comfort', 'Diversification'],
                'cons': ['No regular returns', 'Storage issues', 'Price volatility'],
                'source': 'Indian investment advisors',
                'popularity_score': 7
            },
            {
                'rule_name': 'Festival Spending Rule',
                'category': 'Cultural Budgeting',
                'description': 'Budget 2-3% of annual income for festivals and celebrations, save in advance.',
                'detailed_explanation': 'Indian festivals involve significant expenses. Plan and save monthly rather than using credit or depleting emergency fund.',
                'applicability': 'Indian families and individuals',
                'pros': ['Planned expenses', 'Debt avoidance', 'Cultural enjoyment'],
                'cons': ['Requires advance planning', 'May seem restrictive'],
                'source': 'Indian financial planners',
                'popularity_score': 6
            }
        ]
        
        return indian_rules
    
    def collect_budgeting_rules(self) -> Dict[str, Any]:
        """
        Main method to collect all budgeting rules
        """
        logger.info("Collecting budgeting rules...")
        
        # Get all rules
        general_rules = self.get_budgeting_rules()
        indian_rules = self.get_indian_specific_rules()
        
        all_rules = general_rules + indian_rules
        
        # Save to JSON
        output_file = PROCESSED_DATA_DIR / "budgeting_rules.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_rules, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Collected {len(all_rules)} budgeting rules")
        
        return {
            'total_rules': len(all_rules),
            'categories': list(set(rule['category'] for rule in all_rules)),
            'general_rules': len(general_rules),
            'indian_rules': len(indian_rules),
            'output_file': str(output_file)
        }


def main():
    """Example usage for both market data and budgeting rules"""
    
    # Collect market data
    market_collector = MarketDataCollector()
    market_result = market_collector.collect_market_data()
    print(f"Market data collection completed: {market_result}")
    
    # Collect budgeting rules
    budget_collector = BudgetingRulesCollector()
    budget_result = budget_collector.collect_budgeting_rules()
    print(f"Budgeting rules collection completed: {budget_result}")

if __name__ == "__main__":
    main()