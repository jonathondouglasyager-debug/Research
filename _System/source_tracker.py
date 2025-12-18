"""
SOURCE TRACKER
Evidence provenance and citation management
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

class SourceTracker:
    """
    Tracks source documents and their citations
    Builds evidence chains for truth-telling
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        
        # Source registry file
        self.registry_file = self.research_dir / '_System' / 'source_registry.json'
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create registry
        self.sources = self.load_registry()
    
    def load_registry(self) -> Dict:
        """Load source registry from disk"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'sources': {}, 'claims': {}, 'chains': {}}
        return {'sources': {}, 'claims': {}, 'chains': {}}
    
    def save_registry(self):
        """Save source registry to disk"""
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.sources, f, indent=2)
    
    def generate_source_id(self, filepath: str) -> str:
        """Generate unique ID for a source document"""
        # Use file path hash as ID
        return hashlib.md5(str(filepath).encode()).hexdigest()[:12]
    
    def register_source(self, filepath: str, metadata: Dict = None) -> str:
        """
        Register a source document
        
        Args:
            filepath: Path to source document
            metadata: Optional metadata (author, date, type, etc.)
        
        Returns:
            source_id
        """
        filepath = Path(filepath)
        source_id = self.generate_source_id(str(filepath))
        
        if source_id in self.sources['sources']:
            # Already registered
            return source_id
        
        # Register new source
        source_data = {
            'id': source_id,
            'filepath': str(filepath.absolute()),
            'filename': filepath.name,
            'registered_date': datetime.now().isoformat(),
            'type': filepath.suffix.lower()[1:],  # Extension without dot
            'metadata': metadata or {}
        }
        
        # Try to extract additional metadata
        if filepath.exists():
            stat = filepath.stat()
            source_data['size_bytes'] = stat.st_size
            source_data['modified_date'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        self.sources['sources'][source_id] = source_data
        self.save_registry()
        
        return source_id
    
    def link_claim_to_source(self, claim: str, source_id: str, 
                            page_number: int = None, quote: str = None):
        """
        Link a research claim to its source
        
        Args:
            claim: The claim being made
            source_id: ID of source document
            page_number: Optional page number
            quote: Optional direct quote from source
        """
        claim_id = hashlib.md5(claim.encode()).hexdigest()[:12]
        
        if claim_id not in self.sources['claims']:
            self.sources['claims'][claim_id] = {
                'id': claim_id,
                'claim': claim,
                'sources': [],
                'created_date': datetime.now().isoformat()
            }
        
        # Add source reference
        source_ref = {
            'source_id': source_id,
            'page_number': page_number,
            'quote': quote,
            'linked_date': datetime.now().isoformat()
        }
        
        self.sources['claims'][claim_id]['sources'].append(source_ref)
        self.save_registry()
        
        return claim_id
    
    def generate_citation(self, source_id: str, style: str = 'apa') -> str:
        """
        Generate citation for a source
        
        Styles: 'apa', 'mla', 'chicago'
        """
        if source_id not in self.sources['sources']:
            return f"[Source not found: {source_id}]"
        
        source = self.sources['sources'][source_id]
        metadata = source['metadata']
        
        # Extract metadata
        title = metadata.get('title', source['filename'])
        author = metadata.get('author', 'Unknown')
        date = metadata.get('date', source.get('modified_date', 'n.d.'))[:10]  # YYYY-MM-DD
        url = metadata.get('url', '')
        publisher = metadata.get('publisher', '')
        
        if style == 'apa':
            # APA 7th edition style
            citation = f"{author}. ({date}). {title}."
            if publisher:
                citation += f" {publisher}."
            if url:
                citation += f" {url}"
            return citation
        
        elif style == 'mla':
            # MLA 9th edition style
            citation = f"{author}. \"{title}.\""
            if publisher:
                citation += f" {publisher},"
            citation += f" {date}."
            if url:
                citation += f" {url}."
            return citation
        
        elif style == 'chicago':
            # Chicago style
            citation = f"{author}. \"{title}.\""
            if publisher:
                citation += f" {publisher},"
            citation += f" {date}."
            if url:
                citation += f" {url}."
            return citation
        
        return f"{author}. {title}. {date}."
    
    def get_claim_sources(self, claim_id: str) -> List[Dict]:
        """
        Get all sources for a claim with full details
        """
        if claim_id not in self.sources['claims']:
            return []
        
        claim_data = self.sources['claims'][claim_id]
        result = []
        
        for source_ref in claim_data['sources']:
            source_id = source_ref['source_id']
            
            if source_id in self.sources['sources']:
                source = self.sources['sources'][source_id]
                
                result.append({
                    'source_id': source_id,
                    'filename': source['filename'],
                    'filepath': source['filepath'],
                    'citation': self.generate_citation(source_id),
                    'page_number': source_ref.get('page_number'),
                    'quote': source_ref.get('quote'),
                    'metadata': source.get('metadata', {})
                })
        
        return result
    
    def build_evidence_chain(self, chain_name: str, claims: List[str]) -> str:
        """
        Build an evidence chain linking multiple claims
        
        Args:
            chain_name: Name for this evidence chain
            claims: List of claim IDs or claim text
        
        Returns:
            chain_id
        """
        chain_id = hashlib.md5(chain_name.encode()).hexdigest()[:12]
        
        # Resolve claim IDs
        claim_ids = []
        for claim in claims:
            if claim in self.sources['claims']:
                claim_ids.append(claim)
            else:
                # Try to find by claim text
                for cid, cdata in self.sources['claims'].items():
                    if cdata['claim'] == claim:
                        claim_ids.append(cid)
                        break
        
        self.sources['chains'][chain_id] = {
            'id': chain_id,
            'name': chain_name,
            'claims': claim_ids,
            'created_date': datetime.now().isoformat()
        }
        
        self.save_registry()
        return chain_id
    
    def get_evidence_chain(self, chain_id: str) -> Dict:
        """
        Get full evidence chain with all claims and sources
        """
        if chain_id not in self.sources['chains']:
            return None
        
        chain = self.sources['chains'][chain_id]
        result = {
            'id': chain_id,
            'name': chain['name'],
            'claims': []
        }
        
        for claim_id in chain['claims']:
            if claim_id in self.sources['claims']:
                claim_data = self.sources['claims'][claim_id]
                
                result['claims'].append({
                    'id': claim_id,
                    'claim': claim_data['claim'],
                    'sources': self.get_claim_sources(claim_id)
                })
        
        return result
    
    def verify_sources(self) -> Dict[str, List]:
        """
        Verify all sources still exist and are accessible
        
        Returns:
            {
                'valid': [list of valid source_ids],
                'missing': [list of missing source_ids],
                'broken': [list of broken source_ids]
            }
        """
        valid = []
        missing = []
        broken = []
        
        for source_id, source in self.sources['sources'].items():
            filepath = Path(source['filepath'])
            
            if not filepath.exists():
                missing.append(source_id)
            else:
                try:
                    # Try to access file
                    filepath.stat()
                    valid.append(source_id)
                except:
                    broken.append(source_id)
        
        return {
            'valid': valid,
            'missing': missing,
            'broken': broken
        }
    
    def get_statistics(self) -> Dict:
        """Get source tracking statistics"""
        verification = self.verify_sources()
        
        # Count claims by number of sources
        unsourced = sum(1 for c in self.sources['claims'].values() if not c['sources'])
        single_source = sum(1 for c in self.sources['claims'].values() if len(c['sources']) == 1)
        multi_source = sum(1 for c in self.sources['claims'].values() if len(c['sources']) > 1)
        
        return {
            'total_sources': len(self.sources['sources']),
            'valid_sources': len(verification['valid']),
            'missing_sources': len(verification['missing']),
            'total_claims': len(self.sources['claims']),
            'unsourced_claims': unsourced,
            'single_source_claims': single_source,
            'multi_source_claims': multi_source,
            'evidence_chains': len(self.sources['chains'])
        }
    
    def export_bibliography(self, output_path: str, style: str = 'apa'):
        """Export all sources as a bibliography"""
        citations = []
        
        for source_id in sorted(self.sources['sources'].keys()):
            citation = self.generate_citation(source_id, style)
            citations.append(citation)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# Bibliography ({style.upper()} Style)\n\n")
            for citation in citations:
                f.write(f"- {citation}\n")
        
        print(f"Bibliography exported to {output_path}")


# Command-line interface
if __name__ == '__main__':
    st = SourceTracker()
    
    if len(sys.argv) == 1:
        # Show statistics
        print("\n=== SOURCE TRACKER ===\n")
        
        stats = st.get_statistics()
        
        print(f"Sources: {stats['total_sources']} total")
        print(f"  Valid: {stats['valid_sources']}")
        print(f"  Missing: {stats['missing_sources']}")
        
        print(f"\nClaims: {stats['total_claims']} total")
        print(f"  Unsourced: {stats['unsourced_claims']}")
        print(f"  Single source: {stats['single_source_claims']}")
        print(f"  Multiple sources: {stats['multi_source_claims']}")
        
        print(f"\nEvidence chains: {stats['evidence_chains']}")
    
    elif len(sys.argv) >= 2:
        command = sys.argv[1]
        
        if command == 'register':
            if len(sys.argv) < 3:
                print("Usage: python source_tracker.py register <filepath>")
                sys.exit(1)
            
            filepath = sys.argv[2]
            source_id = st.register_source(filepath)
            print(f"Registered source: {source_id}")
        
        elif command == 'cite':
            if len(sys.argv) < 3:
                print("Usage: python source_tracker.py cite <source_id> [style]")
                sys.exit(1)
            
            source_id = sys.argv[2]
            style = sys.argv[3] if len(sys.argv) > 3 else 'apa'
            
            citation = st.generate_citation(source_id, style)
            print(f"\n{citation}\n")
        
        elif command == 'verify':
            print("\nVerifying sources...")
            verification = st.verify_sources()
            
            print(f"Valid: {len(verification['valid'])}")
            print(f"Missing: {len(verification['missing'])}")
            print(f"Broken: {len(verification['broken'])}")
            
            if verification['missing']:
                print("\nMissing sources:")
                for sid in verification['missing']:
                    source = st.sources['sources'][sid]
                    print(f"  {source['filename']}")
        
        elif command == 'export':
            if len(sys.argv) < 3:
                print("Usage: python source_tracker.py export <output_path> [style]")
                sys.exit(1)
            
            output_path = sys.argv[2]
            style = sys.argv[3] if len(sys.argv) > 3 else 'apa'
            
            st.export_bibliography(output_path, style)
        
        else:
            print("Unknown command")
            print("\nAvailable commands:")
            print("  (none)                  - Show statistics")
            print("  register <filepath>     - Register a source")
            print("  cite <source_id> [style] - Generate citation")
            print("  verify                  - Verify all sources")
            print("  export <path> [style]   - Export bibliography")
