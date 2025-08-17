"""
Task 1.1.8 Frontend Component Implementation Tests
==================================================

Test suite to validate that all core React components are properly implemented
and pass their comprehensive test suites.

Success Criteria:
- All Login component tests pass
- All Register component tests pass  
- All Navbar component tests pass
- All CapeAI Chat component tests pass
- All components render without errors
- All components have proper accessibility features
- All form validation works correctly
"""

import subprocess
import sys
import os
import json
from pathlib import Path

class FrontendComponentTester:
    """Helper class for testing frontend components"""
    
    def __init__(self):
        self.client_dir = Path("/home/robert/Documents/localstorm250722/client")
        self.results = {
            "components_tested": [],
            "tests_passed": 0,
            "tests_failed": 0,
            "implementation_issues": [],
            "success_rate": 0
        }
    
    def run_component_tests(self, component_pattern=None):
        """Run frontend component tests"""
        try:
            os.chdir(self.client_dir)
            
            if component_pattern:
                cmd = ["npm", "test", "--", "--run", f"src/test/{component_pattern}"]
            else:
                cmd = ["npm", "test", "--", "--run"]
            
            print(f"🧪 Running frontend tests: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": "Test execution timed out"
            }
        except Exception as e:
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": str(e)
            }
    
    def parse_test_results(self, test_output):
        """Parse test results from vitest output"""
        lines = test_output.split('\n')
        
        for line in lines:
            # Look for test summary
            if "Test Files" in line and "passed" in line:
                # Extract numbers from line like "Test Files  6 failed | 1 passed (7)"
                if "failed" in line and "passed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "failed":
                            self.results["tests_failed"] += int(parts[i-1])
                        elif part == "passed":
                            self.results["tests_passed"] += int(parts[i-1])
            
            # Look for specific component test results
            if "Test Files" in line:
                continue
                
        # Calculate success rate
        total_tests = self.results["tests_passed"] + self.results["tests_failed"]
        if total_tests > 0:
            self.results["success_rate"] = (self.results["tests_passed"] / total_tests) * 100
    
    def analyze_component_issues(self, test_output):
        """Analyze specific component implementation issues"""
        lines = test_output.split('\n')
        
        current_component = None
        current_error = []
        
        for line in lines:
            # Detect component being tested
            if ".test.jsx" in line and ("Login" in line or "Register" in line or "Navbar" in line or "CapeAI" in line):
                if "Login" in line:
                    current_component = "Login"
                elif "Register" in line:
                    current_component = "Register" 
                elif "Navbar" in line:
                    current_component = "Navbar"
                elif "CapeAI" in line:
                    current_component = "CapeAIChat"
            
            # Detect common errors
            if "Element type is invalid" in line:
                self.results["implementation_issues"].append({
                    "component": current_component,
                    "issue": "Component not properly exported or imported",
                    "error": "Element type is invalid"
                })
            elif "Unable to find an element" in line:
                self.results["implementation_issues"].append({
                    "component": current_component,
                    "issue": "Missing UI elements or improper rendering",
                    "error": line.strip()
                })
            elif "Objects are not valid as a React child" in line:
                self.results["implementation_issues"].append({
                    "component": current_component,
                    "issue": "Component returning invalid JSX",
                    "error": "Invalid React child object"
                })
            elif "You cannot render a <Router> inside another <Router>" in line:
                self.results["implementation_issues"].append({
                    "component": current_component,
                    "issue": "Router nesting issue in test setup",
                    "error": "Nested Router components"
                })
    
def test_task_1_1_8_frontend_components():
    """Main test function for Task 1.1.8 - Frontend Component Implementation"""
    print("\n" + "="*70)
    print("🎨 TASK 1.1.8 - FRONTEND COMPONENT IMPLEMENTATION")
    print("="*70)
    print("Testing that all core React components are properly implemented")
    print("and pass their comprehensive test suites")
    print()
    
    tester = FrontendComponentTester()
    
    # Test each component individually to isolate issues
    components_to_test = [
        ("Login.test.jsx", "Login Page"),
        ("Register.test.jsx", "Register Page"),
        ("Navbar.test.jsx", "Navbar Component"),
        ("CapeAIChat.test.jsx", "CapeAI Chat Component")
    ]
    
    overall_success = True
    
    for test_file, component_name in components_to_test:
        print(f"\n🧪 Testing {component_name}...")
        print("-" * 50)
        
        # Run tests for this specific component
        result = tester.run_component_tests(test_file)
        
        if result["returncode"] == 0:
            print(f"✅ {component_name} - All tests passed!")
            tester.results["components_tested"].append(component_name)
        else:
            print(f"❌ {component_name} - Tests failed")
            overall_success = False
            
            # Analyze the specific issues
            tester.analyze_component_issues(result["stdout"] + result["stderr"])
            
            # Show some key error information
            output_lines = (result["stdout"] + result["stderr"]).split('\n')
            error_count = 0
            for line in output_lines:
                if ("Unable to find" in line or "Element type is invalid" in line or 
                    "Objects are not valid" in line) and error_count < 3:
                    print(f"   🔍 {line.strip()}")
                    error_count += 1
            
            if error_count >= 3:
                print("   📋 (More errors in full output...)")
    
    # Run full test suite to get overall metrics
    print(f"\n📊 Running full test suite for metrics...")
    full_result = tester.run_component_tests()
    tester.parse_test_results(full_result["stdout"])
    
    # Print final results
    print("\n" + "="*70)
    print("📋 TASK 1.1.8 FRONTEND COMPONENT IMPLEMENTATION RESULTS")
    print("="*70)
    
    print(f"📊 Test Summary:")
    print(f"   • Tests Passed: {tester.results['tests_passed']}")
    print(f"   • Tests Failed: {tester.results['tests_failed']}")
    print(f"   • Success Rate: {tester.results['success_rate']:.1f}%")
    print(f"   • Components Successfully Tested: {len(tester.results['components_tested'])}")
    
    print(f"\n🔍 Implementation Issues Found:")
    issues_by_component = {}
    for issue in tester.results["implementation_issues"]:
        comp = issue["component"] or "Unknown"
        if comp not in issues_by_component:
            issues_by_component[comp] = []
        issues_by_component[comp].append(issue["issue"])
    
    for component, issues in issues_by_component.items():
        print(f"   📦 {component}:")
        for issue in set(issues):  # Remove duplicates
            print(f"      - {issue}")
    
    if overall_success and tester.results["success_rate"] >= 80:
        print("\n✅ TASK 1.1.8 COMPLETE - FRONTEND COMPONENTS IMPLEMENTED")
        print("✅ All core components properly implemented and tested")
        print("✅ Component tests passing successfully")
        print("✅ UI elements rendering correctly")
        print("✅ Form validation and interactions working")
        return 0
    else:
        print("\n❌ TASK 1.1.8 INCOMPLETE - COMPONENT IMPLEMENTATION NEEDED")
        print("🔧 Core React components need implementation")
        print("🎨 UI elements and forms need proper rendering")
        print("🧪 Component tests need to pass")
        print("\n📋 NEXT STEPS:")
        print("1. Implement missing React components (Login, Register, Navbar, CapeAIChat)")
        print("2. Add proper JSX rendering and form elements")
        print("3. Implement component logic and state management")
        print("4. Add accessibility features and proper ARIA labels")
        print("5. Ensure all tests pass with proper component behavior")
        return 1

if __name__ == "__main__":
    exit_code = test_task_1_1_8_frontend_components()
    sys.exit(exit_code)
