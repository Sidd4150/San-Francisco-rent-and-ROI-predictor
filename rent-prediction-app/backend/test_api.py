#!/usr/bin/env python3
"""Test script to verify investment parameter transmission"""

import requests
import json

# Test data with all investment parameters
test_data = {
    "beds": 2,
    "baths": 2,
    "footage": 1200,
    "latitude": 37.7749,
    "longitude": -122.4194,
    "purchasePrice": 1200000,
    "downPaymentPercent": 20,
    "interestRate": 7.0,
    "loanTermYears": 30,
    "propertyTaxRate": 1.25,
    "insuranceMonthly": 300,
    "utilitiesMonthly": 200,
    "maintenancePercent": 1,
    "propertyManagementPercent": 8,
    "vacancyRate": 5
}

print("🧪 Testing API with full investment parameters...")
print(f"📊 Sending data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post("http://localhost:8000/predict", json=test_data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS! Response received:")
        print(json.dumps(result, indent=2))
        
        # Check if investment parameters are in the response
        if "input_features" in result:
            print("\n🔍 Checking investment parameters in response:")
            features = result["input_features"]
            params = [
                "downPaymentPercent", "interestRate", "loanTermYears",
                "propertyTaxRate", "insuranceMonthly", "utilitiesMonthly",
                "maintenancePercent", "propertyManagementPercent", "vacancyRate"
            ]
            
            missing = []
            for param in params:
                if param in features:
                    print(f"   ✅ {param}: {features[param]}")
                else:
                    print(f"   ❌ {param}: MISSING!")
                    missing.append(param)
            
            if missing:
                print(f"\n⚠️  WARNING: {len(missing)} parameters missing from response!")
            else:
                print("\n🎉 All investment parameters successfully transmitted!")
    else:
        print(f"\n❌ ERROR: Status code {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")