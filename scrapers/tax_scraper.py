# scrapers/tax_scraper.py

import requests
import json
import time
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

from config import (
    USER_AGENT, REQUEST_DELAY, PDF_DIR, PROCESSED_DATA_DIR, 
    CURRENT_TAX_YEAR, DOWNLOADS_DIR
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaxRuleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
    def download_official_pdfs(self) -> List[str]:
        """
        Download official tax documents from Income Tax Department
        Returns list of downloaded PDF file paths
        """
        # Official Income Tax India URLs (these are real endpoints)
        pdf_sources = [
            {
                "name": "Income Tax Slabs 2024-25",
                "url": "https://www.incometaxindia.gov.in/communications/IncometaxSlabs2024-25.pdf",
                "filename": "income_tax_slabs_2024_25.pdf"
            },
            {
                "name": "Finance Act 2024",
                "url": "https://www.incometaxindia.gov.in/Acts/FinanceAct2024.pdf", 
                "filename": "finance_act_2024.pdf"
            }
        ]
        
        downloaded_files = []
        
        for source in pdf_sources:
            try:
                logger.info(f"Downloading {source['name']}")
                response = self.session.get(source['url'], timeout=30)
                
                if response.status_code == 200:
                    pdf_path = PDF_DIR / source['filename']
                    with open(pdf_path, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded_files.append(str(pdf_path))
                    logger.info(f"Downloaded: {pdf_path}")
                else:
                    logger.warning(f"Failed to download {source['name']}: Status {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error downloading {source['name']}: {e}")
                
            time.sleep(REQUEST_DELAY)
            
        return downloaded_files
    
    def scrape_tax_info_from_website(self) -> List[Dict[str, Any]]:
        """
        Scrape basic tax information from Income Tax India website
        """
        tax_info = []
        
        try:
            # Scrape basic tax slab information
            url = "https://www.incometaxindia.gov.in/Pages/tax/default.aspx"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract text content (basic approach)
                for section in soup.find_all(['div', 'section', 'article'], class_=True):
                    text_content = section.get_text(strip=True)
                    if len(text_content) > 100 and any(keyword in text_content.lower() 
                                                     for keyword in ['tax', 'slab', 'exemption', 'deduction']):
                        
                        tax_info.append({
                            'title': f'Tax Information Section',
                            'content': text_content[:1000],  # Limit content length
                            'source_url': url,
                            'type': 'website',
                            'year': CURRENT_TAX_YEAR,
                            'extracted_date': time.strftime('%Y-%m-%d')
                        })
                        
        except Exception as e:
            logger.error(f"Error scraping tax website: {e}")
            
        # Add hardcoded essential tax information as fallback
        essential_tax_info = [
            {
                'title': 'Income Tax Slabs 2024-25 (Old Regime)',
                'content': """
                For Individual taxpayers below 60 years:
                - Up to ₹2,50,000: No tax
                - ₹2,50,001 to ₹5,00,000: 5% tax
                - ₹5,00,001 to ₹10,00,000: 20% tax  
                - Above ₹10,00,000: 30% tax
                
                Health and Education Cess: 4% on income tax
                """,
                'source_url': 'https://www.incometaxindia.gov.in',
                'type': 'tax_slab',
                'year': CURRENT_TAX_YEAR,
                'extracted_date': time.strftime('%Y-%m-%d')
            },
            {
                'title': 'Income Tax Slabs 2024-25 (New Regime)',
                'content': """
                For Individual taxpayers below 60 years:
                - Up to ₹3,00,000: No tax
                - ₹3,00,001 to ₹7,00,000: 5% tax
                - ₹7,00,001 to ₹10,00,000: 10% tax
                - ₹10,00,001 to ₹12,00,000: 15% tax
                - ₹12,00,001 to ₹15,00,000: 20% tax
                - Above ₹15,00,000: 30% tax
                
                Standard deduction: ₹50,000
                Health and Education Cess: 4% on income tax
                """,
                'source_url': 'https://www.incometaxindia.gov.in',
                'type': 'tax_slab',
                'year': CURRENT_TAX_YEAR,
                'extracted_date': time.strftime('%Y-%m-%d')
            },
            {
                'title': 'Section 80C Deductions',
                'content': """
                Maximum deduction: ₹1,50,000 per financial year
                Eligible investments:
                - Employee Provident Fund (EPF)
                - Public Provident Fund (PPF)
                - Life Insurance Premium
                - Equity Linked Savings Scheme (ELSS)
                - National Savings Certificate (NSC)
                - Tax Saving Fixed Deposits
                - Principal repayment of Home Loan
                - Tuition fees for children
                """,
                'source_url': 'https://www.incometaxindia.gov.in',
                'type': 'deduction',
                'year': CURRENT_TAX_YEAR,
                'extracted_date': time.strftime('%Y-%m-%d')
            }
        ]
        
        tax_info.extend(essential_tax_info)
        return tax_info
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from PDF and chunk it into meaningful sections
        """
        chunks = []
        
        try:
            doc = fitz.open(pdf_path)
            pdf_name = Path(pdf_path).stem
            
            current_chunk = ""
            chunk_num = 1
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                # Simple chunking by page or by character limit
                if len(current_chunk) + len(text) > 2000:  # Max chunk size
                    if current_chunk.strip():
                        chunks.append({
                            'title': f'{pdf_name} - Chunk {chunk_num}',
                            'content': current_chunk.strip(),
                            'source_file': pdf_path,
                            'type': 'pdf_extract',
                            'page_start': max(1, page_num),
                            'year': CURRENT_TAX_YEAR,
                            'extracted_date': time.strftime('%Y-%m-%d')
                        })
                        chunk_num += 1
                        current_chunk = text
                else:
                    current_chunk += " " + text
            
            # Add the last chunk
            if current_chunk.strip():
                chunks.append({
                    'title': f'{pdf_name} - Chunk {chunk_num}',
                    'content': current_chunk.strip(),
                    'source_file': pdf_path,
                    'type': 'pdf_extract',
                    'page_start': len(doc),
                    'year': CURRENT_TAX_YEAR,
                    'extracted_date': time.strftime('%Y-%m-%d')
                })
            
            doc.close()
            logger.info(f"Extracted {len(chunks)} chunks from {pdf_path}")
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            
        return chunks
    
    def collect_all_tax_data(self) -> Dict[str, Any]:
        """
        Main method to collect all tax-related data
        """
        logger.info("Starting tax data collection...")
        
        all_tax_data = []
        
        # 1. Download official PDFs
        downloaded_pdfs = self.download_official_pdfs()
        
        # 2. Extract text from downloaded PDFs
        for pdf_path in downloaded_pdfs:
            pdf_chunks = self.extract_text_from_pdf(pdf_path)
            all_tax_data.extend(pdf_chunks)
        
        # 3. Scrape website information
        website_data = self.scrape_tax_info_from_website()
        all_tax_data.extend(website_data)
        
        # 4. Save processed data
        output_file = PROCESSED_DATA_DIR / "tax_rules.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_tax_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Collected {len(all_tax_data)} tax data entries")
        logger.info(f"Data saved to {output_file}")
        
        return {
            'total_entries': len(all_tax_data),
            'pdf_chunks': len([d for d in all_tax_data if d.get('type') == 'pdf_extract']),
            'website_entries': len([d for d in all_tax_data if d.get('type') == 'website']),
            'hardcoded_entries': len([d for d in all_tax_data if d.get('type') in ['tax_slab', 'deduction']]),
            'output_file': str(output_file)
        }

def main():
    """Example usage"""
    scraper = TaxRuleScraper()
    result = scraper.collect_all_tax_data()
    print(f"Tax data collection completed: {result}")

if __name__ == "__main__":
    main()