# Product Requirements Document (PRD): Play Store Review Analyzer 🚀

## 1. Executive Summary
**Product Name:** Play Store Review Analyzer
**Version:** 1.0
**Status:** Active

This tool automates the extraction and analysis of Google Play Store reviews. By leveraging Google Gemini AI, it transforms raw user feedback into actionable product insights, classifying issues and generating strategic roadmaps.

## 2. Problem Statement
Product Managers and Developers struggle to manually parse thousands of user reviews to identify critical bugs and feature requests. This manual process is time-consuming, prone to bias, and often results in missed opportunities for product improvement.

## 3. Goals & Objectives
*   **Efficiency:** Reduce time spent on review analysis by 90%.
*   **Accuracy:** Use LLMs to understand sentiment and context better than keyword matching.
*   **Actionability:** Automatically generate a prioritized roadmap and bug list.

## 4. Target Audience
*   Product Managers
*   App Developers
*   Customer Support Leads
*   Data Analysts

## 5. Functional Requirements (Features)
*   **Multi-Market Data Ingestion:** Scrape reviews from multiple countries and languages simultaneously (supports 150+ countries, 70+ languages). Users can specify comma-separated country/language codes (e.g., "us,gb,de" or "en,es,fr").
*   **Country & Language Validation:** Validates ISO 3166-1 alpha-2 country codes and ISO 639-1 language codes, automatically filtering invalid entries.
*   **Date Filtering:** Optional date filter to analyze reviews after a specific date (YYYY-MM-DD format).
*   **Enhanced App Search:** Intelligent app discovery with detailed results (title, developer, rating, install count), retry options, fallback to US market, and alternative search strategies.
*   **AI Classification:** Classify feedback into "Bug Report", "Feature Request", or "General Feedback" using Google Gemini 2.5 Pro.
*   **Smart Prioritization:** Assign High/Medium/Low priority based on urgency and sentiment.
*   **Batch Processing:** Processes reviews in batches of 10 per API call for efficiency and cost optimization (~90% cost reduction vs. individual calls).
*   **Interruptible Processing:** Users can interrupt analysis (Ctrl+C) at any time; partial results are saved and roadmap is generated if ≥200 reviews analyzed.
*   **Strategic Output:** Generate a Markdown-formatted Product Roadmap document with tactical engineering tasks.
*   **Cost Tracking:** Real-time API usage cost estimation with transparency (displays estimated cost before/after processing).
*   **Rich Metadata:** Output includes country and language information for each review, enabling market-specific analysis.

## 6. Technical Specifications
### Prerequisites
*   Python 3.7+
*   Google Gemini API Key ([Get one here](https://aistudio.google.com/))

### Core Technologies
*   **Language:** Python 3.7+
*   **Scraping:** `google-play-scraper`
*   **AI Model:** Google Gemini 2.5 Pro via `google-generativeai`
*   **Data Handling:** `pandas`

### Performance & Configuration
*   **Batch Size:** 10 reviews per API call (configurable)
*   **Rate Limiting:** 1-second delay between batches to prevent API throttling
*   **Minimum Reviews for Roadmap:** 200 analyzed reviews required for roadmap generation
*   **Cost Estimate:** ~$0.11 per 1,000 reviews (Gemini 2.5 Pro pricing)

## 7. User Flows (Usage)
**Primary Actor:** Product Manager

The tool provides an interactive menu with three options:

**Scenario 1: Fetch New Reviews Only**
1.  Run `python review_scraper.py`.
2.  Select **Option 1: Fetch New Reviews**.
3.  Enter Country Code(s) (e.g., "us" or "us,gb,in") - supports multiple comma-separated codes.
4.  Enter Language Code(s) (e.g., "en" or "en,es,fr") - supports multiple comma-separated codes.
5.  Enter App Name or ID (e.g., "Spotify") - enhanced search with detailed results and retry options.
6.  Specify number of reviews per country (default: 1000).
7.  Optionally filter reviews after a specific date (YYYY-MM-DD).
8.  System scrapes and saves raw data to CSV.

**Scenario 2: Analyze Existing CSV**
1.  Run `python review_scraper.py`.
2.  Select **Option 2: Analyze Existing CSV**.
3.  Choose a previously scraped file from the `outputs/` directory.
4.  Enter Gemini API key (if not set as environment variable).
5.  System performs AI analysis on local data and generates roadmap (if ≥200 reviews).

**Scenario 3: End-to-End Analysis (Fetch & Analyze)**
1.  Run `python review_scraper.py`.
2.  Select **Option 3: Fetch & Analyze**.
3.  Follow steps 3-7 from Scenario 1.
4.  Enter Gemini API key (if not set as environment variable).
5.  System scrapes data -> Runs AI Analysis -> Generates Roadmap automatically.

## 8. Deliverables (Output Artifacts)
The system generates the following artifacts in the `outputs/` directory:

### 1. Raw Review Data
*   **Single country/language:** `{app_id}_reviews.csv`
*   **Multiple countries/languages:** `{app_id}_{countries}_{languages}_reviews.csv`
*   **Columns:** `review_text`, `rating`, `date`, `votes`, `version`, `country`, `language`
*   **Note:** Country and language columns are automatically added for multi-market scrapes.

### 2. Analyzed Dataset
*   **Filename:** `{app_id}_reviews_analyzed_ai.csv` (or `{app_id}_{countries}_{languages}_reviews_analyzed_ai.csv`)
*   **Additional Columns:** `category` (Bug Report/Feature Request/General Feedback), `priority` (High/Medium/Low)
*   **Note:** If analysis is interrupted, partial results are saved with the number of reviews processed.

### 3. Strategic Product Roadmap
*   **Filename:** `{app_id}_roadmap.md` (or `{app_id}_{countries}_{languages}_roadmap.md`)
*   **Sections:**
    *   The "Must-Fix" List (Immediate Engineering Priority)
    *   Feature Enhancements (The "Quick Wins")
    *   Strategic Feature Bets (Complex Requests)
    *   Discarded Suggestions (Out of Scope)
*   **Note:** Roadmap is only generated if ≥200 reviews are analyzed. Partial analysis (<200 reviews) saves categorized data but skips roadmap generation.

## 9. Constraints & Limitations
*   **Minimum Review Threshold:** Roadmap generation requires ≥200 analyzed reviews. Below this threshold, only categorized data is provided.
*   **API Costs:** Costs scale with review volume (~$0.11 per 1,000 reviews). Large-scale analysis may incur significant costs.
*   **Rate Limiting:** Built-in delays prevent throttling, but Google's API rate limits still apply for very large operations.
*   **AI Accuracy:** While Gemini 2.5 Pro is highly accurate, manual validation of classifications is recommended for critical decisions.
*   **Data Privacy:** Review data is stored locally. Users must comply with GDPR/privacy regulations when analyzing EU user reviews.

## 10. Future Roadmap (v2.0)
*   Sentiment Analysis Visualization (Charts and Graphs).
*   Support for Apple App Store.
*   Slack/Jira Integration for bug reporting.
*   Customizable batch sizes and rate limiting.
*   Advanced filtering options (by rating, date range, keyword).

---
*License: MIT*