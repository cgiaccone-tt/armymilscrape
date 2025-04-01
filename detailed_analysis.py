import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from urllib.parse import urlparse, parse_qs
import re
from datetime import datetime
import os
from config import RESULTS_DIR_ABS
import sys

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

def print_section(title):
    print(f"\n{'='*20} {title} {'='*20}")

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

# 1. Detailed Keyword Analysis
print_section("Detailed Keyword Analysis")

# Create keyword groups
dei_keywords = {
    'Diversity': ['diversity', 'diverse', 'representation', 'cultural', 'multicultural'],
    'Equity': ['equity', 'equal opportunity', 'equal employment', 'equality', 'fairness'],
    'Inclusion': ['inclusion', 'inclusive', 'accessibility', 'accommodation'],
    'Demographics': ['race', 'ethnicity', 'gender', 'black', 'african american', 'hispanic', 'asian', 'native american', 'latino', 'latina'],
    'Military Status': ['veterans', 'veteran', 'active duty', 'reserve', 'national guard', 'service member', 'service members', 'military family', 'military families'],
    'Protected Classes': ['disability', 'disabilities', 'transgender', 'lgbtq', 'lgbtq+', 'sexual orientation', 'religion'],
    'Issues': ['harassment', 'discrimination', 'prejudice', 'systemic', 'bias']
}

# Analyze keyword co-occurrence
keyword_pairs = defaultdict(int)
keyword_groups = defaultdict(int)

for keywords in df['keywords_found'].dropna().str.split(','):
    keywords = [k.strip() for k in keywords]
    
    # Count keyword group occurrences
    for group, terms in dei_keywords.items():
        if any(term in keywords for term in terms):
            keyword_groups[group] += 1
    
    # Count keyword co-occurrences
    for i, k1 in enumerate(keywords):
        for k2 in keywords[i+1:]:
            pair = tuple(sorted([k1.strip(), k2.strip()]))
            keyword_pairs[pair] += 1

print("\nKeyword Group Distribution:")
for group, count in sorted(keyword_groups.items(), key=lambda x: x[1], reverse=True):
    total = len(df)
    percentage = (count / total) * 100
    print(f"{group}: {count} occurrences ({percentage:.1f}% of pages)")

print("\nTop Keyword Co-occurrences:")
top_pairs = sorted(keyword_pairs.items(), key=lambda x: x[1], reverse=True)[:10]
for (k1, k2), count in top_pairs:
    total = len(df)
    percentage = (count / total) * 100
    print(f"'{k1}' + '{k2}': {count} times ({percentage:.1f}% of pages)")

# 2. Content Analysis
print_section("Content Analysis")

# Analyze URL structure
def analyze_url_depth(url):
    path = urlparse(url).path
    return len([x for x in path.split('/') if x])

df['url_depth'] = df['url'].apply(analyze_url_depth)

print("\nURL Depth Distribution:")
depth_dist = df['url_depth'].value_counts().sort_index()
for depth, count in depth_dist.items():
    print(f"Depth {depth}: {count} pages")

# Content age analysis
df['last_modified'] = pd.to_datetime(df['last_modified'], errors='coerce')
df['age_days'] = (pd.Timestamp.now() - df['last_modified']).dt.days

age_bins = [0, 7, 30, 90, 180, 365, float('inf')]
age_labels = ['Last week', 'Last month', '1-3 months', '3-6 months', '6-12 months', 'Over 1 year']
df['age_group'] = pd.cut(df['age_days'], bins=age_bins, labels=age_labels)

print("\nContent Age Distribution:")
age_dist = df['age_group'].value_counts().sort_index()
for age, count in age_dist.items():
    total = len(df)
    percentage = (count / total) * 100
    print(f"{age}: {count} pages ({percentage:.1f}%)")

# 3. Keyword Context Analysis
print_section("Keyword Context Analysis")

# Analyze context around keywords
def get_keyword_context(row, keyword, window=50):
    if pd.isna(row['page_content']):
        return None
    content = row['page_content'].lower()
    keyword_pos = content.find(keyword.lower())
    if keyword_pos == -1:
        return None
    start = max(0, keyword_pos - window)
    end = min(len(content), keyword_pos + len(keyword) + window)
    return f"...{content[start:end]}..."

# Get contexts for top keywords
top_keywords = [k for k, _ in Counter(
    [k.strip() for keywords in df['keywords_found'].dropna().str.split(',') for k in keywords]
).most_common(5)]

print("\nTop Keywords Context Examples:")
for keyword in top_keywords:
    print(f"\nContexts for '{keyword}':")
    contexts = []
    for _, row in df.iterrows():
        if pd.isna(row['keywords_found']):
            continue
        if keyword in row['keywords_found']:
            context = get_keyword_context(row, keyword)
            if context:
                contexts.append((row['url'], context))
                if len(contexts) >= 2:  # Get 2 examples per keyword
                    break
    for url, context in contexts:
        print(f"\nURL: {url}")
        print(f"Context: {context}")

# Save detailed analysis
print_section("Saving Analysis")
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = os.path.join(RESULTS_DIR_ABS, f'detailed_analysis_{timestamp}.txt')

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("=== Army.mil Content Analysis Report ===\n\n")
    f.write(f"Analysis Date: {datetime.now()}\n")
    f.write(f"Total Pages Analyzed: {len(df)}\n\n")
    
    f.write("=== Keyword Groups ===\n")
    for group, count in sorted(keyword_groups.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(df)) * 100
        f.write(f"{group}: {count} ({percentage:.1f}%)\n")
    
    f.write("\n=== Top Co-occurring Keywords ===\n")
    for (k1, k2), count in top_pairs:
        percentage = (count / len(df)) * 100
        f.write(f"'{k1}' + '{k2}': {count} ({percentage:.1f}%)\n")
    
    f.write("\n=== Content Age Distribution ===\n")
    for age, count in age_dist.items():
        percentage = (count / len(df)) * 100
        f.write(f"{age}: {count} ({percentage:.1f}%)\n")

print(f"\nDetailed analysis saved to: {output_file}")
