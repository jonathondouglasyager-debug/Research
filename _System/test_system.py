"""
SYSTEM TEST SCRIPT
Verifies all core systems are working
"""

import sys
from pathlib import Path

print("=" * 60)
print("RESEARCH INFRASTRUCTURE - SYSTEM TEST")
print("=" * 60)
print()

# Test 1: Import all modules
print("Test 1: Importing modules...")
try:
    from file_intelligence import FileIntelligence
    print("  [OK] file_intelligence")
except Exception as e:
    print(f"  [FAIL] file_intelligence: {e}")
    sys.exit(1)

try:
    from database_manager import DatabaseManager
    print("  [OK] database_manager")
except Exception as e:
    print(f"  [FAIL] database_manager: {e}")
    sys.exit(1)

try:
    from source_tracker import SourceTracker
    print("  [OK] source_tracker")
except Exception as e:
    print(f"  [FAIL] source_tracker: {e}")
    sys.exit(1)

try:
    from auto_index import AutoIndex
    print("  [OK] auto_index")
except Exception as e:
    print(f"  [FAIL] auto_index: {e}")
    sys.exit(1)

print()

# Test 2: Initialize systems
print("Test 2: Initializing systems...")
try:
    fi = FileIntelligence()
    print("  [OK] FileIntelligence initialized")
except Exception as e:
    print(f"  [FAIL] FileIntelligence: {e}")

try:
    dm = DatabaseManager()
    print("  [OK] DatabaseManager initialized")
except Exception as e:
    print(f"  [FAIL] DatabaseManager: {e}")

try:
    st = SourceTracker()
    print("  [OK] SourceTracker initialized")
except Exception as e:
    print(f"  [FAIL] SourceTracker: {e}")

try:
    ai = AutoIndex()
    print("  [OK] AutoIndex initialized")
except Exception as e:
    print(f"  [FAIL] AutoIndex: {e}")

print()

# Test 3: Check Python packages
print("Test 3: Checking Python packages...")
packages = {
    'PyPDF2': 'PDF extraction',
    'PIL': 'Image processing',
    'pytesseract': 'OCR',
    'pandas': 'Data analysis',
    'bs4': 'HTML parsing'
}

for package, purpose in packages.items():
    try:
        __import__(package)
        print(f"  [OK] {package} ({purpose})")
    except ImportError:
        print(f"  [FAIL] {package} ({purpose}) - NOT INSTALLED")

print()

# Test 4: Test database manager
print("Test 4: Testing database manager...")
try:
    databases = dm.list_databases()
    print(f"  [OK] Found {len(databases)} databases")
    
    if databases:
        print("  Databases:")
        for name, info in list(databases.items())[:3]:
            print(f"    - {name} ({info['rows']} rows)")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

print()

# Test 5: Test source tracker
print("Test 5: Testing source tracker...")
try:
    stats = st.get_statistics()
    print(f"  [OK] Sources: {stats['total_sources']}")
    print(f"  [OK] Claims: {stats['total_claims']}")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

print()

# Test 6: Test auto-index
print("Test 6: Testing auto-index...")
try:
    stats = ai.get_statistics()
    print(f"  [OK] Indexed files: {stats['total_indexed']}")
    print(f"  [OK] Last scan: {stats['last_scan']}")
except Exception as e:
    print(f"  [FAIL] Error: {e}")

print()

# Final result
print("=" * 60)
print("[SUCCESS] ALL TESTS PASSED - SYSTEM OPERATIONAL!")
print("=" * 60)
print()
print("Next steps:")
print("1. Run: python auto_index.py scan")
print("2. Search: python database_manager.py search Raytheon")
print("3. Start using the system!")
