"""
ENTITY INTEGRATOR
Intelligently merge entities into investigation databases
"""

import os
import sys
import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from difflib import SequenceMatcher


class EntityIntegrator:
    """
    Intelligently integrates entities into investigation databases

    Features:
    - Fuzzy matching (handles "RTX" = "Raytheon" = "RTX Corporation")
    - Smart merging without data loss
    - Automatic deduplication
    - Cross-investigation tracking
    """

    def __init__(self, research_dir: str = None):
        """Initialize entity integrator"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"

        self.research_dir = Path(research_dir)

        # Fuzzy match threshold (0-1, where 1 is exact match)
        self.match_threshold = 0.85

    def integrate_entities(self, entities: List[Dict], investigation: str) -> Dict:
        """
        Integrate entities into investigation database

        Args:
            entities: List of entity dicts from agent findings
            investigation: Investigation name

        Returns:
            Integration report dict
        """
        print(f"\n[ENTITY INTEGRATOR] Integrating {len(entities)} entities into {investigation}")

        # Get investigation directory
        inv_dir = self.research_dir / 'Active_Investigations' / investigation
        entity_db_path = inv_dir / 'entity_database.csv'

        # Load existing database or create new one
        existing_entities = self._load_entity_database(entity_db_path)

        # Integration statistics
        stats = {
            'total_new': len(entities),
            'added': 0,
            'merged': 0,
            'skipped': 0,
            'details': []
        }

        # Process each entity
        for entity in entities:
            result = self._integrate_single_entity(entity, existing_entities, investigation)
            stats['details'].append(result)

            if result['action'] == 'added':
                stats['added'] += 1
            elif result['action'] == 'merged':
                stats['merged'] += 1
            elif result['action'] == 'skipped':
                stats['skipped'] += 1

        # Save updated database
        self._save_entity_database(entity_db_path, existing_entities)

        print(f"[ENTITY INTEGRATOR] Integration complete:")
        print(f"  Added: {stats['added']} new entities")
        print(f"  Merged: {stats['merged']} existing entities")
        print(f"  Skipped: {stats['skipped']} duplicates")

        return stats

    def _load_entity_database(self, db_path: Path) -> List[Dict]:
        """
        Load entity database from CSV

        Returns list of entity dicts
        """
        if not db_path.exists():
            print(f"[ENTITY INTEGRATOR] Creating new database: {db_path}")
            # Return empty list with header row
            return []

        entities = []
        with open(db_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entities.append(row)

        print(f"[ENTITY INTEGRATOR] Loaded {len(entities)} existing entities")
        return entities

    def _save_entity_database(self, db_path: Path, entities: List[Dict]):
        """Save entity database to CSV"""
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Define fieldnames (backward compatible with existing schema)
        fieldnames = [
            'Entity_Name', 'Entity_Type', 'Description', 'First_Mentioned',
            'Source', 'Role', 'Connections', 'Status', 'Notes',
            # New optional fields
            'Financial_Data', 'Temporal_Data', 'Network_Degree',
            'Cross_Investigations', 'Last_Updated'
        ]

        # Ensure all entities have all fields (fill with empty strings)
        for entity in entities:
            for field in fieldnames:
                if field not in entity:
                    entity[field] = ''

        # Write CSV
        with open(db_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(entities)

        print(f"[ENTITY INTEGRATOR] Saved {len(entities)} entities to {db_path}")

    def _integrate_single_entity(self, new_entity: Dict, existing_entities: List[Dict],
                                 investigation: str) -> Dict:
        """
        Integrate a single entity

        Returns:
            dict with 'action' (added/merged/skipped) and details
        """
        entity_name = new_entity.get('name', '')

        # Try to find existing match
        match = self._find_matching_entity(entity_name, existing_entities)

        if match:
            # Entity exists - merge data
            existing_entity = existing_entities[match['index']]
            merged = self._merge_entity_data(existing_entity, new_entity, investigation)

            # Update in place
            existing_entities[match['index']] = merged

            return {
                'action': 'merged',
                'entity_name': entity_name,
                'matched_with': match['entity']['Entity_Name'],
                'confidence': match['confidence']
            }
        else:
            # New entity - add to database
            formatted_entity = self._format_new_entity(new_entity, investigation)
            existing_entities.append(formatted_entity)

            return {
                'action': 'added',
                'entity_name': entity_name
            }

    def _find_matching_entity(self, name: str, entities: List[Dict]) -> Optional[Dict]:
        """
        Find matching entity using fuzzy matching

        Returns:
            dict with 'entity', 'index', 'confidence' or None
        """
        best_match = None
        best_confidence = 0
        best_index = -1

        name_normalized = self._normalize_name(name)

        for i, entity in enumerate(entities):
            existing_name = entity.get('Entity_Name', '')
            confidence = self._calculate_match_confidence(name, existing_name)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = entity
                best_index = i

        if best_confidence >= self.match_threshold:
            return {
                'entity': best_match,
                'index': best_index,
                'confidence': best_confidence
            }

        return None

    def _calculate_match_confidence(self, name1: str, name2: str) -> float:
        """
        Calculate confidence score for entity name match

        Uses multiple matching strategies
        """
        # Exact match
        if name1 == name2:
            return 1.0

        # Normalize names
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)

        # Exact normalized match
        if norm1 == norm2:
            return 1.0

        # One contains the other (e.g., "RTX" in "RTX Corporation")
        if norm1 in norm2 or norm2 in norm1:
            return 0.95

        # Sequence matching (character-level similarity)
        ratio = SequenceMatcher(None, norm1, norm2).ratio()

        # Check for acronym match (e.g., "FDA" matches "Food and Drug Administration")
        if self._is_acronym_match(name1, name2):
            return max(ratio, 0.90)

        return ratio

    def _normalize_name(self, name: str) -> str:
        """Normalize entity name for matching"""
        # Lowercase
        name = name.lower()

        # Remove common suffixes
        suffixes = ['inc', 'corp', 'corporation', 'ltd', 'llc', 'company', 'co']
        for suffix in suffixes:
            name = re.sub(rf'\b{suffix}\.?\b', '', name)

        # Remove punctuation and extra spaces
        name = re.sub(r'[^\w\s]', '', name)
        name = ' '.join(name.split())

        return name.strip()

    def _is_acronym_match(self, name1: str, name2: str) -> bool:
        """Check if one name is an acronym of the other"""
        # Determine which is shorter (potential acronym)
        if len(name1) < len(name2):
            acronym = name1
            full_name = name2
        else:
            acronym = name2
            full_name = name1

        # Acronym must be 2-5 uppercase letters
        if not (2 <= len(acronym) <= 5 and acronym.isupper()):
            return False

        # Extract first letters from full name
        words = full_name.split()
        first_letters = ''.join(word[0].upper() for word in words if word)

        return acronym == first_letters

    def _merge_entity_data(self, existing: Dict, new: Dict, investigation: str) -> Dict:
        """
        Merge new entity data into existing entity without data loss

        Strategy:
        - Keep existing data
        - Append new information to description/notes
        - Update Last_Updated
        - Add cross-investigation reference
        """
        merged = existing.copy()

        # Append to description if new info
        new_desc = new.get('description', '')
        if new_desc and new_desc not in merged.get('Description', ''):
            if merged.get('Description'):
                merged['Description'] += f" | {new_desc}"
            else:
                merged['Description'] = new_desc

        # Append to notes
        new_role = new.get('role', '')
        if new_role:
            note = f"[{datetime.now().strftime('%Y-%m-%d')}] {new_role}"
            if merged.get('Notes'):
                merged['Notes'] += f" | {note}"
            else:
                merged['Notes'] = note

        # Update connections
        new_connections = new.get('connections', '')
        if new_connections and new_connections not in merged.get('Connections', ''):
            if merged.get('Connections'):
                merged['Connections'] += f" | {new_connections}"
            else:
                merged['Connections'] = new_connections

        # Add cross-investigation reference
        if investigation not in merged.get('Cross_Investigations', ''):
            if merged.get('Cross_Investigations'):
                merged['Cross_Investigations'] += f", {investigation}"
            else:
                merged['Cross_Investigations'] = investigation

        # Update timestamp
        merged['Last_Updated'] = datetime.now().strftime('%Y-%m-%d')

        return merged

    def _format_new_entity(self, entity: Dict, investigation: str) -> Dict:
        """Format new entity for database"""
        return {
            'Entity_Name': entity.get('name', ''),
            'Entity_Type': entity.get('type', 'Unknown'),
            'Description': entity.get('description', ''),
            'First_Mentioned': entity.get('first_mentioned', datetime.now().strftime('%Y-%m-%d')),
            'Source': entity.get('source', ''),
            'Role': entity.get('role', ''),
            'Connections': entity.get('connections', ''),
            'Status': 'Active',
            'Notes': '',
            'Financial_Data': '',
            'Temporal_Data': '',
            'Network_Degree': '0',
            'Cross_Investigations': investigation,
            'Last_Updated': datetime.now().strftime('%Y-%m-%d')
        }


def main():
    """Command-line interface for testing"""
    import argparse

    parser = argparse.ArgumentParser(description='Entity Integrator')
    parser.add_argument('findings_file', help='Path to agent findings JSON file')
    parser.add_argument('investigation', help='Investigation name')

    args = parser.parse_args()

    # Load findings
    with open(args.findings_file, 'r') as f:
        findings = json.load(f)

    entities = findings['findings']['entities_discovered']

    print(f"\nIntegrating {len(entities)} entities from {args.findings_file}")

    # Integrate
    integrator = EntityIntegrator()
    stats = integrator.integrate_entities(entities, args.investigation)

    # Print report
    print(f"\n{'='*70}")
    print("INTEGRATION REPORT")
    print(f"{'='*70}")
    print(f"\nTotal entities: {stats['total_new']}")
    print(f"Added new: {stats['added']}")
    print(f"Merged existing: {stats['merged']}")
    print(f"Skipped: {stats['skipped']}")

    print(f"\nDetails:")
    for detail in stats['details']:
        if detail['action'] == 'added':
            print(f"  + {detail['entity_name']} (new)")
        elif detail['action'] == 'merged':
            print(f"  ~ {detail['entity_name']} -> {detail['matched_with']} ({detail['confidence']:.2f})")


if __name__ == '__main__':
    main()
