"""
DATABASE MANAGER
Unified interface for all CSV/JSON databases
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import re

try:
    import pandas as pd
except ImportError:
    pd = None

class DatabaseManager:
    """
    Manages all research databases with unified query interface
    """
    
    def __init__(self, research_dir: str = None):
        """Initialize with research directory"""
        if research_dir is None:
            research_dir = r"C:\Users\jonat\Documents\Research"
        self.research_dir = Path(research_dir)
        
        self.databases = {}
        self.database_paths = {}
        
        # Auto-discover databases
        self.discover_databases()
    
    def discover_databases(self):
        """
        Auto-discover all CSV databases in research directory
        """
        if not pd:
            print("Warning: pandas not installed, database features limited")
            return
        
        # Search for CSV files
        for csv_file in self.research_dir.rglob('*.csv'):
            # Skip temporary files
            if csv_file.name.startswith('~') or csv_file.name.startswith('.'):
                continue
            
            db_name = csv_file.stem  # filename without extension
            
            try:
                df = pd.read_csv(csv_file)
                self.databases[db_name] = df
                self.database_paths[db_name] = str(csv_file)
                
            except Exception as e:
                print(f"Warning: Could not load {csv_file.name}: {e}")
    
    def list_databases(self) -> Dict[str, Dict]:
        """
        List all loaded databases with metadata
        """
        result = {}
        
        for name, df in self.databases.items():
            result[name] = {
                'name': name,
                'path': self.database_paths[name],
                'rows': len(df),
                'columns': list(df.columns),
                'size_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
            }
        
        return result
    
    def get_database(self, name: str) -> Optional[pd.DataFrame]:
        """Get a specific database by name"""
        return self.databases.get(name)
    
    def search_database(self, db_name: str, query: str, columns: List[str] = None) -> pd.DataFrame:
        """
        Search a specific database
        
        Args:
            db_name: Name of database to search
            query: Search term (case-insensitive)
            columns: Optional list of columns to search (default: all text columns)
        
        Returns:
            DataFrame with matching rows
        """
        if not pd:
            return None
        
        df = self.databases.get(db_name)
        if df is None:
            return None
        
        # If no columns specified, search all object (text) columns
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns.tolist()
        
        # Build search mask
        mask = pd.Series([False] * len(df))
        
        for col in columns:
            if col in df.columns:
                # Case-insensitive search
                mask |= df[col].astype(str).str.contains(query, case=False, na=False, regex=False)
        
        return df[mask]
    
    def search_all_databases(self, query: str) -> Dict[str, pd.DataFrame]:
        """
        Search across ALL databases
        
        Returns:
            Dictionary mapping database_name -> matching_rows
        """
        results = {}
        
        for db_name in self.databases.keys():
            matches = self.search_database(db_name, query)
            if matches is not None and len(matches) > 0:
                results[db_name] = matches
        
        return results
    
    def find_entity(self, entity_name: str) -> Dict[str, List[Dict]]:
        """
        Find all mentions of an entity across all databases
        
        Returns formatted results with context
        """
        results = {}
        
        search_results = self.search_all_databases(entity_name)
        
        for db_name, df in search_results.items():
            records = []
            for _, row in df.iterrows():
                records.append(row.to_dict())
            
            results[db_name] = {
                'count': len(records),
                'records': records
            }
        
        return results
    
    def cross_reference(self, entity1: str, entity2: str) -> Dict[str, pd.DataFrame]:
        """
        Find records that mention BOTH entities
        """
        results = {}
        
        for db_name, df in self.databases.items():
            # Search for entity1
            matches1 = self.search_database(db_name, entity1)
            
            if matches1 is not None and len(matches1) > 0:
                # Within those results, search for entity2
                text_cols = matches1.select_dtypes(include=['object']).columns.tolist()
                mask = pd.Series([False] * len(matches1))
                
                for col in text_cols:
                    if col in matches1.columns:
                        mask |= matches1[col].astype(str).str.contains(
                            entity2, case=False, na=False, regex=False
                        )
                
                both_matches = matches1[mask]
                
                if len(both_matches) > 0:
                    results[db_name] = both_matches
        
        return results
    
    def get_entity_connections(self, entity_name: str, max_connections: int = 10) -> Dict[str, int]:
        """
        Find other entities commonly mentioned with this entity
        
        Returns dictionary of entity_name -> co-occurrence count
        """
        connections = {}
        
        # Find all records mentioning the entity
        entity_records = self.find_entity(entity_name)
        
        # Common entities to look for
        common_entities = [
            'Raytheon', 'RTX', 'Lockheed Martin', 'Northrop Grumman',
            'Palantir', 'Tomorrow.io', 'HAARP', 'NOAA', 'NASA', 'DOD',
            'CIA', 'FBI', 'Pentagon', 'Operation Popeye', 'ENMOD',
            'FlightRadar24', 'Charles Hatfield', 'Vincent Schaefer'
        ]
        
        for db_name, data in entity_records.items():
            for record in data['records']:
                # Check entire record for other entities
                record_text = ' '.join([str(v) for v in record.values()]).lower()
                
                for other_entity in common_entities:
                    if other_entity.lower() != entity_name.lower():
                        if other_entity.lower() in record_text:
                            connections[other_entity] = connections.get(other_entity, 0) + 1
        
        # Sort by count and return top connections
        sorted_connections = dict(
            sorted(connections.items(), key=lambda x: x[1], reverse=True)[:max_connections]
        )
        
        return sorted_connections
    
    def export_search_results(self, results: Dict[str, pd.DataFrame], output_path: str):
        """
        Export search results to CSV
        """
        if not results:
            print("No results to export")
            return
        
        # Combine all results
        all_results = []
        
        for db_name, df in results.items():
            df_copy = df.copy()
            df_copy['source_database'] = db_name
            all_results.append(df_copy)
        
        combined = pd.concat(all_results, ignore_index=True)
        combined.to_csv(output_path, index=False)
        
        print(f"Exported {len(combined)} results to {output_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall database statistics
        """
        total_rows = sum(len(df) for df in self.databases.values())
        total_columns = sum(len(df.columns) for df in self.databases.values())
        
        # Find most common entities across all databases
        all_text = ""
        for df in self.databases.values():
            text_cols = df.select_dtypes(include=['object']).columns
            for col in text_cols:
                all_text += " " + " ".join(df[col].astype(str).tolist())
        
        common_entities = [
            'Raytheon', 'RTX', 'Lockheed', 'Northrop', 'Palantir',
            'Tomorrow.io', 'HAARP', 'NOAA', 'NASA', 'DOD', 'Popeye'
        ]
        
        entity_counts = {}
        for entity in common_entities:
            count = all_text.lower().count(entity.lower())
            if count > 0:
                entity_counts[entity] = count
        
        return {
            'total_databases': len(self.databases),
            'total_rows': total_rows,
            'total_columns': total_columns,
            'databases': list(self.databases.keys()),
            'top_entities': dict(
                sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            )
        }
    
    def reload_databases(self):
        """Reload all databases from disk"""
        self.databases.clear()
        self.database_paths.clear()
        self.discover_databases()


