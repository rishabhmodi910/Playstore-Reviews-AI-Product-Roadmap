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

# Valid ISO 3166-1 alpha-2 country codes (common markets)
VALID_COUNTRY_CODES = {
    'us', 'gb', 'in', 'ca', 'au', 'de', 'fr', 'jp', 'kr', 'cn', 'br', 'mx', 
    'es', 'it', 'nl', 'se', 'no', 'dk', 'fi', 'pl', 'ru', 'tr', 'sa', 'ae',
    'sg', 'my', 'th', 'ph', 'id', 'vn', 'nz', 'za', 'eg', 'ng', 'ke', 'ar',
    'cl', 'co', 'pe', 'ch', 'at', 'be', 'ie', 'pt', 'gr', 'cz', 'hu', 'ro',
    'bg', 'hr', 'sk', 'si', 'lt', 'lv', 'ee', 'is', 'lu', 'mt', 'cy', 'ie',
    'hk', 'tw', 'mo', 'pk', 'bd', 'lk', 'mm', 'kh', 'la', 'bn', 'fj', 'pg',
    'nc', 'pf', 'gu', 'as', 'mp', 'vi', 'pr', 'jm', 'tt', 'bb', 'bs', 'bz',
    'cr', 'pa', 'ni', 'hn', 'sv', 'gt', 'uy', 'py', 'bo', 'ec', 've', 'gy',
    'sr', 'gf', 'fk', 'gl', 'is', 'fo', 'sj', 'ax', 'ad', 'mc', 'sm', 'va',
    'li', 'mt', 'al', 'ba', 'me', 'mk', 'xk', 'md', 'ua', 'by', 'ge', 'am',
    'az', 'kz', 'uz', 'tm', 'kg', 'tj', 'af', 'ir', 'iq', 'sy', 'lb', 'jo',
    'il', 'ps', 'ye', 'om', 'kw', 'qa', 'bh', 'dj', 'so', 'et', 'er', 'sd',
    'ss', 'ug', 'tz', 'rw', 'bi', 'mw', 'zm', 'zw', 'bw', 'na', 'sz', 'ls',
    'mg', 'mu', 'sc', 'km', 'cv', 'gw', 'gn', 'sl', 'lr', 'ci', 'gh', 'tg',
    'bj', 'ne', 'bf', 'ml', 'mr', 'sn', 'gm', 'td', 'cm', 'cf', 'cg', 'ga',
    'gq', 'st', 'ao', 'cd', 'mz', 'ma', 'dz', 'tn', 'ly', 'eh', 'mr', 'ml'
}

