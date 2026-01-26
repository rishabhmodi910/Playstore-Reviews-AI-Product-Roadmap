#!/usr/bin/env python3
import pandas as pd
import os
import google.generativeai as genai
import time

# API Key Configuration
# SECURITY WARNING: Do not commit your actual API key to GitHub!
# Priority: 1. Environment variable, 2. User input prompt
GEMINI_API_KEY = None

# Model Configuration
MODEL_NAME = 'models/gemini-2.5-pro'

BATCH_SIZE = 10  # Increase to 50 to save (marginal) cost and improve speed

def get_api_key():
    """
    Gets the API key from environment variable or prompts user for input.
    """
    global GEMINI_API_KEY
    
    # Try environment variable first
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key and api_key != "YOUR_API_KEY_HERE":
        GEMINI_API_KEY = api_key
        print("✅ Using API key from environment variable.")
        return api_key
    
    # Prompt user for API key
    print("\n🔑 API Key Required")
    print("   Get your key from: https://aistudio.google.com/")
    api_key = input("   Enter your Gemini API key: ").strip()
    
    if not api_key:
        raise ValueError("❌ API key is required. Please set GEMINI_API_KEY environment variable or provide it when prompted.")
    
    GEMINI_API_KEY = api_key
    return api_key

def configure_llm():
    """
    Configures the Google Gemini API and returns the model name.
    Uses Gemini 2.5 Pro model.
    """
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    
    try:
        # Verify the model is available
        all_models = list(genai.list_models())
        available_models = [m.name for m in all_models if 'generateContent' in m.supported_generation_methods]
        
        if MODEL_NAME in available_models:
            print(f"✅ Using model: {MODEL_NAME}")
            return MODEL_NAME
        else:
            print(f"⚠️ Warning: {MODEL_NAME} not found in available models.")
            print(f"   Available models: {available_models[:5]}...")
            print(f"   Attempting to use {MODEL_NAME} anyway...")
            return MODEL_NAME
                
    except Exception as e:
        print(f"⚠️ Model discovery failed (Check API Key/Network): {e}")
        print(f"   Will attempt to use {MODEL_NAME} anyway...")
        return MODEL_NAME

def analyze_reviews_batch(model_name, reviews, app_context):
    """
    Sends a batch of reviews to the LLM for classification and prioritization.
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
        print(f"⚠️ Error with {model_name}: {e}")
        print(f"   Returning default classifications for this batch.")
        return [("General Feedback", "Low")] * len(reviews)

def generate_roadmap(model_name, df, app_context, output_dir):
    """
    Generates a tactical product roadmap based on the analyzed reviews.
    """
    print(f"\n🗺️  Generating Product Roadmap for {app_context}...")
    
    # Filter for Feature Requests and High Priority Bugs
    features = df[df['category'] == 'Feature Request']['review_text'].tolist()
    # We look at high priority bugs to see what needs fixing immediately
    critical_bugs = df[(df['category'] == 'Bug Report') & (df['priority'] == 'High')]['review_text'].tolist()
    
    # Take a sample to fit in context
    features_sample = "\n- ".join(features[:50]) 
    bugs_sample = "\n- ".join(critical_bugs[:20])
    
    prompt = f"""
**Context:**
- **App Name:** {app_context}
- **Input Data:** Segmented raw feedback from the Play Store.

**User Feedback Data:**
*Feature Requests:*
{features_sample}

*Critical Bug Reports:*
{bugs_sample}

**Instructions:**
Analyze the data above and generate a Tactical Product Roadmap. 
Avoid corporate jargon. Be specific, technical, and solution-oriented.

**Deliverable Structure (Markdown):**

# Tactical Roadmap: {app_context}

## 1. The "Must-Fix" List (Immediate Engineering Priority)
*Identify the bugs that are functionally breaking the app. For each, provide:*
- **Defect:** [Specific name of the bug]
- **User Impact:** [What the user is unable to do]
- **Success Criteria:** [E.g., "Crash rate drops below 1%" or "Login succeeds in <2s"]

## 2. Feature Enhancements (The "Quick Wins")
*Identify requested features that offer high value with seemingly low complexity.*
- **Feature:** [Name]
- **User Story:** As a [user type], I want to [action] so that [benefit].
- **Implementation Hint:** [Based on the request, what specifically needs to change in the UI or backend?]

## 3. Strategic Feature Bets (Complex Requests)
*Major feature requests that require significant dev time.*
- **Initiative:** [Name]
- **Problem Solved:** [Why do users want this?]
- **Risk/Complexity:** [High/Medium - Assess based on the nature of the request]

