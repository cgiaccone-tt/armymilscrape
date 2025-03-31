import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from urllib.parse import urlparse, parse_qs
import re
from datetime import datetime

def print_section(title):
    print(f"\n{'='*20} {title} {'='*20}")

# Read the results
df = pd.read_csv('army_results.csv')

# 1. Detailed Keyword Analysis
print_section("Detailed Keyword Analysis")

# Create keyword groups
dei_keywords = {
    'Diversity': ['diversity', 'diverse', 'representation', 'cultural', 'multicultural'],
    'Equity': ['equity', 'equal opportunity', 'equal employment', 'equality', 'fairness'],
    'Inclusion': ['inclusion', 'inclusive', 'accessibility', 'accommodation'],
    'Demographics': ['race', 'ethnicity', 'gender', 'black', 'african american', 'hispanic', 'asian', 'native american'],
    'Military Status': ['veterans', 'veteran', 'active duty', 'reserve', 'national guard', 'service member', 'service members'],
    'Protected Classes': ['disability', 'disabilities', 'transgender', 'sexual orientation', 'religion'],
    'Issues': ['harassment', 'discrimination', 'prejudice', 'systemic', 'bias']
}

# Analyze keyword co-occurrence
keyword_pairs = defaultdict(int)
keyword_groups = defaultdict(int)

for keywords in df['keywords_found'].str.split(','):
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
    print(f"{group}: {count} occurrences")

print("\nTop Keyword Co-occurrences:")
top_pairs = sorted(keyword_pairs.items(), key=lambda x: x[1], reverse=True)[:10]
for (k1, k2), count in top_pairs:
    print(f"'{k1}' + '{k2}': {count} times")

# 2. Content Analysis
print_section("Content Analysis")

# Analyze publication types
pub_types = defaultdict(int)
for url in df[df['url'].str.contains('ProductMaps')]['url']:
    match = re.search(r'PubForm/([^/\.]+)', url)
    if match:
        pub_types[match.group(1)] += 1

print("\nPublication Types:")
for pub_type, count in sorted(pub_types.items(), key=lambda x: x[1], reverse=True):
    print(f"{pub_type}: {count}")

# 3. Temporal Analysis
print_section("Temporal Analysis")

df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
df['minute'] = df['timestamp'].dt.minute

# Calculate processing rates
time_diffs = df['timestamp'].diff()
avg_processing_time = time_diffs.mean().total_seconds()
pages_per_minute = 60 / avg_processing_time

print(f"\nProcessing Speed Analysis:")
print(f"Average time between pages: {avg_processing_time:.2f} seconds")
print(f"Pages processed per minute: {pages_per_minute:.2f}")

# 4. URL Structure Analysis
print_section("URL Structure Analysis")

def analyze_url_depth(url):
    path = urlparse(url).path
    return len([x for x in path.split('/') if x])

df['url_depth'] = df['url'].apply(analyze_url_depth)

print("\nURL Depth Distribution:")
depth_dist = df['url_depth'].value_counts().sort_index()
for depth, count in depth_dist.items():
    print(f"Depth {depth}: {count} pages")

# 5. Content Relevance Analysis
print_section("Content Relevance Analysis")

# Calculate keyword density
df['keyword_count'] = df['keywords_found'].str.split(',').str.len()
df['relevance_score'] = df['keyword_count'] / df['keyword_count'].max()

print("\nRelevance Statistics:")
print(f"Average keywords per page: {df['keyword_count'].mean():.2f}")
print(f"Maximum keywords on a single page: {df['keyword_count'].max()}")
print(f"Pages with 5+ keywords: {len(df[df['keyword_count'] >= 5])}")

# Find most relevant pages
print("\nMost Relevant Pages (by keyword count):")
most_relevant = df.nlargest(5, 'keyword_count')[['url', 'keyword_count', 'keywords_found']]
for _, row in most_relevant.iterrows():
    print(f"\nURL: {row['url']}")
    print(f"Keywords ({row['keyword_count']}): {row['keywords_found']}")

# 6. Domain Coverage Analysis
print_section("Domain Coverage Analysis")

df['subdomain'] = df['url'].apply(lambda x: urlparse(x).netloc.split('.')[0])
print("\nSubdomain Distribution:")
print(df['subdomain'].value_counts())

# Save detailed results
with open('detailed_analysis_results.txt', 'w') as f:
    f.write(f"Detailed Analysis Results - {datetime.now()}\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("1. Most Relevant Pages\n")
    f.write("-" * 40 + "\n")
    for _, row in most_relevant.iterrows():
        f.write(f"\nURL: {row['url']}\n")
        f.write(f"Keywords: {row['keywords_found']}\n")
    
    f.write("\n2. Keyword Co-occurrence Patterns\n")
    f.write("-" * 40 + "\n")
    for (k1, k2), count in top_pairs:
        f.write(f"'{k1}' + '{k2}': {count} times\n")
    
    f.write("\n3. Publication Type Analysis\n")
    f.write("-" * 40 + "\n")
    for pub_type, count in sorted(pub_types.items(), key=lambda x: x[1], reverse=True):
        f.write(f"{pub_type}: {count}\n")
    
    f.write("\n4. Full URL List by Relevance Score\n")
    f.write("-" * 40 + "\n")
    for _, row in df.sort_values('relevance_score', ascending=False).iterrows():
        f.write(f"\nScore: {row['relevance_score']:.2f}\n")
        f.write(f"URL: {row['url']}\n")
        f.write(f"Keywords: {row['keywords_found']}\n")
