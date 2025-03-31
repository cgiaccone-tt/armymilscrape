import pandas as pd
from collections import Counter
import re

def analyze_keywords(df):
    # Initialize counter for keywords
    keyword_counter = Counter()

    # Count occurrences of each keyword
    for keywords in df['keywords_found']:
        if isinstance(keywords, str):
            for keyword in keywords.split(','):
                keyword_counter[keyword.strip()] += 1

    # Convert to DataFrame for better display
    results = pd.DataFrame(keyword_counter.most_common(), columns=['Keyword', 'Occurrences'])
    results['Percentage'] = (results['Occurrences'] / len(df) * 100).round(1)

    return results

def find_keyword_context(df, keyword, context_words=50):
    contexts = []
    for _, row in df.iterrows():
        if isinstance(row['keywords_found'], str) and keyword in row['keywords_found']:
            content = row['page_content']
            # Find all instances of the keyword
            for match in re.finditer(r'\b' + re.escape(keyword) + r'\b', content, re.IGNORECASE):
                start = max(0, match.start() - context_words)
                end = min(len(content), match.end() + context_words)
                context = content[start:end].strip()
                contexts.append({
                    'url': row['url'],
                    'title': row['title'],
                    'context': f"...{context}..."
                })
    return contexts

# Read the CSV file
print("Loading results...")
df = pd.read_csv('army_results.csv')

# Overall statistics
print(f"\nAnalysis of {len(df)} articles:")
print(f"Total pages processed: 100")
print(f"Pages with relevant keywords: {len(df)}")
print(f"Hit rate: {(len(df) / 100 * 100):.1f}%")

# Keyword frequency analysis
print("\nKeyword Frequencies:")
keyword_stats = analyze_keywords(df)
print(keyword_stats.to_string(index=False))

# Find most common multi-word phrases
print("\nTop 5 most common multi-word keywords:")
multi_word_keywords = keyword_stats[keyword_stats['Keyword'].str.contains(' ')].head()
print(multi_word_keywords.to_string(index=False))

# Find most common single-word keywords
print("\nTop 5 most common single-word keywords:")
single_word_keywords = keyword_stats[~keyword_stats['Keyword'].str.contains(' ')].head()
print(single_word_keywords.to_string(index=False))

# Sample contexts for top keywords
print("\nSample contexts for top keywords:")
for keyword in keyword_stats.head()['Keyword']:
    contexts = find_keyword_context(df, keyword)
    if contexts:
        print(f"\nContexts for '{keyword}':")
        for ctx in contexts[:2]:  # Show first 2 contexts for each keyword
            print(f"\nTitle: {ctx['title']}")
            print(f"Context: {ctx['context']}")
            print(f"URL: {ctx['url']}")
