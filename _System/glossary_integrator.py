"""
GLOSSARY INTEGRATOR - Hybrid Local + Master Glossary System
Maintains investigation-specific glossaries and aggregates into master glossary
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class GlossaryIntegrator:
    """Manage glossary terms at investigation and master levels"""

    def __init__(self, investigation: str):
        self.research_dir = Path(r"C:\Users\jonat\Documents\Research")
        self.investigation = investigation
        self.investigation_dir = self.research_dir / "Active_Investigations" / investigation
        self.intelligence_dir = self.research_dir / "_Intelligence"

        # Create directories if needed
        self.intelligence_dir.mkdir(parents=True, exist_ok=True)

        # Glossary file paths
        self.local_glossary_file = self.investigation_dir / "glossary.json"
        self.master_glossary_file = self.intelligence_dir / "master_glossary.json"

    def load_glossary(self, filepath: Path) -> Dict:
        """Load glossary from JSON file"""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"terms": {}, "metadata": {}}
        return {"terms": {}, "metadata": {}}

    def save_glossary(self, glossary: Dict, filepath: Path):
        """Save glossary to JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(glossary, f, indent=2, ensure_ascii=False)

    def normalize_term(self, term: str) -> str:
        """Normalize term for matching"""
        return term.strip().lower()

    def integrate_terms(self, new_terms: List[Dict]) -> Dict:
        """Integrate new terms into local and master glossaries"""

        # Load existing glossaries
        local_glossary = self.load_glossary(self.local_glossary_file)
        master_glossary = self.load_glossary(self.master_glossary_file)

        # Initialize if needed
        if "terms" not in local_glossary:
            local_glossary = {"terms": {}, "metadata": {}}
        if "terms" not in master_glossary:
            master_glossary = {"terms": {}, "metadata": {}}

        stats = {
            "new_terms": 0,
            "updated_terms": 0,
            "total_local": 0,
            "total_master": 0
        }

        # Process each new term
        for term_data in new_terms:
            term = term_data.get('term', '')
            definition = term_data.get('definition', '')
            context = term_data.get('context', '')

            if not term or not definition:
                continue

            normalized = self.normalize_term(term)

            # Add to local glossary
            if normalized not in local_glossary["terms"]:
                local_glossary["terms"][normalized] = {
                    "term": term,  # Original capitalization
                    "definition": definition,
                    "contexts": [context] if context else [],
                    "first_seen": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "investigation": self.investigation,
                    "mention_count": 1
                }
                stats["new_terms"] += 1
            else:
                # Update existing term
                existing = local_glossary["terms"][normalized]

                # Append context if new
                if context and context not in existing.get("contexts", []):
                    if "contexts" not in existing:
                        existing["contexts"] = []
                    existing["contexts"].append(context)

                # Update definition if longer/better
                if len(definition) > len(existing.get("definition", "")):
                    existing["definition"] = definition

                existing["last_updated"] = datetime.now().isoformat()
                existing["mention_count"] = existing.get("mention_count", 1) + 1
                stats["updated_terms"] += 1

            # Add to master glossary
            if normalized not in master_glossary["terms"]:
                master_glossary["terms"][normalized] = {
                    "term": term,
                    "definition": definition,
                    "contexts": [context] if context else [],
                    "first_seen": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "investigations": [self.investigation],
                    "mention_count": 1
                }
            else:
                # Update master term
                existing = master_glossary["terms"][normalized]

                # Add investigation if new
                if self.investigation not in existing.get("investigations", []):
                    if "investigations" not in existing:
                        existing["investigations"] = []
                    existing["investigations"].append(self.investigation)

                # Append context if new
                if context and context not in existing.get("contexts", []):
                    if "contexts" not in existing:
                        existing["contexts"] = []
                    existing["contexts"].append(context)

                # Update definition if longer/better
                if len(definition) > len(existing.get("definition", "")):
                    existing["definition"] = definition

                existing["last_updated"] = datetime.now().isoformat()
                existing["mention_count"] = existing.get("mention_count", 1) + 1

        # Update metadata
        local_glossary["metadata"] = {
            "investigation": self.investigation,
            "term_count": len(local_glossary["terms"]),
            "last_updated": datetime.now().isoformat()
        }

        master_glossary["metadata"] = {
            "term_count": len(master_glossary["terms"]),
            "investigation_count": len(set(
                inv
                for term in master_glossary["terms"].values()
                for inv in term.get("investigations", [])
            )),
            "last_updated": datetime.now().isoformat()
        }

        # Save both glossaries
        self.save_glossary(local_glossary, self.local_glossary_file)
        self.save_glossary(master_glossary, self.master_glossary_file)

        stats["total_local"] = len(local_glossary["terms"])
        stats["total_master"] = len(master_glossary["terms"])

        return stats

    def get_term_definition(self, term: str, use_master: bool = False) -> Dict:
        """Look up a term definition"""
        normalized = self.normalize_term(term)

        if use_master:
            glossary = self.load_glossary(self.master_glossary_file)
        else:
            glossary = self.load_glossary(self.local_glossary_file)

        return glossary.get("terms", {}).get(normalized)

    def search_terms(self, query: str, use_master: bool = False) -> List[Dict]:
        """Search for terms containing query"""
        normalized_query = self.normalize_term(query)

        if use_master:
            glossary = self.load_glossary(self.master_glossary_file)
        else:
            glossary = self.load_glossary(self.local_glossary_file)

        results = []
        for normalized, term_data in glossary.get("terms", {}).items():
            if normalized_query in normalized or normalized_query in term_data.get("definition", "").lower():
                results.append(term_data)

        return results

    def export_glossary_markdown(self, filepath: Path = None, use_master: bool = False):
        """Export glossary as readable Markdown"""

        if use_master:
            glossary = self.load_glossary(self.master_glossary_file)
            title = "Master Glossary - All Investigations"
            output_file = filepath or (self.intelligence_dir / "master_glossary.md")
        else:
            glossary = self.load_glossary(self.local_glossary_file)
            title = f"Glossary - {self.investigation}"
            output_file = filepath or (self.investigation_dir / "glossary.md")

        # Sort terms alphabetically
        sorted_terms = sorted(
            glossary.get("terms", {}).values(),
            key=lambda x: x.get("term", "").lower()
        )

        # Generate markdown
        md_content = f"# {title}\n\n"
        md_content += f"**Total Terms:** {len(sorted_terms)}\n"
        md_content += f"**Last Updated:** {glossary.get('metadata', {}).get('last_updated', 'Unknown')}\n\n"
        md_content += "---\n\n"

        for term_data in sorted_terms:
            term = term_data.get("term", "Unknown")
            definition = term_data.get("definition", "No definition")
            contexts = term_data.get("contexts", [])
            mention_count = term_data.get("mention_count", 1)

            md_content += f"## {term}\n\n"
            md_content += f"**Definition:** {definition}\n\n"

            if mention_count > 1:
                md_content += f"**Mentions:** {mention_count}\n\n"

            if contexts:
                md_content += "**Context:**\n"
                for context in contexts[:3]:  # Show top 3 contexts
                    md_content += f"> {context}\n\n"

            if use_master:
                investigations = term_data.get("investigations", [])
                if investigations:
                    md_content += f"**Appears in:** {', '.join(investigations)}\n\n"

            md_content += "---\n\n"

        # Save markdown
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return output_file


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Integrate glossary terms')
    parser.add_argument('--investigation', required=True, help='Investigation name')
    parser.add_argument('--terms-file', help='JSON file with terms to integrate')
    parser.add_argument('--export', action='store_true', help='Export glossary as Markdown')
    parser.add_argument('--master', action='store_true', help='Use master glossary')

    args = parser.parse_args()

    integrator = GlossaryIntegrator(investigation=args.investigation)

    if args.export:
        output = integrator.export_glossary_markdown(use_master=args.master)
        print(f"[OK] Glossary exported: {output}")
    elif args.terms_file:
        with open(args.terms_file, 'r') as f:
            terms = json.load(f)
        stats = integrator.integrate_terms(terms)
        print(f"[OK] Glossary integration complete:")
        print(f"  - New terms: {stats['new_terms']}")
        print(f"  - Updated terms: {stats['updated_terms']}")
        print(f"  - Total local: {stats['total_local']}")
        print(f"  - Total master: {stats['total_master']}")


if __name__ == '__main__':
    main()
