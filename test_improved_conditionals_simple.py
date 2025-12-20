#!/usr/bin/env python3
"""
Simple test of improved conditional functionality using main.py
"""

import subprocess
import sys

def test_conditional_improvements():
    """Test the improved conditional functionality"""
    
    test_cases = [
        "if age greater than 18 then print adult",
        "when temperature greater than 30 do print hot", 
        "if score less than 60 then print fail else print pass"
    ]
    
    print("🎉 TESTING IMPROVED CONDITIONAL STATEMENTS")
    print("=" * 50)
    print()
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"Test {i}: {test_input}")
        print("-" * 40)
        
        try:
            # Run through main.py
            result = subprocess.run([
                sys.executable, 'main.py', 
                '--input', test_input,
                '--no-gui'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Success!")
                print("Generated Code:")
                # Extract the Python code from output
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('Translation') and not line.startswith('Original'):
                        print(f"  {line}")
            else:
                print("❌ Error!")
                print(f"  {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout!")
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print()
        print("=" * 50)
        print()

if __name__ == "__main__":
    test_conditional_improvements()