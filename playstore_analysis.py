#!/usr/bin/env python3
import pandas as pd
import os
import google.generativeai as genai
import time

# Replace with your actual API key
# SECURITY WARNING: Do not commit your actual API key to GitHub!
# Use an environment variable or a separate config file that is ignored by git.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

BATCH_SIZE = 10  # Increase to 50 to save (marginal) cost and improve speed

def configure_llm():
    """
    Configures the Google Gemini API and returns a list of available models.
    """
    genai.configure(api_key=GEMINI_API_KEY)
    
    try:
        # Dynamically find a supported model
        all_models = list(genai.list_models())
        available_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        print(f"🔎 Found {len(available_models)} active models: {available_models}")
        
        # Priority list of models to try
        preferences = [
            'models/gemini-3-flash-preview',
            'models/gemini-2.5-flash',
            'models/gemini-2.5-pro',
            'models/gemini-1.5-flash',
            'models/gemini-1.5-pro',
            'models/gemini-1.0-pro',
            'models/gemini-pro'
        ]
        
        valid_models = []
        for pref in preferences:
            if pref in available_models:
                valid_models.append(pref)
        
        # Add remaining available models
        for m in available_models:
            if 'gemini' in m and m not in valid_models:
                valid_models.append(m)
                
        if valid_models:
            print(f"🤖 AI Models available for rotation: {valid_models}")
            return valid_models
                
    except Exception as e:
        print(f"⚠️ Model discovery failed (Check API Key/Network): {e}")

    # Ultimate fallback
    print("⚠️ Using hardcoded fallback list.")
    return ['models/gemini-1.5-flash', 'models/gemini-pro']

def analyze_reviews_batch(model_names, reviews, app_context):
    """
    Sends a batch of reviews to the LLM for classification and prioritization.
    Rotates through models if rate limits are hit.
    """
    indexed_reviews = "\n".join([f"[{i}] {r}" for i, r in enumerate(reviews)])
    
    prompt = f"""
    You are a Product Manager assistant for the app '{app_context}'. Analyze these {len(reviews)} reviews:
    
    {indexed_reviews}
    
    Task:
    For each review, classify it into 'Bug Report', 'Feature Request', or 'General Feedback', and assign 'High', 'Medium', or 'Low' priority.
    
    Output Format:
    Return exactly {len(reviews)} lines. Each line must correspond to the review index and follow this format:
    [Index] Category | Priority
    
    Example:
    [0] Bug Report | High
    [1] General Feedback | Low
    """
    
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            results = {}
            if response.text:
                lines = response.text.strip().split('\n')
                for line in lines:
                    if '[' in line and ']' in line and '|' in line:
                        try:
                            idx_str = line.split('[')[1].split(']')[0]
                            idx = int(idx_str)
                            parts = line.split(']')[1].split('|')
                            if len(parts) >= 2:
                                results[idx] = (parts[0].strip(), parts[1].strip())
                        except:
                            continue
            
            # Return ordered list
            output = []
            for i in range(len(reviews)):
                output.append(results.get(i, ("General Feedback", "Low")))
            return output

        except Exception as e:
            print(f"⚠️ Error with {model_name}: {e}. Switching model...")
            time.sleep(1)
            continue

    # Fallback if all models fail
    print(f"⚠️ All models failed for this batch.")
    return [("General Feedback", "Low")] * len(reviews)

