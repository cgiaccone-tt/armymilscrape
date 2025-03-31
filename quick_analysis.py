import pandas as pd
from collections import Counter
from urllib.parse import urlparse
import re
from datetime import datetime

# Read the results
df = pd.read_csv('army_results.csv')

# 1. Domain Analysis
print("\n=== Domain Distribution ===")
df['domain'] = df['url'].apply(lambda x: urlparse(x).netloc)
domain_counts = df['domain'].value_counts()
print(domain_counts)

# 2. Keyword Analysis
print("\n=== Most Common Keywords ===")
all_keywords = []
for keywords in df['keywords_found'].str.split(','):
    all_keywords.extend(keywords)
keyword_counts = Counter(all_keywords)
print(pd.Series(keyword_counts).sort_values(ascending=False))

# 3. Content Type Analysis
print("\n=== Content Type Distribution ===")
def get_content_type(url):
    if '/news/' in url.lower():
        return 'News'
    elif '/publications/' in url.lower() or 'pubs' in url.lower():
        return 'Publications'
    elif '/photos/' in url.lower():
        return 'Photos'
    elif '/features/' in url.lower():
        return 'Features'
    elif '/leaders/' in url.lower():
        return 'Leadership'
    else:
        return 'Other'

df['content_type'] = df['url'].apply(get_content_type)
print(df['content_type'].value_counts())

# 4. Time Analysis
print("\n=== Timestamp Analysis ===")
df['timestamp'] = pd.to_datetime(df['timestamp'])
print("First page scraped:", df['timestamp'].min())
print("Last page scraped:", df['timestamp'].max())
print("Total scraping duration:", df['timestamp'].max() - df['timestamp'].min())

# 5. URL Path Analysis
print("\n=== Common URL Patterns ===")
df['path'] = df['url'].apply(lambda x: urlparse(x).path)
path_patterns = Counter([p.split('/')[1] if len(p.split('/')) > 1 else 'root' for p in df['path']])
print(pd.Series(path_patterns).sort_values(ascending=False))

# 6. Summary Statistics
print("\n=== Summary Statistics ===")
print(f"Total unique pages with keywords: {len(df)}")
print(f"Average keywords per page: {len(all_keywords) / len(df):.2f}")
print(f"Number of unique keywords found: {len(set(all_keywords))}")

# Save detailed analysis to file
with open('analysis_results.txt', 'w') as f:
    f.write(f"Analysis Results - {datetime.now()}\n")
    f.write("=" * 50 + "\n\n")
    f.write("=== Domain Distribution ===\n")
    f.write(str(domain_counts) + "\n\n")
    f.write("=== Most Common Keywords ===\n")
    f.write(str(pd.Series(keyword_counts).sort_values(ascending=False)) + "\n\n")
    f.write("=== Content Type Distribution ===\n")
    f.write(str(df['content_type'].value_counts()) + "\n\n")
    f.write("=== URL Path Analysis ===\n")
    f.write(str(pd.Series(path_patterns).sort_values(ascending=False)) + "\n\n")
    f.write("\nDetailed URL List:\n")
    for idx, row in df.iterrows():
        f.write(f"\n{row['url']}\nKeywords: {row['keywords_found']}\n")
