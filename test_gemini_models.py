#!/usr/bin/env python3
import google.generativeai as genai
import os

# SECURITY WARNING: Do not commit your actual API key to GitHub!
# Use an environment variable or a separate config file that is ignored by git.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

def run_test():
    print("========================================")
    print("   GEMINI MODEL AVAILABILITY TEST")
    print("========================================")
    
    # 1. Configure
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_API_KEY_HERE":
        print("🔑 Configuring API with provided key...")
    else:
        print("⚠️  No API key found. Please set GEMINI_API_KEY environment variable.")
        print("   Get your key from: https://aistudio.google.com/")
        return
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return

    # 2. List Models
    print("\n📡 Querying Google for available models...")
    try:
        all_models = list(genai.list_models())
        # Filter for models that support content generation
        generation_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        print(f"✅ Found {len(generation_models)} generation-capable models:")
        for m in generation_models:
            print(f"   - {m}")
            
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return

    # 3. Test Generation on ALL found models
    print("\n🧪 Testing generation on available models...")
    
    working_models = []
    
    for model_name in generation_models:
        print(f"   Testing {model_name}...", end=" ")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Test.")
            if response.text:
                print("✅ SUCCESS")
                working_models.append(model_name)
            else:
                print("⚠️ Empty response")
        except Exception as e:
            print(f"❌ Failed ({str(e)})")

    if working_models:
        print(f"\n🎉 SUCCESS! Your API key can access the following models:")
        for wm in working_models:
            print(f"   - {wm}")
    else:
        print("\n❌ FAILED. Could not generate content with any available model.")

if __name__ == "__main__":
    run_test()