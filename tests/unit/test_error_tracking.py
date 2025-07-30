#!/usr/bin/env python3
"""
Test script to verify enhanced error tracking in the batch evaluator.
This script simulates various error conditions to ensure they are properly captured.
"""

import sys
import os
import time
from datetime import datetime, timezone

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.llm_clients import get_llm_client
from batch_evaluator import run_single_batch

def test_error_tracking():
    """Test the enhanced error tracking functionality"""
    
    print("🧪 Testing Enhanced Error Tracking")
    print("=" * 50)
    
    # Test 1: Check if we can detect API failures
    print("\n1. Testing API failure detection...")
    
    # Create a test with invalid API keys to trigger errors
    original_env = os.environ.copy()
    
    try:
        # Temporarily set invalid API keys to trigger errors
        os.environ['GROQ_API_KEY'] = 'invalid_key_for_testing'
        os.environ['OPENROUTER_API_KEY'] = 'invalid_key_for_testing'
        
        # Run a small batch test
        print("Running batch evaluation with invalid keys...")
        run_single_batch(batch_id=999)  # Use a special batch ID for testing
        
        print("✅ Error tracking test completed")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)
    
    # Test 2: Check data file for error records
    print("\n2. Checking for error records in data...")
    
    try:
        import pandas as pd
        
        # Check if the test data was created
        test_file = "data/batch_eval_metrics.csv"
        if os.path.exists(test_file):
            df = pd.read_csv(test_file)
            
            # Filter for our test batch
            test_data = df[df['batch_id'] == 999]
            
            if len(test_data) > 0:
                print(f"📊 Found {len(test_data)} test records")
                
                # Check for failures
                failures = test_data[test_data['success'] == False]
                print(f"❌ Found {len(failures)} failed requests")
                
                if len(failures) > 0:
                    print("✅ Error tracking is working!")
                    print("\nSample error data:")
                    for _, row in failures.head(3).iterrows():
                        print(f"  Provider: {row['llm_provider']}")
                        print(f"  Model: {row['llm_model']}")
                        print(f"  Error Type: {row['error_type']}")
                        print(f"  Error: {row['error'][:100]}...")
                        print(f"  Retry Count: {row['retry_count']}")
                        print(f"  Rate Limit Hit: {row['rate_limit_hit']}")
                        print()
                else:
                    print("⚠️ No failures detected - this might indicate the error handling is working too well")
            else:
                print("⚠️ No test data found")
        else:
            print("⚠️ No data file found")
            
    except Exception as e:
        print(f"❌ Error checking data: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 Error tracking test completed")

def test_llm_client_errors():
    """Test individual LLM client error handling"""
    
    print("\n🔧 Testing LLM Client Error Handling")
    print("=" * 50)
    
    # Test with invalid API keys
    test_cases = [
        ('groq', 'llama3-70b-8192', 'invalid_groq_key'),
        ('openrouter', 'mistralai/mistral-7b-instruct', 'invalid_openrouter_key')
    ]
    
    for provider, model, invalid_key in test_cases:
        print(f"\nTesting {provider}/{model} with invalid key...")
        
        try:
            # Create client with invalid key
            if provider == 'groq':
                client = get_llm_client('groq', model)
                client.api_key = invalid_key
            else:
                client = get_llm_client('openrouter', model)
                client.api_key = invalid_key
            
            # Try to generate a response
            response = client.generate("Test prompt")
            print(f"❌ Expected error but got response: {response[:50]}...")
            
        except Exception as e:
            print(f"✅ Correctly caught error: {type(e).__name__}: {str(e)[:100]}...")
            
            # Check if it's an authentication error
            error_str = str(e).lower()
            if any(x in error_str for x in ['401', '403', 'unauthorized', 'forbidden', 'invalid']):
                print("✅ Authentication error correctly identified")
            else:
                print("⚠️ Unexpected error type")

if __name__ == "__main__":
    print("🚀 Starting Error Tracking Tests")
    
    # Test individual client error handling
    test_llm_client_errors()
    
    # Test batch error tracking
    test_error_tracking()
    
    print("\n🎯 All tests completed!") 