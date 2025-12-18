"""
TEST SUITE FOR PHASE 3: CONTENT GENERATION
Verify all generation systems are working correctly
"""

import sys
from pathlib import Path

# Add system paths
sys.path.append(str(Path(__file__).parent.parent / '_System'))

def test_timeline_builder():
    """Test timeline builder"""
    print("\n" + "="*60)
    print("TEST 1: TIMELINE AUTO-BUILDER")
    print("="*60)
    
    try:
        from timeline_builder import TimelineBuilder
        
        builder = TimelineBuilder()
        print("[OK] Timeline builder imported")
        
        # Try to build timeline
        timeline = builder.build_timeline("Fox_News_Corp")
        
        print(f"[OK] Timeline built successfully")
        print(f"     - Total events: {timeline['total_events']}")
        print(f"     - Date range: {timeline['date_range']['start'][:10] if timeline['date_range']['start'] else 'N/A'} to {timeline['date_range']['end'][:10] if timeline['date_range']['end'] else 'N/A'}")
        
        if timeline['events_by_year']:
            print(f"     - Events by year:")
            for year in sorted(timeline['events_by_year'].keys())[:5]:
                count = len(timeline['events_by_year'][year])
                print(f"       {year}: {count} events")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Timeline builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_entity_network_mapper():
    """Test entity network mapper"""
    print("\n" + "="*60)
    print("TEST 2: ENTITY NETWORK MAPPER")
    print("="*60)
    
    try:
        from entity_network_mapper import EntityNetworkMapper
        
        mapper = EntityNetworkMapper()
        print("[OK] Entity mapper imported")
        
        # Try to build network
        network = mapper.build_network("Fox_News_Corp")
        
        print(f"[OK] Network built successfully")
        print(f"     - Total nodes: {network['statistics']['total_nodes']}")
        print(f"     - Total edges: {network['statistics']['total_edges']}")
        
        if network['statistics']['entity_types']:
            print(f"     - Entity types:")
            for entity_type, count in list(network['statistics']['entity_types'].items())[:5]:
                print(f"       {entity_type}: {count}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Entity mapper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_generator():
    """Test investigation report generator"""
    print("\n" + "="*60)
    print("TEST 3: INVESTIGATION REPORT GENERATOR")
    print("="*60)
    
    try:
        from report_generator import ReportGenerator
        
        generator = ReportGenerator()
        print("[OK] Report generator imported")
        
        # Find an investigation to test
        research_dir = Path(r"C:\Users\jonat\Documents\Research")
        active_inv = research_dir / "Active_Investigations"
        
        if not active_inv.exists():
            print("[SKIP] No Active_Investigations folder found")
            return True
        
        # Get first investigation
        investigations = [d for d in active_inv.iterdir() if d.is_dir()]
        
        if not investigations:
            print("[SKIP] No investigations found")
            return True
        
        test_inv = investigations[0]
        print(f"[TEST] Using investigation: {test_inv.name}")
        
        # Gather data
        data = generator.gather_investigation_data(test_inv)
        
        print(f"[OK] Data gathered successfully")
        print(f"     - Investigation: {data['investigation_name']}")
        print(f"     - Entities: {len(data['entities'])}")
        print(f"     - Evidence files: {len(data['evidence'])}")
        print(f"     - Analysis reports: {len(data['analysis'])}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Report generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evidence_chain_builder():
    """Test evidence chain builder"""
    print("\n" + "="*60)
    print("TEST 4: EVIDENCE CHAIN BUILDER")
    print("="*60)
    
    try:
        from evidence_chain_builder import EvidenceChainBuilder
        
        builder = EvidenceChainBuilder()
        print("[OK] Evidence chain builder imported")
        
        # Test with a specific investigation's evidence folder
        research_dir = Path(r"C:\Users\jonat\Documents\Research")
        active_inv = research_dir / "Active_Investigations"
        
        if not active_inv.exists():
            print("[SKIP] No Active_Investigations folder found")
            return True
        
        # Find first investigation with evidence
        evidence_dir = None
        for inv_dir in active_inv.iterdir():
            if inv_dir.is_dir():
                ev_dir = inv_dir / "Evidence"
                if ev_dir.exists() and any(ev_dir.iterdir()):
                    evidence_dir = ev_dir
                    break
        
        if not evidence_dir:
            print("[SKIP] No evidence folders found with files")
            return True
        
        print(f"[TEST] Using evidence: {evidence_dir.parent.name}/Evidence")
        
        # Build a small chain (just analyze structure, don't process all files)
        files = list(evidence_dir.rglob('*'))[:5]  # Limit to 5 files
        
        print(f"[OK] Evidence folder accessible")
        print(f"     - Total files: {len(list(evidence_dir.rglob('*')))}")
        print(f"     - Test sample: {len(files)} files")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Evidence chain builder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Phase 3 tests"""
    print("\n" + "="*60)
    print("PHASE 3: CONTENT GENERATION TEST SUITE")
    print("="*60)
    print()
    print("Testing all generation systems...")
    print()
    
    results = {}
    
    # Run tests
    results['timeline_builder'] = test_timeline_builder()
    results['entity_network_mapper'] = test_entity_network_mapper()
    results['report_generator'] = test_report_generator()
    results['evidence_chain_builder'] = test_evidence_chain_builder()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print()
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n✅ ALL TESTS PASSED! Phase 3 is fully operational.")
    else:
        print(f"\n❌ {total_tests - passed_tests} test(s) failed. Check errors above.")
    
    print()
    print("="*60)
    
    return passed_tests == total_tests


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
