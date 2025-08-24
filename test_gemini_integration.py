#!/usr/bin/env python3
"""
Test script for Gemini API integration
"""

import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

async def test_gemini_api():
    """Test the Gemini API integration"""
    
    # Check if API key is set
    api_key = "AIzaSyBmdMaRB-sdP87dDCyg_hxmUiMUcrsu_6M"
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable not set")
        return False
    
    print("✅ GOOGLE_API_KEY found")
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    try:
        # Create model instance
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini model initialized")
        
        # Test simple generation
        response = model.generate_content("Say 'Hello World' in JSON format: {\"message\": \"Hello World\"}")
        print(f"✅ Gemini API response: {response.text}")
        
        # Test JSON parsing
        import json
        import re
        
        def clean_json_response(text: str) -> str:
            """Helper function to clean the JSON string from the model's response."""
            match = re.search(r'\{', text)
            if not match:
                return text
            json_str = text[match.start():]
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                return json_match.group(0)
            return text
        
        cleaned_response = clean_json_response(response.text)
        parsed_json = json.loads(cleaned_response)
        print(f"✅ JSON parsing successful: {parsed_json}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

async def test_entity_extraction():
    """Test entity extraction with Gemini"""
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return False
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    You are an expert entity extractor for insurance claims. Extract the key information from the user query.
    The user query is: "I am a 35 year old male from Mumbai with a 2 month old policy. I need to claim for heart surgery."
    Extract the following fields and respond ONLY with a JSON object:
    - age (integer, or null)
    - gender (string: "male", "female", or null)
    - location (string, or null)
    - procedure (string, or null)
    - policy_duration_months (integer, null if not mentioned, assume 'new policy' is 1 month)
    - intent (string: "claim_eligibility", "coverage_inquiry", "policy_details")

    JSON Response:
    """
    
    try:
        response = model.generate_content(prompt)
        print(f"✅ Entity extraction test: {response.text}")
        
        # Test JSON parsing
        import json
        import re
        
        def clean_json_response(text: str) -> str:
            match = re.search(r'\{', text)
            if not match:
                return text
            json_str = text[match.start():]
            json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if json_match:
                return json_match.group(0)
            return text
        
        cleaned_response = clean_json_response(response.text)
        parsed_json = json.loads(cleaned_response)
        print(f"✅ Entity extraction JSON: {parsed_json}")
        
        return True
        
    except Exception as e:
        print(f"❌ Entity extraction test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API Integration...")
    print("=" * 50)
    
    # Test basic API
    basic_test = asyncio.run(test_gemini_api())
    
    print("\n" + "=" * 50)
    
    # Test entity extraction
    entity_test = asyncio.run(test_entity_extraction())
    
    print("\n" + "=" * 50)
    
    if basic_test and entity_test:
        print("🎉 All tests passed! Gemini integration is working correctly.")
    else:
        print("❌ Some tests failed. Please check your API key and internet connection.") 