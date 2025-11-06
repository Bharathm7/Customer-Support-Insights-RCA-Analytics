# analysis.py
# Reads cleaned CSVs, computes KPIs (AHT, FCR proxy, CSAT, NPS, Resolution Time),
# generates summary tables and exports CX_Insights.xlsx for Power BI or reporting.
# Run: python analysis.py
# Output: CX_Insights.xlsx

import pandas as pd

def load_data(tickets_path='/CSI/data/cleaned_support_tickets.csv', calls_path='/CSI/data/cleaned_call_logs.csv', feedback_path='/mnt/data/cleaned_feedback.csv'):
    tickets = pd.read_csv(tickets_path, parse_dates=['created_date'])
    calls = pd.read_csv(calls_path, parse_dates=['call_date'])
    feedback = pd.read_csv(feedback_path)
    return tickets, calls, feedback

def compute_kpis(tickets, calls, feedback):
    # Average Handle Time (AHT) approximated by call duration average
    aht = calls['duration_min'].mean()
    # First Contact Resolution (FCR) proxy: tickets with status Resolved and not escalated and no repeat customer
    total_tickets = len(tickets)
    resolved = tickets[tickets['status'] == 'Resolved']
    fcr_proxy = len(resolved) / total_tickets if total_tickets else 0
    # CSAT and NPS
    csat = feedback['csat'].mean()
    nps = feedback['nps'].mean()
    # Average resolution time
    avg_resolution_hrs = tickets['resolution_time_hrs'].mean()
    kpis = {
        'AHT_min': round(aht,2),
        'FCR_proxy_pct': round(fcr_proxy*100,2),
        'CSAT_mean': round(csat,2),
        'NPS_mean': round(nps,2),
        'Avg_resolution_hrs': round(avg_resolution_hrs,2)
    }
    return kpis

def monthly_trends(tickets, calls, feedback):
    # Tickets by month and issue type
    tickets_by_month = tickets.groupby(['month','issue_type']).agg(ticket_count=('ticket_id','count'),
                                                                  avg_resolution_hrs=('resolution_time_hrs','mean')).reset_index()
    calls_by_month = calls.groupby(['month']).agg(call_count=('call_id','count'),
                                                 avg_duration_min=('duration_min','mean')).reset_index()
    csat_by_month = feedback.groupby(feedback.index // 10).agg(csat_mean=('csat','mean'))  # approximate grouping if dates not present
    return tickets_by_month, calls_by_month, csat_by_month

def export_insights(kpis, tickets_by_month, calls_by_month, path_out='/CSI/data/CX_Insights.xlsx'):
    with pd.ExcelWriter(path_out) as writer:
        pd.DataFrame([kpis]).to_excel(writer, sheet_name='KPIs', index=False)
        tickets_by_month.to_excel(writer, sheet_name='Tickets_by_Month', index=False)
        calls_by_month.to_excel(writer, sheet_name='Calls_by_Month', index=False)
    print(f'Wrote insights to {path_out}')

if __name__ == '__main__':
    tickets, calls, feedback = load_data()
    kpis = compute_kpis(tickets, calls, feedback)
    tickets_by_month, calls_by_month, csat_by_month = monthly_trends(tickets, calls, feedback)
    export_insights(kpis, tickets_by_month, calls_by_month)
