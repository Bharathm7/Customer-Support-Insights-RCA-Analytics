"""data_cleaning.py
Reads mock CSVs (support_tickets.csv, call_logs.csv, feedback.csv),
performs basic cleaning & feature engineering, and writes cleaned CSVs.

Run: python data_cleaning.py
Outputs: cleaned_support_tickets.csv, cleaned_call_logs.csv, cleaned_feedback.csv
"""
import pandas as pd 
from datetime import datetime


def call_logs(path_in = "/Users/bharathmahesh/Desktop/CSI/Data/call_logs.csv",path_out="/Users/bharathmahesh/Desktop/CSI/Data/cleaned_call_logs.csv"):
	df = pd.read_csv(path_in, parse_dates=['call_date'])
	df.columns = [c.strip().lower() for c in df.columns]
	df['duration_min'] = pd.to_numeric(df['duration_min'], errors='coerce').fillna(0).astype(int)
	df['month'] = df['call_date'].dt.to_period('M').astype(str)
	df.to_csv(path_out, index=False)
	print(f'Wrote {path_out} ({len(df)} rows)')
	return df


def clean_support_tickets(path_in='/Users/bharathmahesh/Desktop/CSI/Data/support_tickets.csv', path_out='/Users/bharathmahesh/Desktop/CSI/Data/cleaned_support_tickets.csv'):
    df = pd.read_csv(path_in, parse_dates=['created_date'])
    # Standardize column names
    df.columns = [c.strip().lower() for c in df.columns]
    # Fix priority to categorical with ordering
    df['priority'] = pd.Categorical(df['priority'], categories=['Low','Medium','High'], ordered=True)
    # Convert resolution_time_hrs to numeric and filter negatives
    df['resolution_time_hrs'] = pd.to_numeric(df['resolution_time_hrs'], errors='coerce').fillna(0).astype(int)
    df = df[df['resolution_time_hrs'] >= 0]
    # Create month field for trend analysis
    df['month'] = df['created_date'].dt.to_period('M').astype(str)
    # Flag repeat issues per customer (simple heuristic)
    df['customer_ticket_count'] = df.groupby('customer_id')['ticket_id'].transform('count')
    df['is_repeat_customer'] = (df['customer_ticket_count'] > 1).astype(int)
    df.to_csv(path_out, index=False)
    print(f'Wrote {path_out} ({len(df)} rows)')
    return df

def clean_feedback(path_in='/Users/bharathmahesh/Desktop/CSI/Data/feedback.csv', path_out='/Users/bharathmahesh/Desktop/CSI/Data/cleaned_feedback.csv'):
    df = pd.read_csv(path_in)
    df.columns = [c.strip().lower() for c in df.columns]
    df['csat'] = pd.to_numeric(df['csat'], errors='coerce').fillna(0).astype(int)
    df['nps'] = pd.to_numeric(df['nps'], errors='coerce').fillna(0).astype(int)
    df.to_csv(path_out, index=False)
    print(f'Wrote {path_out} ({len(df)} rows)')
    return df

call_logs()
clean_support_tickets()
clean_feedback()

