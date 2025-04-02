import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
from datetime import datetime
import os
from config import RESULTS_DIR_ABS, KEYWORDS

def load_latest_results():
    """Load the most recent results file."""
    # Find the most recent xlsx file
    files = [f for f in os.listdir(RESULTS_DIR_ABS) if f.endswith('.xlsx')]
    if not files:
        print("No results files found.")
        return None
        
    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(RESULTS_DIR_ABS, x)))
    file_path = os.path.join(RESULTS_DIR_ABS, latest_file)
    print(f"\nLoading results from {latest_file}...")
    
    return pd.read_excel(file_path)

def analyze_keywords(df):
    """Analyze keyword distribution and patterns."""
    # Convert keywords string to list
    df['keyword_list'] = df['keywords'].str.split(',')
    
    # Count total occurrences of each keyword
    keyword_counts = Counter()
    for keywords in df['keyword_list']:
        keyword_counts.update([k.strip() for k in keywords])
    
    # Sort by frequency
    sorted_counts = dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True))
    
    print("\n=== Keyword Analysis ===")
    print("\nTop 20 Most Common Keywords:")
    for keyword, count in list(sorted_counts.items())[:20]:
        print(f"{keyword:<20}: {count:>5} occurrences")
    
    # Calculate percentages
    total_pages = len(df)
    print("\nKeyword Coverage (% of pages):")
    for keyword, count in sorted_counts.items():
        percentage = (count / total_pages) * 100
        if percentage > 5:  # Show only keywords appearing in more than 5% of pages
            print(f"{keyword:<20}: {percentage:>6.1f}%")
    
    return sorted_counts

def analyze_patterns(df):
    """Analyze patterns and correlations in the data."""
    print("\n=== Pattern Analysis ===")
    
    # Analyze keyword co-occurrence
    co_occurrences = Counter()
    for keywords in df['keyword_list']:
        keywords = [k.strip() for k in keywords]
        for i in range(len(keywords)):
            for j in range(i + 1, len(keywords)):
                pair = tuple(sorted([keywords[i], keywords[j]]))
                co_occurrences[pair] += 1
    
    print("\nTop 10 Keyword Co-occurrences:")
    for (kw1, kw2), count in co_occurrences.most_common(10):
        print(f"{kw1} + {kw2}: {count} pages")
    
    return co_occurrences

def main():
    # Load data
    df = load_latest_results()
    if df is None:
        return
        
    print(f"\nAnalysis of {len(df)} unique pages:")
    
    # Basic statistics
    print("\n=== Basic Statistics ===")
    print(f"Total unique pages: {len(df)}")
    print(f"Average keywords per page: {df['keywords'].str.count(',').mean() + 1:.1f}")
    
    # Analyze keywords
    keyword_counts = analyze_keywords(df)
    
    # Analyze patterns
    co_occurrences = analyze_patterns(df)
    
    print("\nAnalysis complete! Results saved to analysis_results.txt")
    
    # Save detailed results to file
    with open(os.path.join(RESULTS_DIR_ABS, 'analysis_results.txt'), 'w') as f:
        f.write(f"Analysis Results - {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("=== Basic Statistics ===\n")
        f.write(f"Total unique pages: {len(df)}\n")
        f.write(f"Average keywords per page: {df['keywords'].str.count(',').mean() + 1:.1f}\n\n")
        
        f.write("=== Keyword Distribution ===\n")
        for keyword, count in keyword_counts.items():
            percentage = (count / len(df)) * 100
            f.write(f"{keyword:<30}: {count:>5} occurrences ({percentage:>6.1f}%)\n")
        
        f.write("\n=== Keyword Co-occurrences ===\n")
        for (kw1, kw2), count in co_occurrences.most_common(20):
            f.write(f"{kw1:<20} + {kw2:<20}: {count:>5} pages\n")

if __name__ == "__main__":
    main()