# Command-line interface
if __name__ == '__main__':
    dm = DatabaseManager()
    
    if len(sys.argv) == 1:
        # No arguments - show statistics
        print("\n=== DATABASE MANAGER ===\n")
        
        dbs = dm.list_databases()
        print(f"Found {len(dbs)} databases:\n")
        
        for name, info in dbs.items():
            print(f"  {name}")
            print(f"    Rows: {info['rows']}")
            print(f"    Columns: {', '.join(info['columns'][:5])}" + 
                  ("..." if len(info['columns']) > 5 else ""))
            print()
        
        stats = dm.get_statistics()
        print("\nOverall Statistics:")
        print(f"  Total rows: {stats['total_rows']}")
        print(f"  Total columns: {stats['total_columns']}")
        
        if stats['top_entities']:
            print("\n  Top entities mentioned:")
            for entity, count in list(stats['top_entities'].items())[:5]:
                print(f"    {entity}: {count} times")
    
    elif len(sys.argv) >= 2:
        command = sys.argv[1]
        
        if command == 'search':
            if len(sys.argv) < 3:
                print("Usage: python database_manager.py search <query>")
                sys.exit(1)
            
            query = ' '.join(sys.argv[2:])
            print(f"\nSearching for: {query}\n")
            
            results = dm.search_all_databases(query)
            
            if not results:
                print("No results found")
            else:
                for db_name, df in results.items():
                    print(f"\n{db_name}: {len(df)} matches")
                    print(df.to_string())
        
        elif command == 'entity':
            if len(sys.argv) < 3:
                print("Usage: python database_manager.py entity <entity_name>")
                sys.exit(1)
            
            entity = ' '.join(sys.argv[2:])
            print(f"\nFinding entity: {entity}\n")
            
            results = dm.find_entity(entity)
            
            if not results:
                print("Entity not found")
            else:
                for db_name, data in results.items():
                    print(f"\n{db_name}: {data['count']} mentions")
        
        elif command == 'connections':
            if len(sys.argv) < 3:
                print("Usage: python database_manager.py connections <entity_name>")
                sys.exit(1)
            
            entity = ' '.join(sys.argv[2:])
            print(f"\nFinding connections for: {entity}\n")
            
            connections = dm.get_entity_connections(entity)
            
            if not connections:
                print("No connections found")
            else:
                print("Connected entities:")
                for other_entity, count in connections.items():
                    print(f"  {other_entity}: {count} co-occurrences")
        
        else:
            print("Unknown command")
            print("\nAvailable commands:")
            print("  (none)           - Show database statistics")
            print("  search <query>   - Search all databases")
            print("  entity <name>    - Find entity mentions")
            print("  connections <name> - Find entity connections")
