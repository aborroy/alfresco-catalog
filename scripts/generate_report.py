#!/usr/bin/env python3
"""
GitHub Traffic Report Generator
Creates a professional HTML report with charts for management
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import base64
from io import BytesIO

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
except ImportError:
    print("Please install matplotlib: pip install matplotlib")
    exit(1)

# Configuration
DATA_DIR = Path('traffic-data')
REPORT_DIR = Path('reports')
REPORT_DIR.mkdir(exist_ok=True)

def load_data():
    """Load traffic data from CSV files"""
    views_path = DATA_DIR / 'views.csv'
    clones_path = DATA_DIR / 'clones.csv'
    
    if not views_path.exists():
        raise FileNotFoundError("No traffic data found. Run the collector first.")
    
    views_df = pd.read_csv(views_path)
    views_df['timestamp'] = pd.to_datetime(views_df['timestamp'])
    
    clones_df = None
    if clones_path.exists():
        clones_df = pd.read_csv(clones_path)
        clones_df['timestamp'] = pd.to_datetime(clones_df['timestamp'])
    
    return views_df, clones_df

def filter_by_period(df, days=30):
    """Filter dataframe to last N days"""
    if df is None or df.empty:
        return df
    cutoff_date = pd.Timestamp(datetime.now() - timedelta(days=days), tz='UTC')
    return df[df['timestamp'] >= cutoff_date]

def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string"""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