# Valid ISO 639-1 language codes (common languages)
VALID_LANGUAGE_CODES = {
    'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi',
    'nl', 'pl', 'tr', 'sv', 'da', 'fi', 'no', 'cs', 'hu', 'ro', 'el', 'th',
    'vi', 'id', 'ms', 'tl', 'uk', 'he', 'fa', 'ur', 'bn', 'ta', 'te', 'mr',
    'gu', 'kn', 'ml', 'pa', 'or', 'as', 'ne', 'si', 'my', 'km', 'lo', 'ka',
    'am', 'sw', 'zu', 'af', 'sq', 'az', 'be', 'bg', 'bs', 'ca', 'hr', 'et',
    'eu', 'gl', 'is', 'ga', 'lv', 'lt', 'mk', 'mt', 'mn', 'sr', 'sk', 'sl',
    'cy', 'yi', 'eo', 'la', 'co', 'haw', 'ht', 'jv', 'su', 'ceb', 'ny', 'so',
    'zu', 'xh', 'yo', 'ig', 'sn', 'mg', 'ny', 'st', 'tn', 've', 'ts', 'ss'
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def validate_country_code(country_code):
    """
    Validates if a country code is a valid ISO 3166-1 alpha-2 code.
    """
    if not country_code or len(country_code) != 2:
        return False
    country_code = country_code.lower()
    return country_code in VALID_COUNTRY_CODES

def parse_country_codes(input_string):
    """
    Parses comma-separated country codes and validates them.
    Returns list of valid country codes (uppercase).
    """
    if not input_string:
        return []
    
    # Split by comma and clean
    codes = [code.strip().lower() for code in input_string.split(',')]
    
    valid_codes = []
    invalid_codes = []
    
    for code in codes:
        if validate_country_code(code):
            valid_codes.append(code.upper())
        else:
            invalid_codes.append(code)
    
    if invalid_codes:
        print(f"   ⚠️ Invalid country codes ignored: {', '.join(invalid_codes)}")
    
    return valid_codes

def validate_language_code(lang_code):
    """
    Validates if a language code is a valid ISO 639-1 code.
    """
    if not lang_code or len(lang_code) != 2:
        return False
    lang_code = lang_code.lower()
    return lang_code in VALID_LANGUAGE_CODES

def parse_language_codes(input_string):
    """
    Parses comma-separated language codes and validates them.
    Returns list of valid language codes (lowercase).
    """
    if not input_string:
        return []
    
    # Split by comma and clean
    codes = [code.strip().lower() for code in input_string.split(',')]
    
    valid_codes = []
    invalid_codes = []
    
    for code in codes:
        if validate_language_code(code):
            valid_codes.append(code.lower())
        else:
            invalid_codes.append(code)
    
    if invalid_codes:
        print(f"   ⚠️ Invalid language codes ignored: {', '.join(invalid_codes)}")
    
    return valid_codes

def get_user_configuration():
    """
    Collects all user inputs: Countries, Languages, App ID, Count, and Date Filter.
    """
    print("--- Google Play Review Scraper ---")
    
    # 1. Country Codes (can be multiple, comma-separated)
    while True:
        country_input = input(f"1. Enter Country Code(s) (e.g., us or us,gb,in) [default {DEFAULT_COUNTRY}]: ").strip()
        if not country_input:
            countries = [DEFAULT_COUNTRY.upper()]
            break
        
        countries = parse_country_codes(country_input)
        if countries:
            break
        print("   ⚠️ No valid country codes found. Please enter valid 2-letter ISO codes (e.g., 'us' or 'us,gb,in').")
    
    print(f"   ✅ Selected countries: {', '.join(countries)}")
    
    # Use first country for app search (if needed)
    search_country = countries[0].lower()

    # 2. Language Codes (can be multiple, comma-separated)
    while True:
        lang_input = input(f"2. Enter Language Code(s) (e.g., en or en,es,fr) [default {DEFAULT_LANG}]: ").strip()
        if not lang_input:
            languages = [DEFAULT_LANG.lower()]
            break
        
        languages = parse_language_codes(lang_input)
        if languages:
            break
        print("   ⚠️ No valid language codes found. Please enter valid 2-letter ISO codes (e.g., 'en' or 'en,es,fr').")
    
    print(f"   ✅ Selected languages: {', '.join(languages)}")
    
    # Use first language for app search (if needed)
    search_lang = languages[0]
    
    # 3. Get App ID
    user_input = input(f"3. Enter App Name or ID (default: Spotify): ").strip()
    target_app_id = resolve_app_id(user_input, search_country, search_lang)

    # 4. Get Count (per country)
    count_input = input(f"4. Number of reviews to fetch per country (default {DEFAULT_COUNT}): ").strip()
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

    return target_app_id, count, countries, languages, min_date

def search_apps(query, country, lang, n_hits=10):
    """
    Improved app search with better results and error handling.
    """
    try:
        # Try searching with the query
        results = search(query, lang=lang, country=country, n_hits=n_hits)
        
        # Filter out results with missing appId
        valid_results = [r for r in results if r.get('appId')]
        
        # If no results, try a broader search (remove special characters)
        if not valid_results and len(query) > 3:
            clean_query = ''.join(c for c in query if c.isalnum() or c.isspace())
            if clean_query != query:
                print(f"   Trying alternative search: '{clean_query}'...")
                try:
                    results = search(clean_query, lang=lang, country=country, n_hits=n_hits)
                    valid_results = [r for r in results if r.get('appId')]
                except:
                    pass
        
        return valid_results
    except Exception as e:
        print(f"   ⚠️ Search error: {e}")
        return []

def display_app_results(results):
    """
    Displays search results with detailed information.
    """
    if not results:
        return None
    
    print("\n" + "="*60)
    print("Search Results:")
    print("="*60)
    
    for i, app in enumerate(results, 1):
        title = app.get('title', 'Unknown')
        app_id = app.get('appId', 'N/A')
        developer = app.get('developer', 'Unknown Developer')
        score = app.get('score', 'N/A')
        installs = app.get('installs', 'N/A')
        
        # Format installs if it's a number
        if isinstance(installs, (int, float)):
            if installs >= 1_000_000_000:
                installs = f"{installs/1_000_000_000:.1f}B"
            elif installs >= 1_000_000:
                installs = f"{installs/1_000_000:.1f}M"
            elif installs >= 1_000:
                installs = f"{installs/1_000:.1f}K"
        
        print(f"\n{i}. {title}")
        print(f"   App ID: {app_id}")
        print(f"   Developer: {developer}")
        if score != 'N/A':
            print(f"   Rating: {score:.1f} ⭐" if isinstance(score, (int, float)) else f"   Rating: {score}")
        if installs != 'N/A':
            print(f"   Installs: {installs}")
    
    print("="*60)
    return results

def resolve_app_id(user_input, country, lang):
    """
    Resolves app name to app ID with improved search and retry option.
    """
    if not user_input:
        return DEFAULT_APP_ID

    # Heuristic: If it has a dot and no spaces, it's likely an App ID
    if "." in user_input and " " not in user_input:
        print(f"   ✅ Using provided App ID: {user_input}")
        return user_input

    # Search with retry option
    while True:
        print(f"\n🔎 Searching for '{user_input}'...")
        
        # Try searching in the specified country first
        results = search_apps(user_input, country, lang, n_hits=10)
        
        # If no results, try searching in 'us' as fallback
        if not results and country.lower() != 'us':
            print(f"   No results in {country.upper()}, trying US market...")
            results = search_apps(user_input, 'us', lang, n_hits=10)
        
        if not results:
            print("\n❌ No apps found.")
            retry = input("   Would you like to try a different search term? (y/n) [y]: ").strip().lower()
            if retry in ['', 'y', 'yes']:
                user_input = input("   Enter new search term: ").strip()
                if not user_input:
                    print("   Using default: Spotify")
                    return DEFAULT_APP_ID
                continue
            else:
                print("   Using default: Spotify")
                return DEFAULT_APP_ID
        
        # Display results with details
        display_app_results(results)
        
        # Get user selection
        print(f"\nOptions:")
        print(f"  • Enter number (1-{len(results)}) to select an app")
        print(f"  • Enter 'r' or 'retry' to search again")
        print(f"  • Enter 'q' or 'quit' to use default (Spotify)")
        
        choice = input("\nYour choice: ").strip().lower()
        
        # Retry option
        if choice in ['r', 'retry']:
            user_input = input("   Enter new search term: ").strip()
            if not user_input:
                print("   Using default: Spotify")
                return DEFAULT_APP_ID
            continue
        
        # Quit option
        if choice in ['q', 'quit', '']:
            print("   Using default: Spotify")
            return DEFAULT_APP_ID
        
        # Try to parse as number
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                selected_app = results[idx]
                print(f"\n✅ Selected: {selected_app.get('title', 'Unknown')}")
                print(f"   App ID: {selected_app.get('appId')}")
                return selected_app.get('appId')
            else:
                print(f"   ⚠️ Invalid number. Please enter 1-{len(results)}")
                continue
        except ValueError:
            print("   ⚠️ Invalid input. Please enter a number, 'r' to retry, or 'q' to quit.")
            continue
    
    # Fallback (should never reach here)
    return DEFAULT_APP_ID

def fetch_reviews(app_id, count, country, lang):
    """
    Fetches reviews for a single country and language combination.
    Returns list of review dictionaries with country and language info added.
    """
    if not app_id:
        print("❌ Error: Invalid App ID (None). Cannot fetch reviews.")
        return []
        
    print(f"   Fetching from {country} ({lang})...", end=" ")

    try:
        result, continuation_token = reviews(
            app_id,
            lang=lang,             
            country=country.lower(),          
            sort=Sort.NEWEST,      
            count=count
        )
        
        # Add country and language information to each review
        for review in result:
            review['country'] = country.upper()
            review['language'] = lang.upper()
        
        print(f"✅ {len(result)} reviews")
        return result
    except Exception as e:
        print(f"❌ Failed: {e}")
        return []

def fetch_reviews_multiple_countries_languages(app_id, count, countries, languages):
    """
    Fetches reviews from multiple countries and languages, combining all combinations.
    """
    if not app_id:
        print("❌ Error: Invalid App ID (None). Cannot fetch reviews.")
        return []
    
    print(f"\n🚀 Starting scrape for {app_id}...")
    total_combinations = len(countries) * len(languages)
    print(f"   Target: {count} reviews per combination")
    print(f"   Countries: {', '.join(countries)} ({len(countries)} countries)")
    print(f"   Languages: {', '.join(languages)} ({len(languages)} languages)")
    print(f"   Total combinations: {total_combinations}\n")
    
    all_reviews = []
    
    for country in countries:
        for lang in languages:
            country_reviews = fetch_reviews(app_id, count, country, lang)
            all_reviews.extend(country_reviews)
            time.sleep(0.5)  # Small delay between requests to avoid rate limiting
    
    print(f"\n✅ Total reviews fetched: {len(all_reviews)} from {total_combinations} country/language combinations")
    return all_reviews

def process_data(raw_data, min_date=None):
    if not raw_data:
        return None

    df = pd.DataFrame(raw_data)

    # Basic cleanup - include 'country' and 'language' if they exist
    selected_cols = ['content', 'score', 'at', 'thumbsUpCount', 'reviewId', 'appVersion', 'country', 'language']
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
    
    # Ensure country column exists (fallback for single country scrapes)
    if 'country' not in df_clean.columns:
        df_clean['country'] = 'UNKNOWN'
    
    # Ensure language column exists (fallback for single language scrapes)
    if 'language' not in df_clean.columns:
        df_clean['language'] = 'UNKNOWN'

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
        app_id, count, countries, languages, min_date = get_user_configuration()
        
        # Fetch reviews from all country/language combinations
        total_combinations = len(countries) * len(languages)
        if total_combinations == 1:
            # Single country and single language
            raw_reviews = fetch_reviews(app_id, count, countries[0], languages[0])
        else:
            # Multiple countries and/or languages
            raw_reviews = fetch_reviews_multiple_countries_languages(app_id, count, countries, languages)
        
        df_reviews = process_data(raw_reviews, min_date)

        if df_reviews is not None and not df_reviews.empty:
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            # Create filename with country/language info if multiple
            if total_combinations == 1:
                filename = os.path.join(output_dir, f"{app_id}_reviews.csv")
            else:
                countries_str = "_".join(countries).lower()
                languages_str = "_".join(languages).lower()
                filename = os.path.join(output_dir, f"{app_id}_{countries_str}_{languages_str}_reviews.csv")
            
            df_reviews.to_csv(filename, index=False)
            
            print(f"\n💾 Data saved to: {filename}")
            print("-" * 30)
            print(f"Total Reviews: {len(df_reviews)}")
            if 'country' in df_reviews.columns:
                country_counts = df_reviews['country'].value_counts()
                print(f"By Country:")
                for country, count in country_counts.items():
                    print(f"  {country}: {count}")
            if 'language' in df_reviews.columns:
                lang_counts = df_reviews['language'].value_counts()
                print(f"By Language:")
                for lang, count in lang_counts.items():
                    print(f"  {lang}: {count}")
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