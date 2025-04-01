import pandas as pd
from collections import Counter
from urllib.parse import urlparse
import re
from datetime import datetime
import os
import sys
from config import RESULTS_DIR_ABS

# Force unbuffered output
if sys.stdout.isatty():
    sys.stdout.reconfigure(encoding='utf-8')
else:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

def clean_text_for_display(text):
    """Clean text for terminal display."""
    if not isinstance(text, str):
        return str(text)
    # Replace problematic characters with ASCII alternatives
    replacements = {
        '✓': '[OK]',
        '∞': 'inf',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '–': '-',
        '—': '-',
        '…': '...'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def get_latest_results_file():
    """Get the most recent results file from the results directory."""
    files = []
    for f in os.listdir(RESULTS_DIR_ABS):
        if f.startswith('army_results_') and f.endswith('.xlsx'):
            path = os.path.join(RESULTS_DIR_ABS, f)
            files.append((os.path.getmtime(path), path))
    if not files:
        raise FileNotFoundError("No results files found")
    return max(files)[1]

# Read the latest results
results_file = get_latest_results_file()
print(f"Loading results from {os.path.basename(results_file)}...")
df = pd.read_excel(results_file)

print(f"\nTotal unique pages analyzed: {len(df)}")

# 1. Domain Analysis
print("\n=== Domain Distribution ===")
df['domain'] = df['url'].apply(lambda x: urlparse(x).netloc)
domain_counts = df['domain'].value_counts()
print(clean_text_for_display(str(domain_counts)))

# 2. Keyword Analysis
print("\n=== Most Common Keywords ===")
all_keywords = []
for keywords in df['keywords_found'].dropna().str.split(','):
    all_keywords.extend([k.strip() for k in keywords])
keyword_counts = Counter(all_keywords)
print(clean_text_for_display(str(pd.Series(keyword_counts).sort_values(ascending=False).head(10))))

# 3. Content Type Analysis
print("\n=== Content Type Distribution ===")
def get_content_type(url):
    url_lower = url.lower()
    if '/news/' in url_lower:
        return 'News'
    elif '/publications/' in url_lower or '/pubs/' in url_lower:
        return 'Publications'
    elif '/photos/' in url_lower or '/images/' in url_lower:
        return 'Media'
    elif '/features/' in url_lower:
        return 'Features'
    elif '/leaders/' in url_lower or '/leadership/' in url_lower:
        return 'Leadership'
    elif '/careers/' in url_lower or '/jobs/' in url_lower:
        return 'Careers'
    elif '/about/' in url_lower:
        return 'About'
    else:
        return 'Other'

df['content_type'] = df['url'].apply(get_content_type)
print(clean_text_for_display(str(df['content_type'].value_counts())))

# 4. Time Analysis
print("\n=== Timestamp Analysis ===")
df['timestamp'] = pd.to_datetime(df['timestamp'])
print("First page scraped:", df['timestamp'].min())
print("Last page scraped:", df['timestamp'].max())
print("Total scraping duration:", clean_text_for_display(str(df['timestamp'].max() - df['timestamp'].min())))

# 5. URL Path Analysis
print("\n=== Common URL Patterns ===")
df['path'] = df['url'].apply(lambda x: urlparse(x).path)
path_patterns = Counter()
for path in df['path']:
    parts = [p for p in path.split('/') if p]
    if parts:
        path_patterns[parts[0]] += 1

print("\nTop URL path patterns:")
for pattern, count in path_patterns.most_common(10):
    print(f"/{pattern}/: {count} pages")

# 6. Last Modified Analysis
print("\n=== Content Age Analysis ===")
df['last_modified'] = pd.to_datetime(df['last_modified'], errors='coerce')
df['age_days'] = (pd.Timestamp.now() - df['last_modified']).dt.days

age_bins = [0, 30, 90, 180, 365, float('inf')]
age_labels = ['Last 30 days', '1-3 months', '3-6 months', '6-12 months', 'Over 1 year']
df['age_group'] = pd.cut(df['age_days'], bins=age_bins, labels=age_labels)
print("\nContent age distribution:")
print(clean_text_for_display(str(df['age_group'].value_counts().sort_index())))

# Save detailed analysis to file
with open('analysis_results.txt', 'w', encoding='utf-8') as f:
    f.write(f"Analysis Results - {datetime.now()}\n")
    f.write("=" * 50 + "\n\n")
    f.write("=== Domain Distribution ===\n")
    f.write(clean_text_for_display(str(domain_counts)) + "\n\n")
    f.write("=== Most Common Keywords ===\n")
    f.write(clean_text_for_display(str(pd.Series(keyword_counts).sort_values(ascending=False).head(10))) + "\n\n")
    f.write("=== Content Type Distribution ===\n")
    f.write(clean_text_for_display(str(df['content_type'].value_counts())) + "\n\n")
    f.write("=== URL Path Analysis ===\n")
    f.write("Top URL path patterns:\n")
    for pattern, count in path_patterns.most_common(10):
        f.write(f"/{pattern}/: {count} pages\n")
    f.write("\n\nDetailed URL List:\n")
    for idx, row in df.iterrows():
        f.write(f"\n{row['url']}\nKeywords: {row['keywords_found']}\n")
