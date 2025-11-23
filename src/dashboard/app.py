"""Interactive dashboard for IUU fishing detection - Enhanced UI v2.0"""
import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config_loader import load_config
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "logs/dashboard.log")

# Initialize Dash app with custom styling
app = dash.Dash(
    __name__, 
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
)
app.title = "IUU Fishing Detection System"

# Load configuration
config = load_config()

# Load data
def load_data():
    """Load anomaly predictions"""
    try:
        predictions_path = Path("outputs/anomaly_predictions.csv")
        if not predictions_path.exists():
            logger.warning("Predictions file not found, loading sample data")
            return load_sample_data()
        
        df = pd.read_csv(predictions_path, parse_dates=['timestamp'])
        logger.info(f"Loaded {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return load_sample_data()

def load_sample_data():
    """Generate sample data for demonstration"""
    np.random.seed(42)
    n_records = 1000
    n_vessels = 20
    
    data = {
        'MMSI': np.random.choice(range(100000000, 100000000 + n_vessels), n_records),
        'timestamp': pd.date_range(start='2024-01-01', periods=n_records, freq='10min'),
        'lat': np.random.uniform(6, 22, n_records),
        'lon': np.random.uniform(68, 88, n_records),
        'supervised_score': np.random.beta(2, 5, n_records),
        'unsupervised_score': np.random.beta(2, 5, n_records),
        'ensemble_score': np.random.beta(2, 5, n_records)
    }
    
    df = pd.DataFrame(data)
    # Add some high-risk anomalies
    anomaly_indices = np.random.choice(df.index, size=int(n_records * 0.15), replace=False)
    df.loc[anomaly_indices, 'ensemble_score'] = np.random.uniform(0.7, 1.0, len(anomaly_indices))
    df.loc[anomaly_indices, 'supervised_score'] = np.random.uniform(0.7, 1.0, len(anomaly_indices))
    df.loc[anomaly_indices, 'unsupervised_score'] = np.random.uniform(0.6, 0.95, len(anomaly_indices))
    
    logger.info(f"Generated {len(df)} sample records")
    return df

def load_alert_data():
    """Load alert summary data"""
    try:
        alert_path = Path("outputs/explainability/alert_summary.csv")
        if alert_path.exists():
            return pd.read_csv(alert_path)
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading alerts: {e}")
        return pd.DataFrame()

# Custom CSS
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap']

# Color scheme
COLORS = {
    'primary': '#1e3a8a',      # Deep blue
    'secondary': '#3b82f6',    # Bright blue
    'success': '#10b981',      # Green
    'warning': '#f59e0b',      # Orange
    'danger': '#ef4444',       # Red
    'dark': '#1f2937',         # Dark gray
    'light': '#f3f4f6',        # Light gray
    'white': '#ffffff',
    'text': '#374151',
    'text-light': '#6b7280'
}

# App layout with modern design
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.Div([
                html.Img(src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTIwIDVMMzUgMTVWMjVMMjAgMzVMNSAyNVYxNUwyMCA1WiIgZmlsbD0iIzNiODJmNiIvPgo8L3N2Zz4=',
                         style={'height': '40px', 'marginRight': '15px'}),
                html.Div([
                    html.H1("IUU Fishing Detection System", 
                            style={'margin': 0, 'fontSize': '28px', 'fontWeight': '700', 
                                   'color': COLORS['white'], 'letterSpacing': '-0.5px'}),
                    html.P("AI-Powered Maritime Surveillance for Indian EEZ",
                           style={'margin': 0, 'fontSize': '14px', 'color': 'rgba(255,255,255,0.8)', 
                                  'fontWeight': '400'})
                ])
            ], style={'display': 'flex', 'alignItems': 'center'}),
            
            html.Div([
                html.Div([
                    html.Span("●", style={'color': COLORS['success'], 'fontSize': '20px', 'marginRight': '8px'}),
                    html.Span("System Active", style={'color': COLORS['white'], 'fontSize': '14px', 'fontWeight': '500'})
                ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '20px'}),
                
                html.Div([
                    html.Span("🕐", style={'marginRight': '8px'}),
                    html.Span(id='last-update', children="Just now", 
                             style={'color': COLORS['white'], 'fontSize': '14px'})
                ], style={'display': 'flex', 'alignItems': 'center'})
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
                 'maxWidth': '1400px', 'margin': '0 auto', 'padding': '0 20px'})
    ], style={'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%)',
             'padding': '20px 0', 'marginBottom': '30px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
    
    # Main container
    html.Div([
        # Control Panel
        html.Div([
            html.Div([
                html.Div([
                    html.Label("🎯 Anomaly Threshold", 
                              style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['text'],
                                    'marginBottom': '10px', 'display': 'block'}),
                    dcc.Slider(
                        id='threshold-slider',
                        min=0,
                        max=1,
                        step=0.05,
                        value=0.7,
                        marks={i/10: f'{i/10:.1f}' for i in range(0, 11, 2)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={'flex': '1', 'marginRight': '20px'}),
                
                html.Div([
                    html.Label("🚢 Select Vessel (MMSI)", 
                              style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['text'],
                                    'marginBottom': '10px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='vessel-dropdown',
                        options=[],
                        value=None,
                        placeholder="All vessels...",
                        style={'width': '100%'}
                    )
                ], style={'flex': '1', 'marginRight': '20px'}),
                
                html.Div([
                    html.Label("⚙️ Actions", 
                              style={'fontSize': '14px', 'fontWeight': '600', 'color': COLORS['text'],
                                    'marginBottom': '10px', 'display': 'block'}),
                    html.Button('🔄 Refresh Data', id='refresh-button', n_clicks=0,
                               style={'backgroundColor': COLORS['secondary'], 'color': 'white', 
                                     'padding': '10px 24px', 'border': 'none', 
                                     'borderRadius': '8px', 'cursor': 'pointer',
                                     'fontSize': '14px', 'fontWeight': '600',
                                     'boxShadow': '0 2px 4px rgba(59,130,246,0.3)',
                                     'transition': 'all 0.3s'})
                ], style={'flex': '0.8'})
            ], style={'display': 'flex', 'alignItems': 'flex-end', 'gap': '20px'})
        ], style={'backgroundColor': COLORS['white'], 'padding': '24px', 'borderRadius': '12px',
                 'marginBottom': '24px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}),
    
        # Statistics Cards
        html.Div([
            # Total Vessels Card
            html.Div([
                html.Div([
                    html.Div("🚢", style={'fontSize': '32px', 'marginBottom': '8px'}),
                    html.H2(id='total-vessels', 
                           style={'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['primary'],
                                 'margin': '0', 'lineHeight': '1'}),
                    html.P("Total Vessels", 
                          style={'fontSize': '14px', 'color': COLORS['text-light'], 'margin': '8px 0 0 0',
                                'fontWeight': '500'})
                ], style={'textAlign': 'center'})
            ], style={'flex': '1', 'backgroundColor': COLORS['white'], 'padding': '24px',
                     'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                     'border': f'2px solid {COLORS["light"]}', 'transition': 'all 0.3s'}),
            
            # Anomalies Detected Card
            html.Div([
                html.Div([
                    html.Div("⚠️", style={'fontSize': '32px', 'marginBottom': '8px'}),
                    html.H2(id='anomaly-count', 
                           style={'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['danger'],
                                 'margin': '0', 'lineHeight': '1'}),
                    html.P("Anomalies Detected", 
                          style={'fontSize': '14px', 'color': COLORS['text-light'], 'margin': '8px 0 0 0',
                                'fontWeight': '500'})
                ], style={'textAlign': 'center'})
            ], style={'flex': '1', 'backgroundColor': COLORS['white'], 'padding': '24px',
                     'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                     'border': f'2px solid {COLORS["light"]}', 'transition': 'all 0.3s'}),
            
            # Anomaly Rate Card
            html.Div([
                html.Div([
                    html.Div("📊", style={'fontSize': '32px', 'marginBottom': '8px'}),
                    html.H2(id='anomaly-rate', 
                           style={'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['warning'],
                                 'margin': '0', 'lineHeight': '1'}),
                    html.P("Anomaly Rate", 
                          style={'fontSize': '14px', 'color': COLORS['text-light'], 'margin': '8px 0 0 0',
                                'fontWeight': '500'})
                ], style={'textAlign': 'center'})
            ], style={'flex': '1', 'backgroundColor': COLORS['white'], 'padding': '24px',
                     'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                     'border': f'2px solid {COLORS["light"]}', 'transition': 'all 0.3s'}),
            
            # Average Score Card
            html.Div([
                html.Div([
                    html.Div("🎯", style={'fontSize': '32px', 'marginBottom': '8px'}),
                    html.H2(id='avg-score', 
                           style={'fontSize': '36px', 'fontWeight': '700', 'color': COLORS['secondary'],
                                 'margin': '0', 'lineHeight': '1'}),
                    html.P("Avg Anomaly Score", 
                          style={'fontSize': '14px', 'color': COLORS['text-light'], 'margin': '8px 0 0 0',
                                'fontWeight': '500'})
                ], style={'textAlign': 'center'})
            ], style={'flex': '1', 'backgroundColor': COLORS['white'], 'padding': '24px',
                     'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                     'border': f'2px solid {COLORS["light"]}', 'transition': 'all 0.3s'})
        ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '24px'}),
    
        # Main Content Grid
        html.Div([
            # Left Column - Map
            html.Div([
                html.Div([
                    html.H3("🗺️ Vessel Trajectories & Anomalies", 
                           style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['text'],
                                 'margin': '0 0 20px 0'}),
                    dcc.Graph(id='map-plot', style={'height': '600px'}, config={'displayModeBar': False})
                ], style={'backgroundColor': COLORS['white'], 'padding': '24px',
                         'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                         'height': '100%'})
            ], style={'flex': '2', 'marginRight': '20px'}),
            
            # Right Column - Charts
            html.Div([
                # Timeline Chart
                html.Div([
                    html.H3("📈 Anomaly Score Timeline", 
                           style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['text'],
                                 'margin': '0 0 16px 0'}),
                    dcc.Graph(id='timeline-plot', style={'height': '280px'}, config={'displayModeBar': False})
                ], style={'backgroundColor': COLORS['white'], 'padding': '24px',
                         'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                         'marginBottom': '20px'}),
                
                # Model Comparison Chart
                html.Div([
                    html.H3("🤖 Model Scores Comparison", 
                           style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['text'],
                                 'margin': '0 0 16px 0'}),
                    dcc.Graph(id='scores-plot', style={'height': '280px'}, config={'displayModeBar': False})
                ], style={'backgroundColor': COLORS['white'], 'padding': '24px',
                         'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'})
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'marginBottom': '24px'}),
        
        # Risk Distribution Chart
        html.Div([
            html.Div([
                html.H3("📊 Risk Level Distribution", 
                       style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['text'],
                             'margin': '0 0 16px 0'}),
                dcc.Graph(id='risk-distribution', style={'height': '300px'}, config={'displayModeBar': False})
            ], style={'flex': '1', 'backgroundColor': COLORS['white'], 'padding': '24px',
                     'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
                     'marginRight': '20px'}),
            
            html.Div([
                html.H3("🎯 Top Risk Vessels", 
                       style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['text'],
                             'margin': '0 0 16px 0'}),
                html.Div(id='top-risk-vessels')
            ], style={'flex': '1', 'backgroundColor': COLORS['white'], 'padding': '24px',
                     'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'})
        ], style={'display': 'flex', 'marginBottom': '24px'}),
        
        # Bottom Section - Anomaly Table with Export
        html.Div([
            html.Div([
                html.H3("🚨 Recent Anomalies", 
                       style={'fontSize': '18px', 'fontWeight': '600', 'color': COLORS['text'],
                             'margin': '0', 'display': 'inline-block'}),
                html.Button('📥 Export CSV', id='export-button', n_clicks=0,
                           style={'backgroundColor': COLORS['success'], 'color': 'white', 
                                 'padding': '8px 16px', 'border': 'none', 
                                 'borderRadius': '6px', 'cursor': 'pointer',
                                 'fontSize': '13px', 'fontWeight': '600',
                                 'float': 'right', 'marginTop': '-4px'})
            ], style={'marginBottom': '16px'}),
            html.Div(id='anomaly-table'),
            dcc.Download(id='download-dataframe-csv')
        ], style={'backgroundColor': COLORS['white'], 'padding': '24px',
                 'borderRadius': '12px', 'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'}),
    ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '0 20px 40px 20px'}),
    
    # Data store
    dcc.Store(id='data-store'),
    dcc.Interval(id='interval-component', interval=300*1000, n_intervals=0)  # 5 min
])

# Callbacks
@app.callback(
    [Output('data-store', 'data'),
     Output('vessel-dropdown', 'options'),
     Output('last-update', 'children')],
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_data(n_clicks, n_intervals):
    """Load and update data"""
    df = load_data()
    
    if df.empty:
        return {}, [], "No data"
    
    # Vessel options
    vessels = sorted(df['MMSI'].unique())
    vessel_options = [{'label': f'🚢 MMSI: {v}', 'value': v} for v in vessels]
    
    # Update timestamp
    from datetime import datetime
    last_update = datetime.now().strftime("%H:%M:%S")
    
    return df.to_dict('records'), vessel_options, f"Updated: {last_update}"

@app.callback(
    [Output('total-vessels', 'children'),
     Output('anomaly-count', 'children'),
     Output('anomaly-rate', 'children'),
     Output('avg-score', 'children')],
    [Input('data-store', 'data'),
     Input('threshold-slider', 'value')]
)
def update_stats(data, threshold):
    """Update statistics cards"""
    if not data:
        return "0", "0", "0%", "0.00"
    
    df = pd.DataFrame(data)
    
    total_vessels = df['MMSI'].nunique()
    anomalies = (df['ensemble_score'] >= threshold).sum()
    anomaly_rate = f"{anomalies/len(df)*100:.1f}%"
    avg_score = f"{df['ensemble_score'].mean():.3f}"
    
    return str(total_vessels), str(anomalies), anomaly_rate, avg_score

@app.callback(
    Output('map-plot', 'figure'),
    [Input('data-store', 'data'),
     Input('threshold-slider', 'value'),
     Input('vessel-dropdown', 'value')]
)
def update_map(data, threshold, selected_vessel):
    """Update map visualization"""
    if not data:
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    df = pd.DataFrame(data)
    
    # Filter by vessel if selected
    if selected_vessel:
        df = df[df['MMSI'] == selected_vessel]
    
    # Mark anomalies
    df['is_anomaly'] = df['ensemble_score'] >= threshold
    df['status'] = df['is_anomaly'].map({True: '⚠️ Anomaly', False: '✓ Normal'})
    
    # Create map with custom colors
    fig = px.scatter_mapbox(
        df,
        lat='lat',
        lon='lon',
        color='status',
        color_discrete_map={'⚠️ Anomaly': COLORS['danger'], '✓ Normal': COLORS['secondary']},
        hover_data={
            'MMSI': True,
            'timestamp': True,
            'ensemble_score': ':.3f',
            'lat': ':.4f',
            'lon': ':.4f',
            'status': False
        },
        size='ensemble_score',
        size_max=15,
        zoom=4,
        height=600
    )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": df['lat'].mean(), "lon": df['lon'].mean()},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        showlegend=True,
        legend=dict(
            title=dict(text="Status", font=dict(size=14, family='Inter')),
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=COLORS['light'],
            borderwidth=1
        ),
        font=dict(family='Inter, sans-serif', size=12)
    )
    
    return fig

@app.callback(
    Output('timeline-plot', 'figure'),
    [Input('data-store', 'data'),
     Input('vessel-dropdown', 'value'),
     Input('threshold-slider', 'value')]
)
def update_timeline(data, selected_vessel, threshold):
    """Update timeline plot"""
    if not data:
        return go.Figure()
    
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    if selected_vessel:
        df = df[df['MMSI'] == selected_vessel]
    
    fig = go.Figure()
    
    # Add threshold line
    fig.add_hline(
        y=threshold, 
        line_dash="dash", 
        line_color=COLORS['warning'],
        annotation_text=f"Threshold: {threshold}",
        annotation_position="right"
    )
    
    # Add anomaly score line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['ensemble_score'],
        mode='lines+markers',
        name='Anomaly Score',
        line=dict(color=COLORS['danger'], width=2),
        marker=dict(size=6, color=COLORS['danger']),
        fill='tozeroy',
        fillcolor='rgba(239,68,68,0.1)'
    ))
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Anomaly Score",
        hovermode='x unified',
        margin=dict(l=40, r=20, t=10, b=40),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', size=12, color=COLORS['text'])
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)', range=[0, 1])
    
    return fig

@app.callback(
    Output('scores-plot', 'figure'),
    [Input('data-store', 'data'),
     Input('vessel-dropdown', 'value')]
)
def update_scores(data, selected_vessel):
    """Update model scores comparison"""
    if not data:
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    if selected_vessel:
        df = df[df['MMSI'] == selected_vessel]
    
    # Sample data for visualization
    df_sample = df.sample(min(100, len(df)))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_sample.index,
        y=df_sample['supervised_score'],
        mode='lines',
        name='Supervised',
        line=dict(color=COLORS['secondary'], width=2),
        fill='tonexty',
        fillcolor='rgba(59,130,246,0.1)'
    ))
    fig.add_trace(go.Scatter(
        x=df_sample.index,
        y=df_sample['unsupervised_score'],
        mode='lines',
        name='Unsupervised',
        line=dict(color=COLORS['success'], width=2),
        fill='tonexty',
        fillcolor='rgba(16,185,129,0.1)'
    ))
    fig.add_trace(go.Scatter(
        x=df_sample.index,
        y=df_sample['ensemble_score'],
        mode='lines',
        name='Ensemble',
        line=dict(color=COLORS['danger'], width=3)
    ))
    
    fig.update_layout(
        xaxis_title="Sample Index",
        yaxis_title="Score",
        hovermode='x unified',
        margin=dict(l=40, r=20, t=10, b=40),
        legend=dict(orientation="h", y=1.15, x=0.5, xanchor='center'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', size=12, color=COLORS['text'])
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
    
    return fig

@app.callback(
    Output('anomaly-table', 'children'),
    [Input('data-store', 'data'),
     Input('threshold-slider', 'value')]
)
def update_anomaly_table(data, threshold):
    """Update anomaly table"""
    if not data:
        return html.Div("No data available", style={'textAlign': 'center', 'padding': '20px', 
                                                     'color': COLORS['text-light']})
    
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter anomalies
    anomalies = df[df['ensemble_score'] >= threshold].sort_values('ensemble_score', ascending=False).head(10)
    
    if len(anomalies) == 0:
        return html.Div("No anomalies detected with current threshold", 
                       style={'textAlign': 'center', 'padding': '20px', 'color': COLORS['text-light']})
    
    # Create table
    return dash_table.DataTable(
        data=anomalies[['MMSI', 'timestamp', 'ensemble_score', 'supervised_score', 
                       'unsupervised_score', 'lat', 'lon']].to_dict('records'),
        columns=[
            {'name': 'MMSI', 'id': 'MMSI'},
            {'name': 'Timestamp', 'id': 'timestamp'},
            {'name': 'Anomaly Score', 'id': 'ensemble_score', 'type': 'numeric', 'format': {'specifier': '.3f'}},
            {'name': 'Supervised', 'id': 'supervised_score', 'type': 'numeric', 'format': {'specifier': '.3f'}},
            {'name': 'Unsupervised', 'id': 'unsupervised_score', 'type': 'numeric', 'format': {'specifier': '.3f'}},
            {'name': 'Latitude', 'id': 'lat', 'type': 'numeric', 'format': {'specifier': '.4f'}},
            {'name': 'Longitude', 'id': 'lon', 'type': 'numeric', 'format': {'specifier': '.4f'}}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': 'Inter, sans-serif',
            'fontSize': '14px',
            'border': 'none'
        },
        style_header={
            'backgroundColor': COLORS['light'],
            'fontWeight': '600',
            'color': COLORS['text'],
            'borderBottom': f'2px solid {COLORS["primary"]}'
        },
        style_data={
            'backgroundColor': COLORS['white'],
            'color': COLORS['text']
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgba(0,0,0,0.02)'
            },
            {
                'if': {'column_id': 'ensemble_score', 'filter_query': '{ensemble_score} >= 0.8'},
                'backgroundColor': 'rgba(239,68,68,0.1)',
                'color': COLORS['danger'],
                'fontWeight': '600'
            }
        ],
        page_size=10
    )

@app.callback(
    Output('risk-distribution', 'figure'),
    [Input('data-store', 'data'),
     Input('threshold-slider', 'value')]
)
def update_risk_distribution(data, threshold):
    """Update risk level distribution chart"""
    if not data:
        return go.Figure()
    
    df = pd.DataFrame(data)
    
    # Classify risk levels
    def get_risk_level(score):
        if score >= 0.85:
            return 'CRITICAL'
        elif score >= threshold:
            return 'HIGH'
        elif score >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    df['risk_level'] = df['ensemble_score'].apply(get_risk_level)
    
    # Count by risk level
    risk_counts = df['risk_level'].value_counts()
    
    # Define order and colors
    risk_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    risk_colors = {
        'CRITICAL': COLORS['danger'],
        'HIGH': COLORS['warning'],
        'MEDIUM': '#fbbf24',
        'LOW': COLORS['success']
    }
    
    # Prepare data
    risk_data = pd.DataFrame({
        'Risk Level': risk_order,
        'Count': [risk_counts.get(level, 0) for level in risk_order]
    })
    
    fig = go.Figure(data=[
        go.Bar(
            x=risk_data['Risk Level'],
            y=risk_data['Count'],
            marker_color=[risk_colors[level] for level in risk_order],
            text=risk_data['Count'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        xaxis_title="Risk Level",
        yaxis_title="Number of Vessels",
        margin=dict(l=40, r=20, t=10, b=40),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', size=12, color=COLORS['text']),
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
    
    return fig

@app.callback(
    Output('top-risk-vessels', 'children'),
    [Input('data-store', 'data'),
     Input('threshold-slider', 'value')]
)
def update_top_risk_vessels(data, threshold):
    """Update top risk vessels list"""
    if not data:
        return html.Div("No data available", style={'textAlign': 'center', 'padding': '20px', 
                                                     'color': COLORS['text-light']})
    
    df = pd.DataFrame(data)
    
    # Get top risk vessels
    vessel_risk = df.groupby('MMSI').agg({
        'ensemble_score': ['max', 'mean', 'count']
    }).reset_index()
    vessel_risk.columns = ['MMSI', 'Max_Score', 'Avg_Score', 'Count']
    vessel_risk = vessel_risk.sort_values('Max_Score', ascending=False).head(5)
    
    # Create list items
    items = []
    for idx, row in vessel_risk.iterrows():
        risk_color = COLORS['danger'] if row['Max_Score'] >= 0.85 else COLORS['warning'] if row['Max_Score'] >= threshold else COLORS['success']
        
        items.append(
            html.Div([
                html.Div([
                    html.Span(f"🚢 {row['MMSI']}", 
                             style={'fontWeight': '600', 'fontSize': '14px', 'color': COLORS['text']}),
                    html.Span(f"{row['Max_Score']:.3f}", 
                             style={'fontWeight': '700', 'fontSize': '16px', 'color': risk_color,
                                   'float': 'right'})
                ], style={'marginBottom': '4px'}),
                html.Div([
                    html.Span(f"Avg: {row['Avg_Score']:.3f}", 
                             style={'fontSize': '12px', 'color': COLORS['text-light'], 'marginRight': '12px'}),
                    html.Span(f"Records: {int(row['Count'])}", 
                             style={'fontSize': '12px', 'color': COLORS['text-light']})
                ])
            ], style={'padding': '12px', 'borderBottom': f'1px solid {COLORS["light"]}',
                     'transition': 'background-color 0.2s',
                     'cursor': 'pointer'})
        )
    
    return html.Div(items, style={'maxHeight': '240px', 'overflowY': 'auto'})

@app.callback(
    Output('download-dataframe-csv', 'data'),
    [Input('export-button', 'n_clicks')],
    [State('data-store', 'data'),
     State('threshold-slider', 'value')],
    prevent_initial_call=True
)
def export_anomalies(n_clicks, data, threshold):
    """Export anomalies to CSV"""
    if not data or n_clicks == 0:
        return None
    
    df = pd.DataFrame(data)
    anomalies = df[df['ensemble_score'] >= threshold].sort_values('ensemble_score', ascending=False)
    
    # Add risk level
    def get_risk_level(score):
        if score >= 0.85:
            return 'CRITICAL'
        elif score >= threshold:
            return 'HIGH'
        elif score >= 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    anomalies['risk_level'] = anomalies['ensemble_score'].apply(get_risk_level)
    
    # Select columns for export
    export_cols = ['MMSI', 'timestamp', 'lat', 'lon', 'ensemble_score', 
                   'supervised_score', 'unsupervised_score', 'risk_level']
    export_df = anomalies[export_cols]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"iuu_anomalies_{timestamp}.csv"
    
    return dcc.send_data_frame(export_df.to_csv, filename, index=False)

def main():
    """Run dashboard"""
    host = config.get('dashboard', 'host', default='0.0.0.0')
    port = config.get('dashboard', 'port', default=8050)
    
    logger.info("=" * 70)
    logger.info("IUU FISHING DETECTION DASHBOARD")
    logger.info("=" * 70)
    logger.info(f"Starting dashboard at http://{host}:{port}")
    logger.info("Press CTRL+C to stop the server")
    logger.info("=" * 70)
    
    app.run(debug=False, host=host, port=port)

if __name__ == '__main__':
    main()