def generate_roadmap(model_names, df, app_context, output_dir):
    """
    Generates a strategic roadmap based on the analyzed reviews.
    """
    print(f"\n🗺️  Generating Product Roadmap for {app_context}...")
    
    # Filter for Feature Requests and High Priority Bugs
    features = df[df['category'] == 'Feature Request']['review_text'].tolist()
    # We look at high priority bugs to see what needs fixing immediately
    critical_bugs = df[(df['category'] == 'Bug Report') & (df['priority'] == 'High')]['review_text'].tolist()
    
    # Take a sample to fit in context (Gemini 1.5 Flash has a large context, but we limit for speed)
    features_sample = "\n- ".join(features[:50]) 
    bugs_sample = "\n- ".join(critical_bugs[:20])
    
    prompt = f"""
    You are the Chief Product Officer (CPO) for the mobile application '{app_context}'.
    Your goal is to create a professional, strategic Product Roadmap document based on recent user feedback.
    
    **Context:**
    - **App Name:** {app_context}
    - **Input Data:** A sample of recent high-priority bug reports and feature requests from the Google Play Store.
    
    **User Feedback Summary:**
    *Feature Requests (Voice of the Customer):*
    {features_sample}
    
    *Critical Bug Reports (Pain Points):*
    {bugs_sample}
    
    **Deliverable:**
    Generate a formal Product Roadmap Document in Markdown format. The tone should be professional, data-driven, and strategic.
    
    **Document Structure:**
    
    # Product Strategy & Roadmap: {app_context}
    
    ## 1. Executive Summary
    *   Briefly analyze the current sentiment and the industry vertical.
    *   Summarize the core problem areas and the biggest opportunities identified in the feedback.
    
    ## 2. Strategic Pillars for Next Quarter
    *   Define 3 key themes (e.g., "Stability First", "User Engagement") derived from the feedback.
    
    ## 3. Critical Firefighting (Immediate Priority)
    *   List the top 3-5 most critical bugs that must be fixed immediately to prevent churn.
    *   *Format:* **[Issue Name]**: Brief description and impact.
    
    ## 4. Feature Roadmap (Prioritized)
    *   Propose 3-5 new features or enhancements based on user requests.
    *   *Format:* **[Feature Name]** (Priority: High/Medium): Why this matters.
    
    ## 5. Blue Sky Innovation (Competitive Advantage)
    *   Suggest 2 industry-specific features that users haven't explicitly asked for but would differentiate {app_context} from competitors.
    
    ## 6. Success Metrics (KPIs)
    *   Suggest 3 Key Performance Indicators to track the success of this roadmap.
    """
    
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response.text:
                roadmap_path = os.path.join(output_dir, f"{app_context}_roadmap.md")
                with open(roadmap_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print(f"✅ Roadmap generated! Saved to: {roadmap_path}")
                return
        except Exception as e:
            print(f"⚠️ Roadmap generation failed with {model_name}: {e}. Switching...")
            continue
            
    print("❌ Roadmap generation failed with all available models.")

def analyze_dataset(file_path):
    print(f"\n🔄 Analyzing: {file_path}")
    try:
        df = pd.read_csv(file_path)
        
        if 'review_text' not in df.columns:
            print("❌ Error: CSV must contain a 'review_text' column.")
            return

        # Setup LLM
        try:
            model_names = configure_llm()
        except Exception as e:
            print(f"❌ Failed to configure LLM: {e}")
            return

        # Extract App Name from filename for context (e.g., 'com.spotify.music')
        filename = os.path.basename(file_path)
        app_context = filename.replace("_reviews.csv", "").replace("_analyzed_ai.csv", "")

        print("🤖 AI Analysis in progress... (Batch processing)")
        
        categories = []
        priorities = []
        total = len(df)
        all_reviews = df['review_text'].tolist()

        for i in range(0, total, BATCH_SIZE):
            batch = all_reviews[i : i + BATCH_SIZE]
            batch_results = analyze_reviews_batch(model_names, batch, app_context)
            
            for cat, prio in batch_results:
                categories.append(cat)
                priorities.append(prio)
            
            print(f"   Processed {min(i + BATCH_SIZE, total)}/{total} reviews...", end='\r')
            time.sleep(1.0) # Rate limiting: 1 batch per second is much faster than 1 review per second

        df['category'] = categories
        df['priority'] = priorities

        # Save with suffix
        output_path = file_path.replace(".csv", "_analyzed_ai.csv")
        df.to_csv(output_path, index=False)
        
        print(f"✅ Analysis Complete! Saved to: {output_path}")
        print(f"   - Bugs Identified: {len(df[df['category'] == 'Bug Report'])}")
        print(f"   - Feature Requests: {len(df[df['category'] == 'Feature Request'])}")
        
        # Estimate Cost (Flash Tier)
        # Assumptions: ~60 input tokens per review (incl prompt overhead), ~10 output tokens per review
        est_input_tokens = total * 60
        est_output_tokens = total * 10
        est_cost = (est_input_tokens / 1_000_000 * 0.075) + (est_output_tokens / 1_000_000 * 0.30)
        print(f"   - Estimated Cost (Flash Tier): ~${est_cost:.4f}")
        
        # Generate Strategic Roadmap
        generate_roadmap(model_names, df, app_context, os.path.dirname(file_path))
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        print(f"❌ Directory '{output_dir}' not found. Please fetch reviews first.")
    else:
        files = [f for f in os.listdir(output_dir) if f.endswith(".csv") and "_analyzed" not in f]
        
        if not files:
            print("❌ No raw CSV files found to analyze.")
        else:
            print("\nSelect an App to Analyze:")
            for i, f in enumerate(files):
                print(f"{i+1}. {f.replace('_reviews.csv', '')}")
            
            choice = input("\nEnter number: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(files):
                analyze_dataset(os.path.join(output_dir, files[int(choice)-1]))
            else:
                print("❌ Invalid selection.")