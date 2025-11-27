#!/usr/bin/env python3
"""
Test script to verify the dashboard fix.
This script creates a simple test server to verify the dashboard can load without crashes.
"""

import os
os.environ['PROJECT_ID'] = 'test-project'

# Mock BigQuery before importing main
from unittest.mock import Mock, MagicMock
import sys

# Create mock for google.cloud.bigquery
bigquery_mock = MagicMock()
sys.modules['google.cloud.bigquery'] = bigquery_mock

# Import the Flask app
from main import app

if __name__ == '__main__':
    print("🧪 Testing dashboard fix...")
    print("\n1. Testing that Flask app can be initialized...")
    print(f"   ✓ Flask app created successfully")
    print(f"   ✓ Routes registered: {list(app.url_map.iter_rules())}")
    
    print("\n2. Starting test server on http://localhost:5000")
    print("   Dashboard will be available at: http://localhost:5000/")
    print("   API endpoint at: http://localhost:5000/api/predictions")
    print("\n   Note: BigQuery calls will fail (no credentials), but we can test the dashboard loads.\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
