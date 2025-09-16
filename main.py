# main.py

"""
Financial Planning LLM Framework - Main Orchestrator
This script orchestrates the entire data collection and RAG pipeline setup.
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, Any
import logging

# Import our modules
from scrapers.tax_scraper import TaxRuleScraper
from scrapers.investment_scraper import InvestmentDataCollector
from scrapers.market_data import MarketDataCollector, BudgetingRulesCollector
# from rag.ingestion import VectorDBIngestion

from config import PROCESSED_DATA_DIR, BASE_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDataOrchestrator:
    """
    Orchestrates the entire data collection and processing pipeline
    """
    
    def __init__(self):
        self.results = {}
        
    def collect_all_data(self) -> Dict[str, Any]:
        """
        Run all data collection scripts in sequence
        """
        logger.info("Starting comprehensive data collection...")
        start_time = time.time()
        
        # 1. Collect Tax Data
        logger.info("=== Phase 1: Collecting Tax Data ===")
        try:
            tax_scraper = TaxRuleScraper()
            tax_results = tax_scraper.collect_all_tax_data()
            self.results['tax_data'] = tax_results
            logger.info(f"Tax data collection completed: {tax_results}")
        except Exception as e:
            logger.error(f"Tax data collection failed: {e}")
            self.results['tax_data'] = {"error": str(e)}
        
        # 2. Collect Investment Data
        logger.info("=== Phase 2: Collecting Investment Data ===")
        try:
            investment_collector = InvestmentDataCollector()
            investment_results = investment_collector.collect_all_investment_data()
            self.results['investment_data'] = investment_results
            logger.info(f"Investment data collection completed: {investment_results}")
        except Exception as e:
            logger.error(f"Investment data collection failed: {e}")
            self.results['investment_data'] = {"error": str(e)}
        
        # 3. Collect Market Data
        logger.info("=== Phase 3: Collecting Market Data ===")
        try:
            market_collector = MarketDataCollector()
            market_results = market_collector.collect_market_data()
            self.results['market_data'] = market_results
            logger.info(f"Market data collection completed: {market_results}")
        except Exception as e:
            logger.error(f"Market data collection failed: {e}")
            self.results['market_data'] = {"error": str(e)}
        
        # 4. Collect Budgeting Rules
        logger.info("=== Phase 4: Collecting Budgeting Rules ===")
        try:
            budget_collector = BudgetingRulesCollector()
            budget_results = budget_collector.collect_budgeting_rules()
            self.results['budgeting_data'] = budget_results
            logger.info(f"Budgeting rules collection completed: {budget_results}")
        except Exception as e:
            logger.error(f"Budgeting rules collection failed: {e}")
            self.results['budgeting_data'] = {"error": str(e)}
        
        # 5. Set up Vector Database
        # logger.info("=== Phase 5: Setting up Vector Database ===")
        # try:
        #     vector_ingestion = VectorDBIngestion()
        #     rag_results = vector_ingestion.ingest_all_data()
        #     self.results['vector_db'] = rag_results
        #     logger.info(f"Vector DB setup completed: {rag_results}")
        # except Exception as e:
        #     logger.error(f"Vector DB setup failed: {e}")
        #     self.results['vector_db'] = {"error": str(e)}
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Summary
        self.results['summary'] = {
            'total_execution_time_seconds': round(total_time, 2),
            'total_execution_time_minutes': round(total_time / 60, 2),
            'phases_completed': len([k for k, v in self.results.items() if k != 'summary' and 'error' not in v]),
            'phases_with_errors': len([k for k, v in self.results.items() if k != 'summary' and 'error' in v]),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info(f"Data collection pipeline completed in {total_time:.2f} seconds")
        return self.results
    
    def save_pipeline_results(self) -> str:
        """
        Save the complete pipeline results
        """
        results_file = PROCESSED_DATA_DIR / "pipeline_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Pipeline results saved to {results_file}")
        return str(results_file)
    
    def generate_summary_report(self) -> str:
        """
        Generate a human-readable summary report
        """
        report_lines = [
            "=" * 60,
            "FINANCIAL PLANNING LLM FRAMEWORK - SETUP REPORT",
            "=" * 60,
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "PIPELINE EXECUTION SUMMARY:",
            f"- Total Time: {self.results.get('summary', {}).get('total_execution_time_minutes', 0):.1f} minutes",
            f"- Phases Completed: {self.results.get('summary', {}).get('phases_completed', 0)}/5",
            f"- Phases with Errors: {self.results.get('summary', {}).get('phases_with_errors', 0)}/5",
            "",
            "DETAILED RESULTS:",
        ]
        
        # Tax Data Results
        tax_data = self.results.get('tax_data', {})
        if 'error' not in tax_data:
            report_lines.extend([
                "",
                "✅ TAX DATA COLLECTION:",
                f"  - Total Entries: {tax_data.get('total_entries', 0)}",
                f"  - PDF Chunks: {tax_data.get('pdf_chunks', 0)}",
                f"  - Website Entries: {tax_data.get('website_entries', 0)}",
                f"  - Hardcoded Entries: {tax_data.get('hardcoded_entries', 0)}",
            ])
        else:
            report_lines.extend([
                "",
                "❌ TAX DATA COLLECTION: FAILED",
                f"  - Error: {tax_data.get('error', 'Unknown error')}"
            ])
        
        # Investment Data Results
        investment_data = self.results.get('investment_data', {})
        if 'error' not in investment_data:
            report_lines.extend([
                "",
                "✅ INVESTMENT DATA COLLECTION:",
                f"  - Total Options: {investment_data.get('total_options', 0)}",
                f"  - Categories: {', '.join(investment_data.get('categories', []))}",
                f"  - Risk Levels: {', '.join(investment_data.get('risk_levels', []))}",
            ])
        else:
            report_lines.extend([
                "",
                "❌ INVESTMENT DATA COLLECTION: FAILED",
                f"  - Error: {investment_data.get('error', 'Unknown error')}"
            ])
        
        # Market Data Results
        market_data = self.results.get('market_data', {})
        if 'error' not in market_data:
            report_lines.extend([
                "",
                "✅ MARKET DATA COLLECTION:",
                f"  - Tickers Collected: {market_data.get('total_tickers', 0)}",
                f"  - Tickers: {', '.join(market_data.get('tickers_collected', []))}",
                f"  - Date Range: {market_data.get('date_range', 'N/A')}",
            ])
        else:
            report_lines.extend([
                "",
                "❌ MARKET DATA COLLECTION: FAILED",
                f"  - Error: {market_data.get('error', 'Unknown error')}"
            ])
        
        # Budgeting Data Results
        budgeting_data = self.results.get('budgeting_data', {})
        if 'error' not in budgeting_data:
            report_lines.extend([
                "",
                "✅ BUDGETING RULES COLLECTION:",
                f"  - Total Rules: {budgeting_data.get('total_rules', 0)}",
                f"  - General Rules: {budgeting_data.get('general_rules', 0)}",
                f"  - Indian-Specific Rules: {budgeting_data.get('indian_rules', 0)}",
                f"  - Categories: {', '.join(budgeting_data.get('categories', []))}",
            ])
        else:
            report_lines.extend([
                "",
                "❌ BUDGETING RULES COLLECTION: FAILED",
                f"  - Error: {budgeting_data.get('error', 'Unknown error')}"
            ])
        
        # Vector DB Results
        vector_db = self.results.get('vector_db', {})
        if 'error' not in vector_db:
            db_stats = vector_db.get('database_stats', {})
            report_lines.extend([
                "",
                "✅ VECTOR DATABASE SETUP:",
                f"  - Tax Collection: {db_stats.get('tax_collection_count', 0)} documents",
                f"  - Investment Collection: {db_stats.get('investment_collection_count', 0)} documents",
                f"  - Budget Collection: {db_stats.get('budget_collection_count', 0)} documents",
                f"  - Total Documents: {sum(db_stats.values()) if db_stats else 0}",
            ])
        else:
            report_lines.extend([
                "",
                "❌ VECTOR DATABASE SETUP: FAILED",
                f"  - Error: {vector_db.get('error', 'Unknown error')}"
            ])
        
        # Next Steps
        report_lines.extend([
            "",
            "NEXT STEPS:",
            "1. Review any error messages above",
            "2. Test the RAG system with sample queries",
            "3. Build FastAPI endpoints in the /api/ directory", 
            "4. Implement user interface for financial planning",
            "5. Set up periodic data updates",
            "",
            "FILES CREATED:",
            f"- Tax Data: {PROCESSED_DATA_DIR}/tax_rules.json",
            f"- Investment Data: {PROCESSED_DATA_DIR}/investment_options.csv & .json",
            f"- Market Data: {PROCESSED_DATA_DIR}/market_data_combined.csv",
            f"- Budget Rules: {PROCESSED_DATA_DIR}/budgeting_rules.json",
            f"- Vector Database: {BASE_DIR}/chroma_db/",
            f"- Pipeline Results: {PROCESSED_DATA_DIR}/pipeline_results.json",
            "",
            "=" * 60,
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save report
        report_file = PROCESSED_DATA_DIR / "setup_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Setup report saved to {report_file}")
        return report_content


def run_quick_test():
    """
    Run a quick test of the RAG system
    """
    logger.info("Running quick RAG system test...")
    
    # try:
    #     from rag.ingestion import VectorDBIngestion
        
    #     ingestion = VectorDBIngestion()
        
    #     test_queries = [
    #         "tax slabs for individual",
    #         "best mutual funds for beginners", 
    #         "emergency fund planning"
    #     ]
        
    #     print("\n" + "="*50)
    #     print("QUICK RAG SYSTEM TEST")
    #     print("="*50)
        
    #     for query in test_queries:
    #         print(f"\nQuery: {query}")
    #         print("-" * 30)
            
    #         results = ingestion.search_all_collections(query, n_results=1)
            
    #         for collection_name, collection_results in results.items():
    #             if 'results' in collection_results and collection_results['results']['documents']:
    #                 doc = collection_results['results']['documents'][0][0]
    #                 meta = collection_results['results']['metadatas'][0][0]
                    
    #                 print(f"{collection_name.title()}: {doc[:150]}...")
    #                 print(f"Source: {meta.get('source', 'N/A')}")
    #             else:
    #                 print(f"{collection_name.title()}: No results found")
        
    #     print("\n" + "="*50)
    #     print("RAG system test completed successfully!")
        
    # except Exception as e:
    #     logger.error(f"RAG system test failed: {e}")


def main():
    """
    Main execution function
    """
    print("🚀 Starting Financial Planning LLM Framework Setup...")
    print("This may take several minutes depending on your internet connection.")
    print()
    
    # Run the full pipeline
    orchestrator = FinancialDataOrchestrator()
    results = orchestrator.collect_all_data()
    
    # Save results
    orchestrator.save_pipeline_results()
    
    # Generate and display report
    report = orchestrator.generate_summary_report()
    print("\n")
    print(report)
    
    # Run quick test
    if results.get('vector_db', {}).get('database_stats'):
        run_quick_test()
    
    print("\n✅ Setup completed! Check the files in /data/processed/ directory.")
    return results


if __name__ == "__main__":
    results = main()