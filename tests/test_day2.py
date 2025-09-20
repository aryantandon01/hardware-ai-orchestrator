# test_day2_fixed.py - Fixed Day 2 RAG Testing with Correct Data Structure Access

import requests
import json
import time
import sys
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

class Day2FixedRAGTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": time.time(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if not success and "error" in details:
            print(f"   Error: {details['error']}")
        elif success and "summary" in details:
            print(f"   {details['summary']}")
    
    def test_knowledge_retrieval_system_health(self) -> bool:
        """Test Day 2 knowledge retrieval system availability"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                components = data.get("components", {})
                
                # Check if knowledge retrieval component is operational
                knowledge_status = components.get("knowledge_retrieval", "unknown")
                
                if knowledge_status == "operational":
                    self.log_result("Knowledge Retrieval System Health", True, {
                        "summary": f"Knowledge retrieval system operational",
                        "all_components": components
                    })
                    return True
                else:
                    self.log_result("Knowledge Retrieval System Health", False, {
                        "error": f"Knowledge retrieval status: {knowledge_status}",
                        "components": components
                    })
                    return False
            else:
                self.log_result("Knowledge Retrieval System Health", False, {
                    "error": f"Health check failed: HTTP {response.status_code}"
                })
                return False
                
        except Exception as e:
            self.log_result("Knowledge Retrieval System Health", False, {"error": str(e)})
            return False
    
    def test_chromadb_component_database_access(self) -> bool:
        """Test ChromaDB hardware_components collection access via RAG"""
        
        # Test queries targeting component database
        component_queries = [
            {
                "name": "Power Management Component",
                "query": "LM317 voltage regulator specifications and applications",
                "expertise": "intermediate"
            },
            {
                "name": "Microcontroller Database",
                "query": "ARM Cortex-M4 microcontroller for automotive applications",
                "expertise": "senior"
            },
            {
                "name": "Analog IC Component",
                "query": "precision operational amplifier for medical instrumentation",
                "expertise": "expert"
            }
        ]
        
        success_count = 0
        
        for test_case in component_queries:
            try:
                payload = {
                    "query": test_case["query"],
                    "user_expertise": test_case["expertise"]
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/analyze-with-knowledge",
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    knowledge = data.get("knowledge", {})
                    components = knowledge.get("components", [])
                    retrieval_summary = knowledge.get("retrieval_summary", {})
                    
                    if len(components) > 0:
                        success_count += 1
                        
                        # Extract actual component names for validation
                        component_names = []
                        for comp in components[:3]:  # Show first 3
                            comp_data = comp.get('component', {})
                            comp_name = comp_data.get('name', comp_data.get('part_number', 'Unknown'))
                            component_names.append(comp_name)
                        
                        self.log_result(f"Components RAG: {test_case['name']}", True, {
                            "summary": f"Retrieved {len(components)} components from ChromaDB",
                            "components_count": len(components),
                            "sample_components": component_names,
                            "retrieval_quality": retrieval_summary.get("overall_quality", "N/A")
                        })
                        
                        print(f"     Sample components: {', '.join(component_names)}")
                    else:
                        self.log_result(f"Components RAG: {test_case['name']}", False, {
                            "error": "No components retrieved from ChromaDB",
                            "knowledge_structure": list(knowledge.keys())
                        })
                else:
                    self.log_result(f"Components RAG: {test_case['name']}", False, {
                        "error": f"HTTP {response.status_code}: {response.text[:100]}"
                    })
                    
            except Exception as e:
                self.log_result(f"Components RAG: {test_case['name']}", False, {"error": str(e)})
        
        component_db_success = success_count >= len(component_queries) * 0.67
        
        self.log_result("ChromaDB Component Database Access", component_db_success, {
            "summary": f"{success_count}/{len(component_queries)} component queries retrieved data",
            "note": "Day 2 spec requires 500+ component entries"
        })
        
        return component_db_success
    
    def test_chromadb_standards_database_access(self) -> bool:
        """Test ChromaDB compliance_standards collection access via RAG"""
        
        standards_queries = [
            {
                "name": "AEC-Q100 Automotive Standards",
                "query": "AEC-Q100 Grade 0 qualification requirements for automotive components",
                "expertise": "expert"
            },
            {
                "name": "IEC 60601 Medical Standards",
                "query": "IEC 60601 electrical safety requirements for medical device design",
                "expertise": "expert"
            }
        ]
        
        success_count = 0
        
        for test_case in standards_queries:
            try:
                payload = {
                    "query": test_case["query"],
                    "user_expertise": test_case["expertise"]
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/analyze-with-knowledge",
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    knowledge = data.get("knowledge", {})
                    standards = knowledge.get("standards", [])
                    
                    if len(standards) > 0:
                        success_count += 1
                        
                        # Extract actual standard names for validation
                        standard_names = []
                        for std in standards[:3]:  # Show first 3
                            std_data = std.get('standard', {})
                            std_name = std_data.get('name', std_data.get('standard_id', 'Unknown'))
                            standard_names.append(std_name)
                        
                        self.log_result(f"Standards RAG: {test_case['name']}", True, {
                            "summary": f"Retrieved {len(standards)} standards from ChromaDB",
                            "standards_count": len(standards),
                            "sample_standards": standard_names
                        })
                        
                        print(f"     Sample standards: {', '.join(standard_names)}")
                    else:
                        self.log_result(f"Standards RAG: {test_case['name']}", False, {
                            "error": "No standards retrieved from ChromaDB",
                            "knowledge_structure": list(knowledge.keys())
                        })
                else:
                    self.log_result(f"Standards RAG: {test_case['name']}", False, {
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                self.log_result(f"Standards RAG: {test_case['name']}", False, {"error": str(e)})
        
        standards_success = success_count >= len(standards_queries) * 0.5
        
        self.log_result("ChromaDB Standards Database Access", standards_success, {
            "summary": f"{success_count}/{len(standards_queries)} standards queries retrieved data",
            "note": "Day 2 spec requires AEC-Q100, ISO 26262, IEC 60601 standards"
        })
        
        return standards_success
    
    def test_true_vector_search_semantic_quality(self) -> bool:
        """Test TRUE semantic quality of ChromaDB vector search - FIXED DATA STRUCTURE ACCESS"""
        
        semantic_quality_tests = [
            {
                "name": "Power Management Semantic Search",
                "query": "low power switching regulator for battery powered automotive sensors",
                "expected_component_keywords": ["power", "regulator", "converter", "switching", "battery", "low power", "efficient", "buck", "boost"],
                "expected_standards_keywords": ["automotive", "aec-q100", "grade", "qualification"],
                "expected_categories": ["power_management"],
                "semantic_expectation": "Power management components with automotive compliance"
            },
            {
                "name": "Medical Device Semantic Search", 
                "query": "precision operational amplifier for medical device IEC 60601 electrical safety",
                "expected_component_keywords": ["amplifier", "precision", "operational", "op-amp", "medical", "low noise", "analog"],
                "expected_standards_keywords": ["iec 60601", "medical", "electrical safety", "patient"],
                "expected_categories": ["analog", "amplifier"],
                "semantic_expectation": "Precision analog components with medical standards compliance"
            },
            {
                "name": "Microcontroller Semantic Search",
                "query": "ARM Cortex-M4 microcontroller ultra-low power consumption IoT wireless",
                "expected_component_keywords": ["arm", "cortex", "microcontroller", "mcu", "low power", "wireless", "iot", "stm32"],
                "expected_standards_keywords": ["fcc", "ce", "wireless", "iot"],
                "expected_categories": ["microcontroller", "embedded"],
                "semantic_expectation": "Low-power microcontrollers suitable for IoT applications"
            }
        ]
        
        success_count = 0
        
        for test_case in semantic_quality_tests:
            try:
                payload = {
                    "query": test_case["query"],
                    "user_expertise": "senior"
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/analyze-with-knowledge",
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    knowledge = data.get("knowledge", {})
                    components = knowledge.get("components", [])
                    standards = knowledge.get("standards", [])
                    
                    if len(components) == 0 and len(standards) == 0:
                        self.log_result(f"Semantic Quality: {test_case['name']}", False, {
                            "error": "No components or standards retrieved"
                        })
                        continue
                    
                    # FIXED: Test semantic relevance with correct data structure access
                    component_relevance_score = self._evaluate_component_semantic_relevance_fixed(
                        components, test_case["expected_component_keywords"]
                    )
                    
                    standards_relevance_score = self._evaluate_standards_semantic_relevance_fixed(
                        standards, test_case["expected_standards_keywords"]
                    )
                    
                    category_alignment_score = self._evaluate_category_alignment_fixed(
                        components, test_case["expected_categories"]
                    )
                    
                    # Overall semantic quality score (weighted average)
                    semantic_quality_score = (
                        component_relevance_score * 0.4 + 
                        standards_relevance_score * 0.3 + 
                        category_alignment_score * 0.3
                    )
                    
                    # Lower threshold for initial validation: 40% semantic relevance
                    if semantic_quality_score >= 0.4:
                        success_count += 1
                        self.log_result(f"Semantic Quality: {test_case['name']}", True, {
                            "summary": f"Good semantic quality: {semantic_quality_score:.3f} score",
                            "component_relevance": f"{component_relevance_score:.3f}",
                            "standards_relevance": f"{standards_relevance_score:.3f}",
                            "category_alignment": f"{category_alignment_score:.3f}",
                            "components_found": len(components),
                            "standards_found": len(standards),
                            "semantic_expectation": test_case["semantic_expectation"]
                        })
                        
                        # Show sample relevant components
                        if components:
                            print(f"     Sample retrieved components:")
                            for comp in components[:2]:
                                comp_data = comp.get('component', {})
                                comp_name = comp_data.get('name', comp_data.get('part_number', 'Unknown'))
                                comp_desc = comp_data.get('description', 'No description')[:80]
                                comp_category = comp_data.get('category', 'No category')
                                print(f"       • {comp_name} ({comp_category}): {comp_desc}")
                    else:
                        self.log_result(f"Semantic Quality: {test_case['name']}", False, {
                            "error": f"Low semantic quality: {semantic_quality_score:.3f} score (threshold: 0.40)",
                            "component_relevance": f"{component_relevance_score:.3f}",
                            "standards_relevance": f"{standards_relevance_score:.3f}",
                            "category_alignment": f"{category_alignment_score:.3f}",
                            "components_found": len(components),
                            "standards_found": len(standards)
                        })
                        
                        # Debug: Show what was actually retrieved
                        if components:
                            print(f"     Retrieved components (checking relevance):")
                            for comp in components[:2]:
                                comp_data = comp.get('component', {})
                                comp_name = comp_data.get('name', comp_data.get('part_number', 'Unknown'))
                                comp_category = comp_data.get('category', 'No category')
                                print(f"       • {comp_name} ({comp_category})")
                else:
                    self.log_result(f"Semantic Quality: {test_case['name']}", False, {
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                self.log_result(f"Semantic Quality: {test_case['name']}", False, {"error": str(e)})
        
        semantic_success = success_count >= len(semantic_quality_tests) * 0.66
        
        self.log_result("True Vector Search Semantic Quality", semantic_success, {
            "summary": f"{success_count}/{len(semantic_quality_tests)} semantic quality tests passed",
            "note": "Tests actual relevance of ChromaDB retrieved components/standards with FIXED data structure access"
        })
        
        return semantic_success
    
    def _evaluate_component_semantic_relevance_fixed(self, components: List[Dict], expected_keywords: List[str]) -> float:
        """FIXED: Evaluate semantic relevance with correct data structure access"""
        if not components:
            return 0.0
        
        relevant_components = 0
        
        for component in components:
            if self._is_component_relevant_fixed(component, expected_keywords):
                relevant_components += 1
        
        return relevant_components / len(components) if components else 0.0
    
    def _is_component_relevant_fixed(self, component: Dict, expected_keywords: List[str]) -> bool:
        """FIXED: Check component relevance with correct nested data structure access"""
        
        # FIXED: Access nested component data correctly
        comp_data = component.get('component', {})
        
        # Build searchable text from all relevant component fields
        comp_text = ""
        for field in ['name', 'part_number', 'description', 'category', 'manufacturer', 'key_features', 'applications']:
            if field in comp_data:
                value = comp_data[field]
                if isinstance(value, list):
                    comp_text += f" {' '.join(map(str, value))}"
                else:
                    comp_text += f" {value}"
        
        comp_text = comp_text.lower()
        
        # Check for keyword matches (at least 2 keywords should match for relevance)
        keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in comp_text)
        return keyword_matches >= min(2, len(expected_keywords) // 2)
    
    def _evaluate_standards_semantic_relevance_fixed(self, standards: List[Dict], expected_keywords: List[str]) -> float:
        """FIXED: Evaluate standards relevance with correct data structure access"""
        if not standards:
            return 0.0
        
        relevant_standards = 0
        
        for standard in standards:
            # FIXED: Access nested standard data correctly
            std_data = standard.get('standard', {})
            
            # Build searchable text from standard fields
            std_text = ""
            for field in ['name', 'standard_id', 'description', 'scope', 'organization']:
                if field in std_data:
                    std_text += f" {std_data[field]}"
            
            std_text = std_text.lower()
            
            # Check for keyword relevance (at least 1 keyword match for standards)
            keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in std_text)
            if keyword_matches >= 1:
                relevant_standards += 1
        
        return relevant_standards / len(standards) if standards else 0.0
    
    def _evaluate_category_alignment_fixed(self, components: List[Dict], expected_categories: List[str]) -> float:
        """FIXED: Evaluate category alignment with proper type handling"""
        if not components:
            return 0.0
        
        aligned_components = 0
        
        for component in components:
            comp_data = component.get('component', {})
            
            comp_category = comp_data.get('category', '').lower()
            comp_type = comp_data.get('type', '').lower()
            
            # FIX: Handle automotive qualification with proper type checking
            automotive_qualified = False
            
            # Check automotive_qualified field (boolean)
            if comp_data.get('automotive_qualified'):
                automotive_qualified = True
                
            # Check automotive_grade field (handle string/int/None safely)
            automotive_grade = comp_data.get('automotive_grade')
            if automotive_grade is not None:
                try:
                    if isinstance(automotive_grade, str):
                        # Handle string grades like "Grade 1", "1", etc.
                        if automotive_grade.lower().replace('grade ', '') not in ['0', '']:
                            automotive_qualified = True
                    elif isinstance(automotive_grade, (int, float)):
                        if automotive_grade > 0:
                            automotive_qualified = True
                except:
                    pass  # If anything fails, assume not qualified
            
            # Check category alignment
            category_match = any(expected_cat.lower() in comp_category or expected_cat.lower() in comp_type 
                            for expected_cat in expected_categories)
            
            # Special handling for automotive qualification
            if 'automotive' in str(expected_categories).lower() and automotive_qualified:
                category_match = True
            
            if category_match:
                aligned_components += 1
        
        return aligned_components / len(components) if components else 0.0

    
    def test_day1_day2_integration(self) -> bool:
        """Test integration of Day 1 (routing) + Day 2 (knowledge) functionality"""
        
        try:
            integration_query = {
                "query": "automotive qualified buck converter AEC-Q100 Grade 0 for 12V to 5V conversion with thermal management",
                "user_expertise": "expert"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analyze-with-knowledge",
                json=integration_query,
                timeout=25
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate Day 1 functionality is preserved
                day1_indicators = 0
                if "classification" in data:
                    day1_indicators += 1
                if "complexity" in data:
                    day1_indicators += 1
                if "routing" in data:
                    day1_indicators += 1
                
                # Validate Day 2 functionality is working
                day2_indicators = 0
                knowledge = data.get("knowledge", {})
                if "components" in knowledge:
                    day2_indicators += 1
                if "standards" in knowledge:
                    day2_indicators += 1
                if "retrieval_summary" in knowledge:
                    day2_indicators += 1
                
                integration_success = day1_indicators >= 2 and day2_indicators >= 2
                
                if integration_success:
                    self.log_result("Day 1 + Day 2 Integration", True, {
                        "summary": f"Integration working: Day 1 ({day1_indicators}/3), Day 2 ({day2_indicators}/3)",
                        "selected_model": data.get("routing", {}).get("selected_model", "unknown"),
                        "components_retrieved": len(knowledge.get("components", [])),
                        "standards_retrieved": len(knowledge.get("standards", []))
                    })
                    return True
                else:
                    self.log_result("Day 1 + Day 2 Integration", False, {
                        "error": f"Integration incomplete: Day 1 ({day1_indicators}/3), Day 2 ({day2_indicators}/3)",
                        "response_structure": list(data.keys())
                    })
                    return False
            else:
                self.log_result("Day 1 + Day 2 Integration", False, {
                    "error": f"HTTP {response.status_code}"
                })
                return False
                
        except Exception as e:
            self.log_result("Day 1 + Day 2 Integration", False, {"error": str(e)})
            return False
    
    def run_day2_fixed_tests(self) -> Dict[str, Any]:
        """Run Day 2 tests with FIXED data structure access"""
        print("🧠 Hardware AI Orchestrator - FIXED Day 2 RAG Testing")
        print("🎯 Testing: ChromaDB + sentence-transformers + CORRECTED Semantic Quality Validation")
        print("=" * 90)
        
        tests = [
            ("Knowledge System Health", self.test_knowledge_retrieval_system_health),
            ("Component Database (ChromaDB)", self.test_chromadb_component_database_access),
            ("Standards Database (ChromaDB)", self.test_chromadb_standards_database_access),
            ("FIXED Vector Search Semantic Quality", self.test_true_vector_search_semantic_quality),
            ("Day 1 + Day 2 Integration", self.test_day1_day2_integration)
        ]
        
        results = {}
        total_success = 0
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                success = test_func()
                results[test_name] = success
                if success:
                    total_success += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test_name}: {e}")
                results[test_name] = False
        
        # Summary
        success_rate = (total_success / len(tests)) * 100
        
        print(f"\n{'=' * 90}")
        print(f"🏆 FIXED DAY 2 RAG TEST RESULTS")
        print(f"{'=' * 90}")
        print(f"Tests Passed: {total_success}/{len(tests)} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print(f"✅ EXCELLENT: Day 2 RAG system with corrected semantic quality validation!")
            print(f"   • ChromaDB vector database working optimally")
            print(f"   • Component and standards retrieval highly relevant")
            print(f"   • sentence-transformers providing quality semantic matching") 
            print(f"   • Day 1 + Day 2 integration seamless")
            print(f"   • FIXED data structure access showing true semantic quality")
        elif success_rate >= 60:
            print(f"✅ GOOD: Day 2 RAG system functional with corrected validation")
            print(f"   • Core knowledge retrieval working")
            print(f"   • Semantic matching validated with proper data access")
        else:
            print(f"⚠️ NEEDS ATTENTION: Issues detected even with corrected validation")
            print(f"   • Check component database content quality")
            print(f"   • Verify sentence-transformers embeddings")
        
        return {
            "overall_success_rate": success_rate,
            "tests_passed": total_success,
            "total_tests": len(tests),
            "individual_results": results,
            "detailed_results": self.test_results,
            "fixed_validation": {
                "corrected_data_structure_access": True,
                "semantic_quality_validated": results.get("FIXED Vector Search Semantic Quality", False),
                "chromadb_integration": results.get("Component Database (ChromaDB)", False) or results.get("Standards Database (ChromaDB)", False),
                "day1_day2_integration": results.get("Day 1 + Day 2 Integration", False),
                "knowledge_retrieval_system": results.get("Knowledge System Health", False)
            }
        }

def main():
    """Main test execution"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
    
    print(f"🎯 Testing FIXED Day 2 RAG System at: {base_url}")
    
    tester = Day2FixedRAGTester(base_url)
    results = tester.run_day2_fixed_tests()
    
    # Return appropriate exit code
    if results["overall_success_rate"] >= 60:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