def create_views_chart(df, period_days):
    """Create page views chart"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(df['timestamp'], df['count'], marker='o', linewidth=2, 
            markersize=4, label='Total Views', color='#2563eb')
    ax.plot(df['timestamp'], df['uniques'], marker='s', linewidth=2, 
            markersize=4, label='Unique Visitors', color='#dc2626')
    
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title(f'Page Views - Last {period_days} Days', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, period_days // 10)))
    plt.xticks(rotation=45, ha='right')
    
    fig.tight_layout()
    return fig_to_base64(fig)

def create_summary_chart(df, period_days):
    """Create summary bar chart"""
    total_views = df['count'].sum()
    total_uniques = df['uniques'].sum()
    avg_daily_views = df['count'].mean()
    avg_daily_uniques = df['uniques'].mean()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Total counts
    categories = ['Total Views', 'Unique Visitors']
    values = [total_views, total_uniques]
    colors = ['#2563eb', '#dc2626']
    
    bars1 = ax1.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax1.set_title(f'Total Traffic ({period_days} Days)', fontsize=13, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Daily averages
    categories = ['Avg Daily Views', 'Avg Daily Uniques']
    values = [avg_daily_views, avg_daily_uniques]
    
    bars2 = ax2.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax2.set_title('Daily Averages', fontsize=13, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Add value labels on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    fig.tight_layout()
    return fig_to_base64(fig)

def create_trend_chart(df, period_days):
    """Create weekly trend chart"""
    df_copy = df.copy()
    df_copy['week'] = df_copy['timestamp'].dt.to_period('W')
    
    weekly = df_copy.groupby('week').agg({
        'count': 'sum',
        'uniques': 'sum'
    }).reset_index()
    
    weekly['week_str'] = weekly['week'].astype(str)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(weekly))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], weekly['count'], width, 
                   label='Total Views', color='#2563eb', alpha=0.8, edgecolor='black')
    bars2 = ax.bar([i + width/2 for i in x], weekly['uniques'], width,
                   label='Unique Visitors', color='#dc2626', alpha=0.8, edgecolor='black')
    
    ax.set_xlabel('Week', fontsize=12, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title(f'Weekly Traffic Trend', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(weekly['week_str'], rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    fig.tight_layout()
    return fig_to_base64(fig)

def get_top_referrers():
    """Get most recent referrers data"""
    referrer_files = sorted(DATA_DIR.glob('referrers_*.json'), reverse=True)
    if not referrer_files:
        return []
    
    with open(referrer_files[0], 'r') as f:
        referrers = json.load(f)
    
    return referrers[:10]  # Top 10

def get_top_paths():
    """Get most recent paths data"""
    path_files = sorted(DATA_DIR.glob('paths_*.json'), reverse=True)
    if not path_files:
        return []
    
    with open(path_files[0], 'r') as f:
        paths = json.load(f)
    
    return paths[:10]  # Top 10

def calculate_growth(df, period_days):
    """Calculate growth percentage"""
    if len(df) < 2:
        return None, None
    
    # Split into two halves
    mid_point = len(df) // 2
    first_half = df.iloc[:mid_point]
    second_half = df.iloc[mid_point:]
    
    first_avg = first_half['count'].mean()
    second_avg = second_half['count'].mean()
    
    if first_avg == 0:
        return None, None
    
    views_growth = ((second_avg - first_avg) / first_avg) * 100
    
    first_uniques = first_half['uniques'].mean()
    second_uniques = second_half['uniques'].mean()
    
    uniques_growth = ((second_uniques - first_uniques) / first_uniques) * 100 if first_uniques > 0 else None
    
    return views_growth, uniques_growth

def generate_html_report(period_days=30):
    """Generate complete HTML report"""
    
    # Load and filter data
    views_df, clones_df = load_data()
    views_df = filter_by_period(views_df, period_days)
    
    if views_df.empty:
        raise ValueError(f"No data available for the last {period_days} days")
    
    # Calculate metrics
    total_views = views_df['count'].sum()
    total_uniques = views_df['uniques'].sum()
    avg_daily_views = views_df['count'].mean()
    avg_daily_uniques = views_df['uniques'].mean()
    max_daily_views = views_df['count'].max()
    max_daily_uniques = views_df['uniques'].max()
    
    views_growth, uniques_growth = calculate_growth(views_df, period_days)
    
    # Generate charts
    views_chart = create_views_chart(views_df, period_days)
    summary_chart = create_summary_chart(views_df, period_days)
    trend_chart = create_trend_chart(views_df, period_days)
    
    # Get top pages and referrers
    top_paths = get_top_paths()
    top_referrers = get_top_referrers()
    
    # Generate report date range
    start_date = views_df['timestamp'].min().strftime('%B %d, %Y')
    end_date = views_df['timestamp'].max().strftime('%B %d, %Y')
    report_date = datetime.now().strftime('%B %d, %Y')
    
    # Create HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alfresco Catalog - Traffic Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background-color: #f9fafb;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .header {{
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 32px;
            color: #111827;
            margin-bottom: 8px;
        }}
        
        .subtitle {{
            font-size: 16px;
            color: #6b7280;
        }}
        
        .report-info {{
            background-color: #eff6ff;
            border-left: 4px solid #2563eb;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .report-info p {{
            margin: 5px 0;
            font-size: 14px;
            color: #1e40af;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .metric-card.blue {{
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        }}
        
        .metric-card.red {{
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
        }}
        
        .metric-card.green {{
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
        }}
        
        .metric-card.purple {{
            background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
        }}
        
        .metric-label {{
            font-size: 13px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
        }}
        
        .metric-subvalue {{
            font-size: 14px;
            opacity: 0.85;
            margin-top: 5px;
        }}
        
        .section {{
            margin: 40px 0;
        }}
        
        h2 {{
            font-size: 24px;
            color: #111827;
            margin-bottom: 20px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }}
        
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        
        th {{
            background-color: #f3f4f6;
            color: #374151;
            font-weight: 600;
            text-align: left;
            padding: 12px;
            border-bottom: 2px solid #e5e7eb;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        tr:hover {{
            background-color: #f9fafb;
        }}
        
        .path-link {{
            color: #2563eb;
            text-decoration: none;
            font-family: monospace;
            font-size: 13px;
        }}
        
        .path-link:hover {{
            text-decoration: underline;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 13px;
        }}
        
        .growth {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
        }}
        
        .growth.positive {{
            background-color: #d1fae5;
            color: #047857;
        }}
        
        .growth.negative {{
            background-color: #fee2e2;
            color: #991b1b;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Alfresco Catalog Traffic Report</h1>
            <p class="subtitle">GitHub Pages Analytics</p>
        </div>
        
        <div class="report-info">
            <p><strong>Report Period:</strong> {start_date} to {end_date} ({period_days} days)</p>
            <p><strong>Report Generated:</strong> {report_date}</p>
            <p><strong>Site URL:</strong> <a href="https://alfrescolabs.github.io/alfresco-addons-catalog/" target="_blank">https://alfrescolabs.github.io/alfresco-addons-catalog/</a></p>
        </div>
        
        <div class="section">
            <h2>📈 Key Metrics</h2>
            <div class="metrics-grid">
                <div class="metric-card blue">
                    <div class="metric-label">Total Page Views</div>
                    <div class="metric-value">{total_views:,}</div>
                    {f'<div class="growth positive">↑ {views_growth:.1f}%</div>' if views_growth and views_growth > 0 else f'<div class="growth negative">↓ {abs(views_growth):.1f}%</div>' if views_growth and views_growth < 0 else ''}
                </div>
                
                <div class="metric-card red">
                    <div class="metric-label">Unique Visitors</div>
                    <div class="metric-value">{total_uniques:,}</div>
                    {f'<div class="growth positive">↑ {uniques_growth:.1f}%</div>' if uniques_growth and uniques_growth > 0 else f'<div class="growth negative">↓ {abs(uniques_growth):.1f}%</div>' if uniques_growth and uniques_growth < 0 else ''}
                </div>
                
                <div class="metric-card green">
                    <div class="metric-label">Avg Daily Views</div>
                    <div class="metric-value">{avg_daily_views:.1f}</div>
                    <div class="metric-subvalue">Max: {max_daily_views} views/day</div>
                </div>
                
                <div class="metric-card purple">
                    <div class="metric-label">Avg Daily Uniques</div>
                    <div class="metric-value">{avg_daily_uniques:.1f}</div>
                    <div class="metric-subvalue">Max: {max_daily_uniques} visitors/day</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Traffic Overview</h2>
            <div class="chart-container">
                <img src="data:image/png;base64,{views_chart}" alt="Page Views Chart">
            </div>
        </div>
        
        <div class="section">
            <h2>📉 Summary Statistics</h2>
            <div class="chart-container">
                <img src="data:image/png;base64,{summary_chart}" alt="Summary Chart">
            </div>
        </div>
        
        <div class="section">
            <h2>📅 Weekly Trends</h2>
            <div class="chart-container">
                <img src="data:image/png;base64,{trend_chart}" alt="Weekly Trend Chart">
            </div>
        </div>
"""
    
    # Add top pages if available
    if top_paths:
        html += """
        <div class="section">
            <h2>🔝 Most Popular Pages</h2>
            <table>
                <thead>
                    <tr>
                        <th>Page Path</th>
                        <th style="text-align: right;">Total Views</th>
                        <th style="text-align: right;">Unique Visitors</th>
                    </tr>
                </thead>
                <tbody>
"""
        for path in top_paths:
            html += f"""
                    <tr>
                        <td><a href="https://alfrescolabs.github.io/alfresco-addons-catalog{path['path']}" class="path-link" target="_blank">{path['path']}</a></td>
                        <td style="text-align: right;"><strong>{path['count']:,}</strong></td>
                        <td style="text-align: right;">{path['uniques']:,}</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </div>
"""
    
    # Add top referrers if available
    if top_referrers:
        html += """
        <div class="section">
            <h2>🔗 Top Traffic Sources</h2>
            <table>
                <thead>
                    <tr>
                        <th>Referrer</th>
                        <th style="text-align: right;">Total Views</th>
                        <th style="text-align: right;">Unique Visitors</th>
                    </tr>
                </thead>
                <tbody>
"""
        for ref in top_referrers:
            html += f"""
                    <tr>
                        <td><a href="https://{ref['referrer']}" target="_blank">{ref['referrer']}</a></td>
                        <td style="text-align: right;"><strong>{ref['count']:,}</strong></td>
                        <td style="text-align: right;">{ref['uniques']:,}</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </div>
"""
    
    html += """
        <div class="footer">
            <p>Generated automatically from GitHub Traffic API data</p>
            <p>This report can be regenerated at any time with updated data</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate traffic report')
    parser.add_argument('--days', type=int, default=30, 
                       help='Number of days to include in report (default: 30)')
    parser.add_argument('--output', type=str, 
                       help='Output filename (default: traffic-report-YYYYMMDD.html)')
    
    args = parser.parse_args()
    
    print(f"Generating traffic report for last {args.days} days...")
    
    try:
        html = generate_html_report(args.days)
        
        if args.output:
            output_file = REPORT_DIR / args.output
        else:
            timestamp = datetime.now().strftime('%Y%m%d')
            output_file = REPORT_DIR / f'traffic-report-{timestamp}.html'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Report generated successfully!")
        print(f"📄 Saved to: {output_file}")
        print(f"\nOpen the file in your browser to view the report.")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        exit(1)

if __name__ == '__main__':
    main()