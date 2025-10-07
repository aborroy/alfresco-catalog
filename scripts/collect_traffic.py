#!/usr/bin/env python3
"""
GitHub Traffic Stats Collector
Collects traffic data from GitHub API and stores it locally
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import pandas as pd

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
REPO_OWNER = os.environ.get('REPO_OWNER')
REPO_NAME = os.environ.get('REPO_NAME')
BASE_URL = 'https://api.github.com'

# Data directory
DATA_DIR = Path('traffic-data')
DATA_DIR.mkdir(exist_ok=True)

def get_headers():
    """Return headers for GitHub API requests"""
    return {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

def fetch_views():
    """Fetch page views data"""
    url = f'{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/traffic/views'
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

def fetch_clones():
    """Fetch git clones data"""
    url = f'{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/traffic/clones'
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

def fetch_paths():
    """Fetch popular paths data"""
    url = f'{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/traffic/popular/paths'
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

def fetch_referrers():
    """Fetch referrers data"""
    url = f'{BASE_URL}/repos/{REPO_OWNER}/{REPO_NAME}/traffic/popular/referrers'
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()

def save_time_series_data(data, filename):
    """Save time series data (views/clones) to CSV, merging with existing data"""
    csv_path = DATA_DIR / filename
    
    # Convert new data to DataFrame
    if 'views' in data or 'clones' in data:
        key = 'views' if 'views' in data else 'clones'
        new_df = pd.DataFrame(data[key])
        
        # Load existing data if available
        if csv_path.exists():
            existing_df = pd.read_csv(csv_path)
            # Combine and remove duplicates based on timestamp
            combined_df = pd.concat([existing_df, new_df])
            combined_df = combined_df.drop_duplicates(subset=['timestamp'], keep='last')
            combined_df = combined_df.sort_values('timestamp')
        else:
            combined_df = new_df
        
        # Save to CSV
        combined_df.to_csv(csv_path, index=False)
        print(f"Saved {len(combined_df)} records to {filename}")

def save_snapshot_data(data, prefix):
    """Save snapshot data (paths/referrers) with timestamp"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    json_path = DATA_DIR / f'{prefix}_{timestamp}.json'
    
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved snapshot to {json_path.name}")

def main():
    """Main execution function"""
    print(f"Collecting traffic stats for {REPO_OWNER}/{REPO_NAME}...")
    
    try:
        # Fetch and save views
        print("\nFetching page views...")
        views_data = fetch_views()
        save_time_series_data(views_data, 'views.csv')
        print(f"Total views (last 14 days): {views_data.get('count', 0)}")
        print(f"Unique visitors: {views_data.get('uniques', 0)}")
        
        # Fetch and save clones
        print("\nFetching git clones...")
        clones_data = fetch_clones()
        save_time_series_data(clones_data, 'clones.csv')
        print(f"Total clones (last 14 days): {clones_data.get('count', 0)}")
        
        # Fetch and save popular paths
        print("\nFetching popular paths...")
        paths_data = fetch_paths()
        save_snapshot_data(paths_data, 'paths')
        print(f"Top paths: {len(paths_data)}")
        
        # Fetch and save referrers
        print("\nFetching referrers...")
        referrers_data = fetch_referrers()
        save_snapshot_data(referrers_data, 'referrers')
        print(f"Top referrers: {len(referrers_data)}")
        
        # Save summary
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'views_total': views_data.get('count', 0),
            'views_unique': views_data.get('uniques', 0),
            'clones_total': clones_data.get('count', 0),
            'clones_unique': clones_data.get('uniques', 0),
            'top_paths': len(paths_data),
            'top_referrers': len(referrers_data)
        }
        
        summary_path = DATA_DIR / 'latest_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\nTraffic stats collection completed successfully!")
        
    except requests.exceptions.HTTPError as e:
        print(f"Error fetching data: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

if __name__ == '__main__':
    main()