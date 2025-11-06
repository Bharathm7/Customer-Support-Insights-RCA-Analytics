# rca_pareto.py
# Performs Pareto analysis on issue types and outputs a CSV with cumulative percentages.
# Also creates a simple 5-Whys template CSV for the top issues.
# Run: python rca_pareto.py
# Outputs: pareto_issue_type.csv, five_whys_template.csv

import pandas as pd

def pareto_issues(tickets_path='/CSI/data/cleaned_support_tickets.csv', out_path='/CSI/data/pareto_issue_type.csv'):
    tickets = pd.read_csv(tickets_path)
    counts = tickets['issue_type'].value_counts().rename_axis('issue_type').reset_index(name='count')
    counts = counts.sort_values(by='count', ascending=False)
    counts['cum_count'] = counts['count'].cumsum()
    counts['cum_pct'] = counts['cum_count'] / counts['count'].sum() * 100
    counts.to_csv(out_path, index=False)
    print(f'Wrote pareto to {out_path}')
    return counts

def five_whys_template(counts, out_path='/CSI/data/five_whys_template.csv'):
    top = counts.head(5)['issue_type'].tolist()
    rows = []
    for issue in top:
        rows.append({
            'issue_type': issue,
            'why_1': '',
            'why_2': '',
            'why_3': '',
            'why_4': '',
            'why_5': '',
            'recommended_action': ''
        })
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    print(f'Wrote 5-Whys template to {out_path}')
    return df

if __name__ == '__main__':
    counts = pareto_issues()
    five_whys_template(counts)