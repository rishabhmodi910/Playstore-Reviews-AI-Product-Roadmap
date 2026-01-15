#!/usr/bin/env python3
import pandas as pd
from google_play_scraper import Sort, reviews, search
import time
from datetime import datetime
import os
import playstore_analysis  # Import the new analysis module

# ==========================================
# CONFIGURATION (DEFAULTS)
# ==========================================
DEFAULT_APP_ID = 'com.spotify.music' 
DEFAULT_COUNT = 1000 
DEFAULT_LANG = 'en'
DEFAULT_COUNTRY = 'us'

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_user_configuration():
    """
    Collects all user inputs: Country, Lang, App ID, Count, and Date Filter.
    """
    print("--- Google Play Review Scraper ---")
    
    # 1. Country & Language (Ask first to help with search)
    while True:
        country_input = input(f"1. Enter Country Code (e.g., us, gb, in) [default {DEFAULT_COUNTRY}]: ").strip()
        if not country_input:
            country = DEFAULT_COUNTRY
            break
        if len(country_input) == 2 and country_input.isalpha():
            country = country_input
            break
        print("   ⚠️ Invalid format. Please enter a 2-letter country code (e.g., 'us').")

    lang_input = input(f"2. Enter Language Code (e.g., en, es) [default {DEFAULT_LANG}]: ").strip()
    # Basic validation: if input is not 2 letters, fallback to default to prevent API errors
    lang = lang_input if (lang_input and len(lang_input) == 2) else DEFAULT_LANG
    
    # 3. Get App ID
    user_input = input(f"3. Enter App Name or ID (default: Spotify): ").strip()
    target_app_id = resolve_app_id(user_input, country, lang)

    # 4. Get Count
    count_input = input(f"4. Number of reviews to fetch (default {DEFAULT_COUNT}): ").strip()
    try:
        count = int(count_input) if count_input else DEFAULT_COUNT
    except ValueError:
        print(f"   Invalid number. Using default: {DEFAULT_COUNT}")
        count = DEFAULT_COUNT

    # 5. Get Date Filter
    date_input = input(f"5. Filter reviews after date (YYYY-MM-DD) [Enter to skip]: ").strip()
    min_date = None
    if date_input:
        try:
            min_date = pd.to_datetime(date_input)
            print(f"   Filtering for reviews after: {min_date.date()}")
        except Exception:
            print("   Invalid date format. Skipping date filter.")

    return target_app_id, count, country, lang, min_date

def resolve_app_id(user_input, country, lang):
    if not user_input:
        return DEFAULT_APP_ID

    # Heuristic: If it has a dot and no spaces, it's likely an App ID
    if "." in user_input and " " not in user_input:
        print(f"   Using provided ID: {user_input}")
        return user_input

    # Search logic
    print(f"🔎 Searching for '{user_input}'...")
    try:
        results = search(user_input, lang=lang, country=country, n_hits=5)
        
        # Filter out results with missing appId
        valid_results = [r for r in results if r.get('appId')]
        
        if not valid_results:
            print("❌ No apps found. Defaulting to Spotify.")
            return DEFAULT_APP_ID
            
        print("\nSelect an app:")
        for i, app in enumerate(valid_results):
            print(f"{i+1}. {app['title']} ({app['appId']})")

        choice = input("\nEnter number (default 1): ").strip()
        idx = int(choice) - 1 if choice.isdigit() else 0
        
        selected_app = valid_results[idx] if 0 <= idx < len(valid_results) else valid_results[0]
        print(f"✅ Selected: {selected_app['title']}")
        return selected_app['appId']

    except Exception as e:
        print(f"❌ Search failed: {e}")
        if "400" in str(e):
            print("   (This often means the Country or Language code was invalid)")
        return DEFAULT_APP_ID

