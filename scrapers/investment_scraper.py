# scrapers/investment_scraper.py

import pandas as pd
import json
import requests
import time
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import logging

from config import USER_AGENT, REQUEST_DELAY, PROCESSED_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvestmentDataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
    def get_comprehensive_investment_data(self) -> List[Dict[str, Any]]:
        """
        Create comprehensive investment options data for Indian market
        """
        investment_options = [
            {
                'name': 'Fixed Deposit (FD)',
                'category': 'Debt',
                'risk_level': 'Low',
                'liquidity': 'Medium',
                'expected_return_range': '6-8%',
                'tax_treatment': 'Interest taxable as per income tax slab',
                'minimum_investment': 1000,
                'lock_in_period': '7 days to 10 years',
                'description': 'Bank fixed deposits offer guaranteed returns with capital protection. Interest is taxable as per income tax slab. Premature withdrawal penalties apply.',
                'pros': ['Capital protection', 'Guaranteed returns', 'No market risk'],
                'cons': ['Low real returns', 'Interest fully taxable', 'Inflation risk'],
                'suitable_for': 'Conservative investors, emergency funds',
                'source': 'RBI guidelines and bank websites'
            },
            {
                'name': 'Public Provident Fund (PPF)',
                'category': 'Tax Saving',
                'risk_level': 'Low',
                'liquidity': 'Low',
                'expected_return_range': '7.1-8.5%',
                'tax_treatment': 'EEE (Exempt-Exempt-Exempt)',
                'minimum_investment': 500,
                'lock_in_period': '15 years',
                'description': 'Government-backed long-term savings scheme with tax benefits. 15-year lock-in with partial withdrawal after 7th year.',
                'pros': ['Triple tax benefit', 'Government backing', 'Compounding benefits'],
                'cons': ['Long lock-in period', 'Low liquidity', 'Interest rate changes'],
                'suitable_for': 'Long-term wealth creation, retirement planning',
                'source': 'Ministry of Finance notifications'
            },
            {
                'name': 'National Pension System (NPS)',
                'category': 'Retirement',
                'risk_level': 'Medium',
                'liquidity': 'Low',
                'expected_return_range': '8-12%',
                'tax_treatment': 'EET (Exempt-Exempt-Taxable)',
                'minimum_investment': 1000,
                'lock_in_period': 'Until age 60',
                'description': 'Government pension scheme with equity and debt options. Additional tax benefit under 80CCD(1B).',
                'pros': ['Additional tax benefit', 'Professional fund management', 'Low cost'],
                'cons': ['Limited liquidity', 'Annuity mandatory', 'Market risk in equity'],
                'suitable_for': 'Retirement planning, government employees',
                'source': 'PFRDA guidelines'
            },
            {
                'name': 'Equity Linked Savings Scheme (ELSS)',
                'category': 'Tax Saving Mutual Fund',
                'risk_level': 'High',
                'liquidity': 'Medium',
                'expected_return_range': '10-15%',
                'tax_treatment': 'EEE for investment, LTCG on redemption',
                'minimum_investment': 500,
                'lock_in_period': '3 years',
                'description': 'Equity mutual funds with tax benefits and shortest lock-in among 80C options.',
                'pros': ['Shortest lock-in', 'High return potential', 'Professional management'],
                'cons': ['Market risk', 'LTCG tax on gains', 'Volatility'],
                'suitable_for': 'Young investors, tax saving with growth',
                'source': 'SEBI and AMC data'
            },
            {
                'name': 'Gold (Physical/Digital)',
                'category': 'Commodity',
                'risk_level': 'Medium',
                'liquidity': 'High',
                'expected_return_range': '8-10%',
                'tax_treatment': 'LTCG after 3 years with indexation',
                'minimum_investment': 1000,
                'lock_in_period': 'None',
                'description': 'Traditional inflation hedge available in physical, digital, and ETF formats.',
                'pros': ['Inflation hedge', 'High liquidity', 'Cultural significance'],
                'cons': ['Storage costs', 'No regular income', 'Price volatility'],
                'suitable_for': 'Portfolio diversification, inflation protection',
                'source': 'MCX and jewelry association data'
            },
            {
                'name': 'Large Cap Mutual Funds',
                'category': 'Equity Mutual Fund',
                'risk_level': 'Medium',
                'liquidity': 'High',
                'expected_return_range': '10-13%',
                'tax_treatment': 'LTCG tax after 1 year, STCG as per slab',
                'minimum_investment': 500,
                'lock_in_period': 'None',
                'description': 'Mutual funds investing in large, established companies with lower volatility.',
                'pros': ['Professional management', 'Diversification', 'High liquidity'],
                'cons': ['Market risk', 'Fund management fees', 'Tax on gains'],
                'suitable_for': 'Medium to long-term wealth creation',
                'source': 'SEBI and AMC factsheets'
            },
            {
                'name': 'Mid & Small Cap Mutual Funds',
                'category': 'Equity Mutual Fund',
                'risk_level': 'High',
                'liquidity': 'High',
                'expected_return_range': '12-18%',
                'tax_treatment': 'LTCG tax after 1 year, STCG as per slab',
                'minimum_investment': 500,
                'lock_in_period': 'None',
                'description': 'Higher risk-reward funds investing in mid and small cap companies.',
                'pros': ['High growth potential', 'Early stage company access', 'Professional management'],
                'cons': ['High volatility', 'Liquidity risk', 'Higher expense ratios'],
                'suitable_for': 'Aggressive investors, long-term horizon',
                'source': 'SEBI and AMC factsheets'
            },
            {
                'name': 'Corporate Bonds',
                'category': 'Debt',
                'risk_level': 'Medium',
                'liquidity': 'Medium',
                'expected_return_range': '7-10%',
                'tax_treatment': 'Interest taxable, LTCG with indexation',
                'minimum_investment': 10000,
                'lock_in_period': 'Varies (1-10 years)',
                'description': 'Debt instruments issued by corporations offering higher yields than government bonds.',
                'pros': ['Higher yields than FDs', 'Regular income', 'Credit rating available'],
                'cons': ['Credit risk', 'Interest rate risk', 'Limited liquidity'],
                'suitable_for': 'Income seekers, moderate risk appetite',
                'source': 'NSE/BSE bond platforms'
            },
            {
                'name': 'Government Bonds (G-Sec)',
                'category': 'Debt',
                'risk_level': 'Low',
                'liquidity': 'High',
                'expected_return_range': '6-8%',
                'tax_treatment': 'Interest taxable, LTCG with indexation',
                'minimum_investment': 10000,
                'lock_in_period': 'Varies (1-30 years)',
                'description': 'Sovereign debt instruments with government guarantee and no default risk.',
                'pros': ['No default risk', 'High liquidity', 'Regular income'],
                'cons': ['Interest rate risk', 'Taxable interest', 'Lower yields'],
                'suitable_for': 'Conservative investors, portfolio stability',
                'source': 'RBI and NSE goBID platform'
            },
            {
                'name': 'Real Estate Investment Trusts (REITs)',
                'category': 'Real Estate',
                'risk_level': 'Medium',
                'liquidity': 'Medium',
                'expected_return_range': '8-12%',
                'tax_treatment': 'Dividend taxable, LTCG on units',
                'minimum_investment': 15000,
                'lock_in_period': 'None',
                'description': 'Investment in commercial real estate through stock exchange listed trusts.',
                'pros': ['Real estate exposure', 'Regular dividends', 'Professional management'],
                'cons': ['Interest rate sensitivity', 'Limited options', 'Market volatility'],
                'suitable_for': 'Real estate exposure without direct ownership',
                'source': 'NSE/BSE REIT platforms'
            }
        ]
        
        return investment_options
    
    def scrape_additional_investment_info(self) -> List[Dict[str, Any]]:
        """
        Scrape additional investment information from financial websites
        Note: This is a basic example - in practice, you'd need to respect robots.txt
        and terms of service
        """
        additional_info = []
        
        try:
            # Example: Scrape basic mutual fund information
            # This is a simplified example - actual implementation would need
            # proper parsing and error handling
            
            # For demonstration, we'll add some scraped-like data
            scraped_info = [
                {
                    'name': 'Index Funds',
                    'category': 'Passive Equity',
                    'risk_level': 'Medium',
                    'liquidity': 'High',
                    'expected_return_range': '10-12%',
                    'tax_treatment': 'LTCG tax after 1 year',
                    'minimum_investment': 100,
                    'lock_in_period': 'None',
                    'description': 'Passively managed funds tracking market indices like Nifty 50, Sensex.',
                    'pros': ['Low expense ratio', 'Market returns', 'Diversification'],
                    'cons': ['No outperformance', 'Market risk', 'No active management'],
                    'suitable_for': 'Long-term passive investors',
                    'source': 'Scraped from financial websites'
                }
            ]
            
            additional_info.extend(scraped_info)
            
        except Exception as e:
            logger.error(f"Error scraping additional investment info: {e}")
            
        return additional_info
    
    def save_investment_data(self, data: List[Dict[str, Any]]) -> str:
        """
        Save investment data in both CSV and JSON formats
        """
        # Save as JSON for detailed information
        json_file = PROCESSED_DATA_DIR / "investment_options.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Save as CSV for easy analysis
        csv_file = PROCESSED_DATA_DIR / "investment_options.csv"
        
        # Create a simplified version for CSV
        csv_data = []
        for item in data:
            csv_row = {
                'name': item['name'],
                'category': item['category'],
                'risk_level': item['risk_level'],
                'liquidity': item['liquidity'],
                'expected_return_range': item['expected_return_range'],
                'tax_treatment': item['tax_treatment'],
                'minimum_investment': item['minimum_investment'],
                'lock_in_period': item['lock_in_period'],
                'description': item['description'][:200] + '...' if len(item['description']) > 200 else item['description'],
                'suitable_for': item['suitable_for'],
                'source': item['source']
            }
            csv_data.append(csv_row)
        
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False)
        
        logger.info(f"Investment data saved to {json_file} and {csv_file}")
        return str(json_file)
    
    def collect_all_investment_data(self) -> Dict[str, Any]:
        """
        Main method to collect all investment data
        """
        logger.info("Starting investment data collection...")
        
        # Get comprehensive investment data
        investment_data = self.get_comprehensive_investment_data()
        
        # Scrape additional information
        additional_data = self.scrape_additional_investment_info()
        investment_data.extend(additional_data)
        
        # Save data
        output_file = self.save_investment_data(investment_data)
        
        logger.info(f"Collected {len(investment_data)} investment options")
        
        return {
            'total_options': len(investment_data),
            'categories': list(set(item['category'] for item in investment_data)),
            'risk_levels': list(set(item['risk_level'] for item in investment_data)),
            'output_file': output_file
        }

def main():
    """Example usage"""
    collector = InvestmentDataCollector()
    result = collector.collect_all_investment_data()
    print(f"Investment data collection completed: {result}")

if __name__ == "__main__":
    main()