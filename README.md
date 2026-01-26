# AI-Powered Google Play Store Review Analyzer 🚀

An automated tool that scrapes user reviews from the Google Play Store and uses Google Gemini AI to analyze feedback, classify issues (Bugs vs. Features), and generate a tactical Product Roadmap.

## ✨ Features

*   **Multi-Market Scraping**: Fetch reviews from multiple countries and languages simultaneously
*   **Country & Language Validation**: Validates ISO country codes and language codes
*   **AI-Powered Analysis**: Uses Google Gemini 2.5 Pro to classify reviews into "Bug Reports", "Feature Requests", or "General Feedback"
*   **Smart Prioritization**: Automatically assigns High/Medium/Low priority based on sentiment and urgency
*   **Tactical Roadmap Generation**: Creates a solution-oriented Product Roadmap with specific engineering tasks
*   **Interruptible Processing**: Press Ctrl+C to stop analysis; saves partial results and generates roadmap if ≥200 reviews analyzed
*   **Enhanced App Search**: Improved search with detailed results, retry options, and fallback mechanisms
*   **Cost Estimation**: Tracks estimated API costs for transparency
*   **Rich Metadata**: Output includes country and language information for each review

## 📋 Prerequisites

*   Python 3.7+
*   Google Gemini API Key ([Get one here](https://aistudio.google.com/))

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rishabhmodi910/PM-Playstore-Review-Analyzer.git
    cd PM-Playstore-Review-Analyzer
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your Google Gemini API Key:**
    
    **Option 1: Environment Variable (Recommended)**
    ```bash
    export GEMINI_API_KEY="your_actual_api_key_here"
    ```
    
    **Option 2: Interactive Input**
    The script will prompt you to enter the API key if not set as an environment variable.

## 💻 Usage

Run the main scraper script:

```bash
python review_scraper.py
```

### Interactive Menu Options

1.  **Fetch New Reviews**: Search for an app and download reviews from multiple countries/languages
2.  **Analyze Existing CSV**: Run AI analysis on previously fetched data
3.  **Fetch & Analyze**: Run the end-to-end pipeline (scrape → analyze → roadmap)

### Example Workflow

```
========================================
   GOOGLE PLAY STORE TOOLKIT
========================================
1. Fetch New Reviews
2. Analyze Existing CSV
3. Fetch & Analyze (End-to-End)

Select option (1, 2, or 3): 3

--- Google Play Review Scraper ---
1. Enter Country Code(s) (e.g., us or us,gb,in) [default us]: us,gb,de,fr
   ✅ Selected countries: US, GB, DE, FR

2. Enter Language Code(s) (e.g., en or en,es,fr) [default en]: en,es,fr
   ✅ Selected languages: en, es, fr

3. Enter App Name or ID (default: Spotify): Spotify
   🔎 Searching for 'Spotify'...
   [Shows app selection menu]

4. Number of reviews to fetch per country (default 1000): 500

5. Filter reviews after date (YYYY-MM-DD) [Enter to skip]: 

🔑 API Key Required
   Get your key from: https://aistudio.google.com/
   Enter your Gemini API key: [your_key]

✅ Using model: models/gemini-2.5-pro
🤖 AI Analysis in progress... (Batch processing)
   💡 Tip: Press Ctrl+C to interrupt and save partial results (requires ≥200 reviews for roadmap)
```

## 📊 Output Files

Results are saved in the `outputs/` directory:

### 1. Raw Review Data
*   **Single country/language**: `{app_id}_reviews.csv`
*   **Multiple countries/languages**: `{app_id}_{countries}_{languages}_reviews.csv`
*   **Columns**: `review_text`, `rating`, `date`, `votes`, `version`, `country`, `language`

### 2. Analyzed Dataset
*   `{app_id}_reviews_analyzed_ai.csv`
*   **Additional columns**: `category` (Bug Report/Feature Request/General Feedback), `priority` (High/Medium/Low)

### 3. Product Roadmap
*   `{app_id}_roadmap.md`
*   **Sections**:
    *   The "Must-Fix" List (Immediate Engineering Priority)
    *   Feature Enhancements (The "Quick Wins")
    *   Strategic Feature Bets (Complex Requests)
    *   Discarded Suggestions (Out of Scope)

## 🌍 Supported Countries & Languages

### Countries
The script supports 150+ ISO 3166-1 alpha-2 country codes. Common examples:
- `us`, `gb`, `in`, `ca`, `au`, `de`, `fr`, `jp`, `kr`, `cn`, `br`, `mx`, `es`, `it`, `nl`, `se`, `no`, `dk`, `fi`, `pl`, `ru`, `tr`, `sa`, `ae`, `sg`, `my`, `th`, `ph`, `id`, `vn`, `nz`, `za`, and more...

### Languages
The script supports 70+ ISO 639-1 language codes. Common examples:
- `en`, `es`, `fr`, `de`, `it`, `pt`, `ru`, `ja`, `ko`, `zh`, `ar`, `hi`, `nl`, `pl`, `tr`, `sv`, `da`, `fi`, `no`, `cs`, `hu`, `ro`, `el`, `th`, `vi`, `id`, `ms`, `tl`, and more...

### Multi-Selection Examples
```bash
# Multiple countries, single language
Countries: us,gb,de,fr
Language: en

# Single country, multiple languages
Countries: us
Languages: en,es,fr

# Multiple countries and languages (creates all combinations)
Countries: us,gb
Languages: en,es
# Results: US+EN, US+ES, GB+EN, GB+ES (4 combinations)
```

## 🛑 Interruption Handling

You can interrupt the analysis process at any time by pressing `Ctrl+C`:

*   **If ≥200 reviews analyzed**: Partial results are saved and roadmap is generated
*   **If <200 reviews analyzed**: Partial results are saved, but roadmap is **not** generated (shows informative message)

Example:
```
⚠️ Analysis interrupted by user.
   Processed 350 out of 1000 reviews.
   ✅ Sufficient reviews (350 ≥ 200) - roadmap will be generated.

💾 Analysis saved to: ...
🗺️  Generating Product Roadmap (based on 350 analyzed reviews)...
```

## 🔍 Enhanced App Search

The improved search function provides:
*   Up to 10 search results (instead of 5)
*   Detailed information: App title, ID, developer, rating, install count
*   Retry option: Enter `r` to search again with different terms
*   Fallback search: Automatically tries US market if no results in selected country
*   Alternative search: Cleans special characters and retries if needed

## 💰 Cost Estimation

The script estimates API costs based on:
*   **Model**: Gemini 2.5 Pro
*   **Pricing**: $1.25 per 1M input tokens, $5.00 per 1M output tokens
*   **Assumptions**: ~60 input tokens and ~10 output tokens per review

Example: Analyzing 1,000 reviews ≈ $0.11

## 📁 Project Structure

```
PM-Playstore-Review-Analyzer/
├── review_scraper.py          # Main scraper script
├── playstore_analysis.py       # AI analysis and roadmap generation
├── test_gemini_models.py      # API key and model testing utility
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── PRD.md                      # Product Requirements Document
├── LICENSE                     # MIT License
└── outputs/                    # Generated files (gitignored)
    ├── {app_id}_reviews.csv
    ├── {app_id}_reviews_analyzed_ai.csv
    └── {app_id}_roadmap.md
```

## 🔧 Configuration

### Default Settings
*   **Default App**: Spotify (`com.spotify.music`)
*   **Default Country**: US (`us`)
*   **Default Language**: English (`en`)
*   **Default Review Count**: 1000 per country
*   **Batch Size**: 10 reviews per API call
*   **Minimum Reviews for Roadmap**: 200

### Environment Variables
```bash
export GEMINI_API_KEY="your_api_key_here"
```

## 🐛 Troubleshooting

### Common Issues

**1. "No apps found" during search**
- Try a different search term
- Check if the app exists in the selected country
- Use the App ID directly (e.g., `com.spotify.music`)

**2. "API key is required"**
- Set `GEMINI_API_KEY` environment variable, or
- Enter it when prompted by the script

**3. "Too few reviews analyzed"**
- Ensure you have at least 200 reviews in your dataset
- If interrupted, wait until ≥200 reviews are processed

**4. Invalid country/language codes**
- Use 2-letter ISO codes only
- Check the supported codes list above
- Invalid codes are automatically ignored with a warning

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

*   [google-play-scraper](https://github.com/JoMingyu/google-play-scraper) - Play Store scraping library
*   [Google Gemini AI](https://deepmind.google/technologies/gemini/) - AI analysis capabilities

## 📧 Contact

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for Product Managers and Developers**