## 4. Discarded Suggestions (Out of Scope)
*List 2-3 requests you are choosing NOT to build right now and why (e.g., too niche, technically infeasible based on current context).*
"""
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        if response.text:
            roadmap_path = os.path.join(output_dir, f"{app_context}_roadmap.md")
            with open(roadmap_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"✅ Roadmap generated! Saved to: {roadmap_path}")
        else:
            print("❌ Roadmap generation failed: Empty response from model.")
    except Exception as e:
        print(f"❌ Roadmap generation failed: {e}")

def analyze_dataset(file_path):
    print(f"\n🔄 Analyzing: {file_path}")
    try:
        df = pd.read_csv(file_path)
        
        if 'review_text' not in df.columns:
            print("❌ Error: CSV must contain a 'review_text' column.")
            return

        # Setup LLM
        try:
            model_name = configure_llm()
        except Exception as e:
            print(f"❌ Failed to configure LLM: {e}")
            return

        # Extract App Name from filename for context (e.g., 'com.spotify.music')
        filename = os.path.basename(file_path)
        app_context = filename.replace("_reviews.csv", "").replace("_analyzed_ai.csv", "")

        print("🤖 AI Analysis in progress... (Batch processing)")
        print("   💡 Tip: Press Ctrl+C to interrupt and save partial results (requires ≥200 reviews for roadmap)")
        print()
        
        categories = []
        priorities = []
        total = len(df)
        all_reviews = df['review_text'].tolist()
        analyzed_count = 0
        MIN_REVIEWS_FOR_ROADMAP = 200

        try:
            for i in range(0, total, BATCH_SIZE):
                batch = all_reviews[i : i + BATCH_SIZE]
                batch_results = analyze_reviews_batch(model_name, batch, app_context)
                
                for cat, prio in batch_results:
                    categories.append(cat)
                    priorities.append(prio)
                
                analyzed_count = len(categories)
                print(f"   Processed {analyzed_count}/{total} reviews...", end='\r')
                time.sleep(1.0) # Rate limiting: 1 batch per second is much faster than 1 review per second

            # If we completed all reviews
            print(f"\n✅ Analysis Complete! Processed all {total} reviews.")
            
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Analysis interrupted by user.")
            print(f"   Processed {analyzed_count} out of {total} reviews.")
            
            if analyzed_count < MIN_REVIEWS_FOR_ROADMAP:
                print(f"\n❌ Insufficient reviews for roadmap generation.")
                print(f"   Analyzed: {analyzed_count} reviews")
                print(f"   Required: {MIN_REVIEWS_FOR_ROADMAP} reviews minimum")
                print(f"   Partial analysis will still be saved.")
            else:
                print(f"   ✅ Sufficient reviews ({analyzed_count} ≥ {MIN_REVIEWS_FOR_ROADMAP}) - roadmap will be generated.")

        # Create a dataframe with only analyzed reviews
        # Take only the rows that were successfully analyzed
        df_analyzed = df.iloc[:analyzed_count].copy()
        df_analyzed['category'] = categories
        df_analyzed['priority'] = priorities
        
        # Save with suffix
        output_path = file_path.replace(".csv", "_analyzed_ai.csv")
        df_analyzed.to_csv(output_path, index=False)
        
        print(f"\n💾 Analysis saved to: {output_path}")
        print(f"   - Reviews Analyzed: {len(df_analyzed)}")
        print(f"   - Bugs Identified: {len(df_analyzed[df_analyzed['category'] == 'Bug Report'])}")
        print(f"   - Feature Requests: {len(df_analyzed[df_analyzed['category'] == 'Feature Request'])}")
        
        # Estimate Cost (Gemini 2.5 Pro pricing)
        # Assumptions: ~60 input tokens per review (incl prompt overhead), ~10 output tokens per review
        # Gemini 2.5 Pro: $1.25 per 1M input tokens, $5.00 per 1M output tokens
        est_input_tokens = analyzed_count * 60
        est_output_tokens = analyzed_count * 10
        est_cost = (est_input_tokens / 1_000_000 * 1.25) + (est_output_tokens / 1_000_000 * 5.00)
        print(f"   - Estimated Cost (Gemini 2.5 Pro): ~${est_cost:.4f}")
        
        # Generate Strategic Roadmap only if we have enough reviews
        if analyzed_count >= MIN_REVIEWS_FOR_ROADMAP:
            print(f"\n🗺️  Generating Product Roadmap (based on {analyzed_count} analyzed reviews)...")
            generate_roadmap(model_name, df_analyzed, app_context, os.path.dirname(file_path))
        else:
            print(f"\n⚠️  Product Roadmap not generated.")
            print(f"   Reason: Too few reviews analyzed ({analyzed_count} < {MIN_REVIEWS_FOR_ROADMAP} minimum required)")
            print(f"   The partial analysis has been saved, but a roadmap requires at least {MIN_REVIEWS_FOR_ROADMAP} reviews.")
        
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