def fetch_reviews(app_id, count, country, lang):
    if not app_id:
        print("❌ Error: Invalid App ID (None). Cannot fetch reviews.")
        return []
        
    print(f"\n🚀 Starting scrape for {app_id}...")
    print(f"   Target: {count} newest reviews (Country: {country}, Lang: {lang})")

    try:
        result, continuation_token = reviews(
            app_id,
            lang=lang,             
            country=country,          
            sort=Sort.NEWEST,      
            count=count
        )
        print(f"✅ Successfully fetched {len(result)} raw reviews.")
        return result
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        print("   💡 Tip: Check if the App ID is correct for this Country/Region.")
        print("   💡 Tip: Try running 'pip install --upgrade google-play-scraper'")
        return []

def process_data(raw_data, min_date=None):
    if not raw_data:
        return None

    df = pd.DataFrame(raw_data)

    # Basic cleanup
    selected_cols = ['content', 'score', 'at', 'thumbsUpCount', 'reviewId', 'appVersion']
    available_cols = [c for c in selected_cols if c in df.columns]
    df_clean = df[available_cols].copy()

    df_clean = df_clean.rename(columns={
        'content': 'review_text',
        'score': 'rating',
        'at': 'date',
        'thumbsUpCount': 'votes',
        'appVersion': 'version'
    })

    # Ensure date is datetime
    df_clean['date'] = pd.to_datetime(df_clean['date'])

    # Apply Date Filter if requested
    if min_date:
        original_count = len(df_clean)
        df_clean = df_clean[df_clean['date'] >= min_date]
        filtered_count = len(df_clean)
        print(f"📅 Date Filter Applied: kept {filtered_count} of {original_count} reviews.")
        
        if filtered_count == original_count and original_count > 0:
             print("   (Note: The oldest review fetched is still newer than your filter date. You may need to increase the fetch count to go back further.)")

    return df_clean

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("========================================")
    print("   GOOGLE PLAY STORE TOOLKIT")
    print("========================================")
    print("1. Fetch New Reviews")
    print("2. Analyze Existing CSV")
    print("3. Fetch & Analyze (End-to-End)")
    
    mode = input("\nSelect option (1, 2, or 3): ").strip()

    if mode in ['1', '3']:
        # --- FETCH MODE ---
        app_id, count, country, lang, min_date = get_user_configuration()
        raw_reviews = fetch_reviews(app_id, count, country, lang)
        df_reviews = process_data(raw_reviews, min_date)

        if df_reviews is not None and not df_reviews.empty:
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            filename = os.path.join(output_dir, f"{app_id}_reviews.csv")
            df_reviews.to_csv(filename, index=False)
            
            print(f"\n💾 Data saved to: {filename}")
            print("-" * 30)
            print(f"Oldest Review: {df_reviews['date'].min()}")
            print(f"Newest Review: {df_reviews['date'].max()}")
            print("-" * 30)
            
            if mode == '3':
                print("\n🚀 Starting Automatic Analysis...")
                playstore_analysis.analyze_dataset(filename)
        else:
            print("\n⚠️ No reviews found.")

    elif mode == '2':
        # --- ANALYSIS MODE ---
        output_dir = "outputs"
        if not os.path.exists(output_dir):
            print(f"❌ Output directory '{output_dir}' does not exist. Fetch reviews first.")
            exit()

        files = [f for f in os.listdir(output_dir) if f.endswith(".csv") and "_analyzed" not in f]
        
        if not files:
            print("❌ No raw CSV files found in 'outputs/'.")
            exit()

        print("\nSelect an App to Analyze:")
        for i, f in enumerate(files):
            app_name = f.replace("_reviews.csv", "")
            print(f"{i+1}. {app_name}")
        
        choice = input("\nEnter number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            selected_file = os.path.join(output_dir, files[int(choice)-1])
            playstore_analysis.analyze_dataset(selected_file)
        else:
            print("❌ Invalid selection.")
    else:
        print("❌ Invalid option selected.")