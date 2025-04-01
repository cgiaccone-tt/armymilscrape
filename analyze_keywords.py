import sys
import os
import pandas as pd
from collections import Counter
import re
import json
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

if __name__ == "__main__":
    # Get and read the latest results file
    results_file = get_latest_results_file()
    print(f"Loading results from {os.path.basename(results_file)}...")
    df = pd.read_excel(results_file)

    # Overall statistics
    total_pages = len(df['url'].unique())
    print(f"\nAnalysis of {total_pages} unique pages:")
    print(f"Pages with relevant keywords: {len(df)}")

    # Keyword frequency analysis
    print("\nKeyword Frequencies:")
    keyword_stats = analyze_keywords(df)
    print(keyword_stats.to_string(index=False))

    # Detailed context for top keywords
    print("\nTop 3 Keywords Context Examples:")
    for keyword in keyword_stats['Keyword'][:3]:
        print(f"\nContexts for '{keyword}':")
        contexts = find_keyword_context(df, keyword)[:2]  # Show 2 examples per keyword
        for ctx in contexts:
            print(f"\nURL: {ctx['url']}")
            print(f"Title: {ctx['title']}")
            print(f"Context: {ctx['context']}\n")
