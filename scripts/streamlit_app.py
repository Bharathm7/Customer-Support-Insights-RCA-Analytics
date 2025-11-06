import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

st.set_page_config(layout="wide", page_title="Customer Support Insights & RCA (Plotly)", initial_sidebar_state="expanded")

st.title("Customer Support Insights & RCA Analytics (Mock Data)")

@st.cache_data
def load_cleaned_data(base_path='Data'):
    tickets = pd.read_csv(f'{base_path}/cleaned_support_tickets.csv', parse_dates=['created_date'])
    calls = pd.read_csv(f'{base_path}/cleaned_call_logs.csv', parse_dates=['call_date'])
    feedback = pd.read_csv(f'{base_path}/cleaned_feedback.csv')
    return tickets, calls, feedback

tickets, calls, feedback = load_cleaned_data()

st.sidebar.header("Filters")
months = ['All'] + sorted(tickets['month'].unique().tolist())
selected_month = st.sidebar.selectbox("Month", months)

if selected_month != 'All':
    tickets = tickets[tickets['month'] == selected_month]
    calls = calls[calls['month'] == selected_month]

# KPI calculations
aht = calls['duration_min'].mean() if len(calls) else 0
total_tickets = len(tickets)
resolved_tickets = len(tickets[tickets['status'] == 'Resolved'])
fcr_proxy = (resolved_tickets / total_tickets * 100) if total_tickets else 0
csat = feedback['csat'].mean() if len(feedback) else 0
nps = feedback['nps'].mean() if len(feedback) else 0
avg_resolution_hrs = tickets['resolution_time_hrs'].mean() if len(tickets) else 0

# KPI display
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("AHT (min)", f"{aht:.2f}")
col2.metric("FCR proxy (%)", f"{fcr_proxy:.2f}")
col3.metric("CSAT (1-5)", f"{csat:.2f}")
col4.metric("NPS (0-10)", f"{nps:.2f}")
col5.metric("Avg Resolution (hrs)", f"{avg_resolution_hrs:.2f}")

st.markdown("---")

# Pareto chart for issue types using Plotly
st.header("Pareto: Issue Types (Interactive)")
issue_counts = tickets['issue_type'].value_counts().reset_index()
issue_counts.columns = ['issue_type', 'count']
issue_counts = issue_counts.sort_values(by='count', ascending=False).reset_index(drop=True)
issue_counts['cum_count'] = issue_counts['count'].cumsum()
issue_counts['cum_pct'] = issue_counts['cum_count'] / issue_counts['count'].sum() * 100

fig = go.Figure()
fig.add_trace(go.Bar(
    x=issue_counts['issue_type'],
    y=issue_counts['count'],
    name='Issue Count',
    yaxis='y1',
    hovertemplate='%{x}<br>Count: %{y}<extra></extra>'
))
fig.add_trace(go.Scatter(
    x=issue_counts['issue_type'],
    y=issue_counts['cum_pct'],
    name='Cumulative %',
    mode='lines+markers',
    line=dict(width=3, dash='solid'),
    yaxis='y2',
    hovertemplate='%{x}<br>Cumulative: %{y:.1f}%<extra></extra>'
))

fig.update_layout(
    title="Pareto Chart - Issue Types",
    xaxis=dict(title="Issue Type"),
    yaxis=dict(title="Count", side='left', showgrid=False),
    yaxis2=dict(title="Cumulative %", overlaying='y', side='right', range=[0,110], tickformat=',.0f'),
    legend=dict(x=0.75, y=1.15, orientation='h'),
    bargap=0.3,
    template='plotly_white',
    height=450
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(issue_counts.style.format({'count':'{:.0f}','cum_pct':'{:.1f}%'}))

st.markdown("---")

# Monthly trends using Plotly Express (interactive)
st.header("Monthly Trends (Interactive)")
tickets_by_month = tickets.groupby('month').agg(ticket_count=('ticket_id','count'),
                                                avg_resolution_hrs=('resolution_time_hrs','mean')).reset_index()
calls_by_month = calls.groupby('month').agg(call_count=('call_id','count'),
                                            avg_duration_min=('duration_min','mean')).reset_index()

if not tickets_by_month.empty:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=tickets_by_month['month'],
        y=tickets_by_month['ticket_count'],
        name='Ticket Count',
        mode='lines+markers',
        hovertemplate='%{x}<br>Tickets: %{y}<extra></extra>'
    ))
    fig2.add_trace(go.Scatter(
        x=tickets_by_month['month'],
        y=tickets_by_month['avg_resolution_hrs'],
        name='Avg Resolution (hrs)',
        mode='lines+markers',
        yaxis='y2',
        hovertemplate='%{x}<br>Avg Res (hrs): %{y:.2f}<extra></extra>'
    ))
    fig2.update_layout(
        title="Tickets & Avg Resolution by Month",
        xaxis=dict(title="Month"),
        yaxis=dict(title="Ticket Count", side='left'),
        yaxis2=dict(title="Avg Resolution (hrs)", overlaying='y', side='right'),
        template='plotly_white',
        height=450
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No monthly ticket data available.")

st.markdown("---")

# Agent performance table
st.header("Agent Performance")
agent_perf = tickets.groupby('agent').agg(tickets_handled=('ticket_id','count'),
                                          avg_res_hrs=('resolution_time_hrs','mean')).reset_index()
agent_calls = calls.groupby('agent_id').agg(calls_handled=('call_id','count'),
                                           avg_call_min=('duration_min','mean')).reset_index()
agent_perf = agent_perf.merge(agent_calls, left_on='agent', right_on='agent_id', how='left').drop(columns=['agent_id'])
st.dataframe(agent_perf.round(2))

st.markdown("---")

# Downloadable outputs (CX_Insights.xlsx and Pareto CSV)
st.header("Download Outputs")
def to_bytes_io_excel(kpis, tickets_df, calls_df, feedback_df):
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine='openpyxl') as writer:
        pd.DataFrame([kpis]).to_excel(writer, sheet_name='KPIs', index=False)
        tickets_df.to_excel(writer, sheet_name='Tickets', index=False)
        calls_df.to_excel(writer, sheet_name='Calls', index=False)
        feedback_df.to_excel(writer, sheet_name='Feedback', index=False)
    bio.seek(0)
    return bio

kpis = {
    'AHT_min': round(aht,2),
    'FCR_proxy_pct': round(fcr_proxy,2),
    'CSAT_mean': round(csat,2),
    'NPS_mean': round(nps,2),
    'Avg_resolution_hrs': round(avg_resolution_hrs,2)
}

if st.button("Export CX_Insights.xlsx"):
    bio = to_bytes_io_excel(kpis, tickets, calls, feedback)
    st.download_button("Download CX_Insights_streamlit_plotly.xlsx", bio, file_name="CX_Insights_streamlit_plotly.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Pareto CSV download
st.download_button("Download pareto_issue_type.csv", issue_counts.to_csv(index=False).encode('utf-8'), file_name='pareto_issue_type.csv')

st.markdown("### Notes")
st.markdown("- AHT is approximated from average call duration in mock data.\n- FCR is a proxy (Resolved / Total tickets) - for real FCR you'd track first-contact flags.\n- Use the 5-Whys template (generated by rca_pareto.py) to perform qualitative RCA for the top issue types.")

