"""
FILE INTELLIGENCE CORE
Handles all file operations: detection, extraction, categorization
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import mimetypes
from datetime import datetime
import re
import json

# PDF handling
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

# Image handling
try:
    from PIL import Image
    import pytesseract
    # Set Tesseract path
    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\jonat\tesseract.exe'
except ImportError:
    Image = None
    pytesseract = None

# CSV/Excel handling
try:
    import pandas as pd
except ImportError:
    pd = None

class FileIntelligence:
    """
    Core file intelligence system for research operations
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        
        # File type categories
        self.categories = {
            'document': ['.pdf', '.docx', '.doc', '.txt', '.md', '.rtf'],
            'spreadsheet': ['.csv', '.xlsx', '.xls', '.tsv'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'web': ['.html', '.htm', '.xml', '.json'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.sh', '.bat']
        }
        
        # Investigation keywords for auto-categorization
        self.investigation_keywords = {
            'weather_modification': [
                'weather', 'cloud seeding', 'geoengineering', 'haarp',
                'atmospheric', 'climate', 'popeye', 'enmod', 'silver iodide',
                'rain enhancement', 'hail suppression', 'drought'
            ],
            'surveillance_infrastructure': [
                'surveillance', 'raytheon', 'palantir', 'defense contractor',
                'rtx', 'lockheed', 'northrop', 'tracking', 'monitoring',
                'intelligence', 'sensor', 'data collection'
            ],
            'flight_tracking': [
                'flight', 'aircraft', 'flightradar', 'c-17', 'military aircraft',
                'transponder', 'adsb', 'faa', 'aviation', 'runway'
            ],
            'media_ownership': [
                'media', 'news', 'journalism', 'fox', 'cnn', 'newspaper',
                'broadcast', 'television', 'ownership', 'corporate media'
            ]
        }
    
    def detect_file_type(self, filepath: str) -> Dict[str, str]:
        """
        Detect file type and category
        
        Returns:
            {
                'extension': '.pdf',
                'category': 'document',
                'mime_type': 'application/pdf',
                'can_extract_text': True
            }
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            return {'error': 'File does not exist'}
        
        extension = filepath.suffix.lower()
        mime_type, _ = mimetypes.guess_type(str(filepath))
        
        # Determine category
        category = 'unknown'
        for cat, extensions in self.categories.items():
            if extension in extensions:
                category = cat
                break
        
        # Can we extract text?
        can_extract_text = False
        if category == 'document' or category == 'web':
            can_extract_text = True
        elif category == 'image' and Image and pytesseract:
            can_extract_text = True
        
        return {
            'extension': extension,
            'category': category,
            'mime_type': mime_type or 'unknown',
            'can_extract_text': can_extract_text,
            'size_bytes': filepath.stat().st_size,
            'size_mb': round(filepath.stat().st_size / (1024 * 1024), 2),
            'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
        }
    
    def extract_text_from_pdf(self, filepath: str) -> Dict[str, any]:
        """Extract text from PDF file"""
        if not PdfReader:
            return {'error': 'PyPDF2 not installed'}
        
        try:
            filepath = Path(filepath)
            reader = PdfReader(str(filepath))
            
            text_content = []
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_content.append({
                        'page': page_num,
                        'text': text
                    })
            
            full_text = '\n\n'.join([p['text'] for p in text_content])
            
            return {
                'success': True,
                'pages': len(reader.pages),
                'text_pages': len(text_content),
                'full_text': full_text,
                'page_texts': text_content,
                'word_count': len(full_text.split())
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def extract_text_from_image(self, filepath: str) -> Dict[str, any]:
        """Extract text from image using OCR"""
        if not Image or not pytesseract:
            return {'error': 'PIL or pytesseract not installed'}
        
        try:
            filepath = Path(filepath)
            image = Image.open(str(filepath))
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            return {
                'success': True,
                'text': text,
                'word_count': len(text.split()),
                'image_size': image.size,
                'image_mode': image.mode
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def extract_text(self, filepath: str) -> Dict[str, any]:
        """
        Universal text extraction - detects type and uses appropriate method
        """
        file_info = self.detect_file_type(filepath)
        
        if 'error' in file_info:
            return file_info
        
        if not file_info['can_extract_text']:
            return {'error': f"Cannot extract text from {file_info['category']} files"}
        
        filepath = Path(filepath)
        
        # PDF extraction
        if file_info['extension'] == '.pdf':
            return self.extract_text_from_pdf(filepath)
        
        # Image OCR
        elif file_info['category'] == 'image':
            return self.extract_text_from_image(filepath)
        
        # Plain text files
        elif file_info['extension'] in ['.txt', '.md']:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                return {
                    'success': True,
                    'text': text,
                    'word_count': len(text.split())
                }
            except Exception as e:
                return {'error': str(e)}
        
        # CSV files
        elif file_info['extension'] == '.csv' and pd is not None:
            try:
                df = pd.read_csv(filepath)
                return {
                    'success': True,
                    'text': df.to_string(),
                    'rows': len(df),
                    'columns': list(df.columns)
                }
            except Exception as e:
                return {'error': str(e)}
        
        return {'error': 'Unsupported file type for text extraction'}
    
    def extract_metadata(self, filepath: str) -> Dict[str, any]:
        """
        Extract metadata including dates, entities, locations
        """
        # First get text content
        extraction = self.extract_text(filepath)
        
        if 'error' in extraction:
            return extraction
        
        text = extraction.get('text', '')
        
        # Extract dates
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # 2024-12-10
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # 12/10/2024
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # December 10, 2024
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Extract potential entities (capitalized words/phrases)
        entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_entities = re.findall(entity_pattern, text)
        
        # Common entities to look for
        common_entities = [
            'Raytheon', 'RTX', 'Lockheed Martin', 'Northrop Grumman',
            'Palantir', 'Tomorrow.io', 'HAARP', 'NOAA', 'NASA', 'DOD',
            'CIA', 'FBI', 'Pentagon'
        ]
        
        found_entities = []
        text_lower = text.lower()
        for entity in common_entities:
            if entity.lower() in text_lower:
                # Count occurrences
                count = text_lower.count(entity.lower())
                found_entities.append({
                    'name': entity,
                    'count': count
                })
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        return {
            'success': True,
            'dates': list(set(dates))[:20],  # Unique dates, max 20
            'date_count': len(set(dates)),
            'found_entities': sorted(found_entities, key=lambda x: x['count'], reverse=True)[:10],
            'potential_entities': list(set(potential_entities))[:30],
            'urls': list(set(urls))[:10],
            'emails': list(set(emails))[:10],
            'word_count': len(text.split()),
            'char_count': len(text)
        }
    
    def categorize_content(self, filepath: str) -> List[str]:
        """
        Auto-categorize file into investigations based on content
        
        Returns list of matching investigation names
        """
        extraction = self.extract_text(filepath)
        
        if 'error' in extraction:
            return []
        
        text = extraction.get('text', '').lower()
        
        matches = []
        
        for investigation, keywords in self.investigation_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    score += text.count(keyword.lower())
            
            if score > 0:
                matches.append({
                    'investigation': investigation,
                    'score': score
                })
        
        # Sort by score, return investigation names
        matches.sort(key=lambda x: x['score'], reverse=True)
        return [m['investigation'] for m in matches]
    
    def analyze_file(self, filepath: str) -> Dict[str, any]:
        """
        Complete file analysis - type, extraction, metadata, categorization
        """
        file_info = self.detect_file_type(filepath)
        
        result = {
            'filepath': str(filepath),
            'filename': Path(filepath).name,
            'file_info': file_info
        }
        
        if 'error' in file_info:
            return result
        
        # Extract metadata
        if file_info['can_extract_text']:
            metadata = self.extract_metadata(filepath)
            result['metadata'] = metadata
            
            # Categorize
            categories = self.categorize_content(filepath)
            result['suggested_investigations'] = categories
        
        return result


# Command-line interface for testing
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python file_intelligence.py <filepath>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    fi = FileIntelligence()
    result = fi.analyze_file(filepath)
    
    print(json.dumps(result, indent=2))
