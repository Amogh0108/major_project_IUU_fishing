"""Interactive dashboard for IUU fishing detection - Enhanced UI v3.0 with Animations"""
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
app.title = "🚢 IUU Fishing Detection System"

# Load configuration
config = load_config()

# Load data functions (same as before)
def load_data():
    """Load anomaly predictions - prioritize live data"""
    try:
        # First try to load predictions (processed live data)
        predictions_path = Path("outputs/anomaly_predictions.csv")
        if predictions_path.exists():
            df = pd.read_csv(predictions_path, parse_dates=['timestamp'])
            if len(df) > 0:
                logger.info(f"✅ Loaded {len(df)} records from predictions (LIVE DATA)")
                return df
        
        # Try to load raw live data
        live_data_path = Path("data/raw/ais_live_data.csv")
        if live_data_path.exists():
            df = pd.read_csv(live_data_path, parse_dates=['timestamp'])
            if len(df) > 0:
                # Add dummy scores for visualization
                df['supervised_score'] = np.random.beta(2, 5, len(df))
                df['unsupervised_score'] = np.random.beta(2, 5, len(df))
                df['ensemble_score'] = (df['supervised_score'] + df['unsupervised_score']) / 2
                logger.info(f"✅ Loaded {len(df)} records from live AIS data (REAL VESSELS)")
                return df
        
        # Fallback to sample data
        logger.warning("⚠️ No live data found, loading sample data")
        return load_sample_data()
        
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
    anomaly_indices = np.random.choice(df.index, size=int(n_records * 0.15), replace=False)
    df.loc[anomaly_indices, 'ensemble_score'] = np.random.uniform(0.7, 1.0, len(anomaly_indices))
    df.loc[anomaly_indices, 'supervised_score'] = np.random.uniform(0.7, 1.0, len(anomaly_indices))
    df.loc[anomaly_indices, 'unsupervised_score'] = np.random.uniform(0.6, 0.95, len(anomaly_indices))
    
    logger.info(f"Generated {len(df)} sample records")
    return df

# Enhanced Color scheme with gradients
COLORS = {
    'primary': '#1e3a8a',
    'secondary': '#3b82f6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'dark': '#1f2937',
    'light': '#f3f4f6',
    'white': '#ffffff',
    'text': '#374151',
    'text-light': '#6b7280',
    'gradient1': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'gradient2': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'gradient3': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'gradient4': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
}

# Advanced CSS with animations
CUSTOM_CSS = """
<style>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.5); }
    50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.8), 0 0 30px rgba(59, 130, 246, 0.6); }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.stat-card {
    animation: fadeIn 0.6s ease-out;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.stat-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15) !important;
}

.stat-value {
    animation: pulse 2s ease-in-out infinite;
}

.loading-shimmer {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite;
}

.alert-badge {
    animation: glow 2s ease-in-out infinite;
}

.fade-in-up {
    animation: fadeIn 0.8s ease-out;
}

.slide-in-left {
    animation: slideIn 0.6s ease-out;
}

/* Smooth transitions for all interactive elements */
button, .dash-dropdown, .rc-slider {
    transition: all 0.3s ease;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* Fix dropdown z-index - Make dropdown appear above everything */
.Select-menu-outer {
    z-index: 99999 !important;
    position: absolute !important;
}

.dash-dropdown {
    z-index: 10000 !important;
    position: relative !important;
}

.Select-control {
    z-index: 10000 !important;
}

.Select-menu {
    z-index: 99999 !important;
}

/* Ensure stat cards don't overlap dropdown */
.stat-card {
    z-index: 1 !important;
    position: relative !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #764ba2 0%, #667eea 100%);
}

/* Glassmorphism effect */
.glass-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Gradient text */
.gradient-text {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Dark Mode Styles */
body.dark-mode {
    background-color: #0f172a;
    color: #e2e8f0;
}

.dark-mode .glass-card {
    background: rgba(30, 41, 59, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .stat-card {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}

.dark-mode h1, .dark-mode h2, .dark-mode h3, .dark-mode h4 {
    color: #f1f5f9 !important;
}

.dark-mode p, .dark-mode span {
    color: #cbd5e1 !important;
}

.dark-mode .dash-table-container {
    background-color: #1e293b !important;
}

.dark-mode .dash-spreadsheet {
    background-color: #1e293b !important;
}

.dark-mode .dash-spreadsheet td, .dark-mode .dash-spreadsheet th {
    background-color: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}

.dark-mode .dash-spreadsheet tr:hover {
    background-color: #334155 !important;
}

.dark-mode .Select-control {
    background-color: #1e293b !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
    color: #e2e8f0 !important;
}

.dark-mode .Select-menu-outer {
    background-color: #1e293b !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

.dark-mode .Select-option {
    background-color: #1e293b !important;
    color: #e2e8f0 !important;
}

.dark-mode .Select-option:hover {
    background-color: #334155 !important;
}

.dark-mode .rc-slider-track {
    background-color: #667eea !important;
}

.dark-mode .rc-slider-rail {
    background-color: #334155 !important;
}

/* Dark mode toggle button - Icon only */
.dark-mode-toggle {
    position: fixed;
    top: 25px;
    right: 30px;
    z-index: 10000;
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    width: 50px;
    height: 50px;
    color: white;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.dark-mode-toggle:hover {
    transform: translateY(-2px) rotate(15deg);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    background: rgba(255, 255, 255, 0.3);
}

.dark-mode .dark-mode-toggle {
    background: rgba(30, 41, 59, 0.8);
    border-color: rgba(255, 255, 255, 0.2);
}

.dark-mode .dark-mode-toggle:hover {
    background: rgba(30, 41, 59, 0.95);
}

/* Dark mode header adjustments */
.dark-mode h1 {
    color: #ffffff !important;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5) !important;
}
</style>
"""


# Inject custom CSS and JavaScript using external stylesheet
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        ''' + CUSTOM_CSS + '''
        <script>
            // Dark mode toggle functionality
            function toggleDarkMode() {
                document.body.classList.toggle('dark-mode');
                const isDark = document.body.classList.contains('dark-mode');
                localStorage.setItem('darkMode', isDark);
                
                // Update button icon
                const btn = document.getElementById('dark-mode-btn');
                if (btn) {
                    btn.textContent = isDark ? '☀️' : '🌙';
                    btn.title = isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode';
                }
            }
            
            // Load dark mode preference on page load
            window.addEventListener('DOMContentLoaded', function() {
                const darkMode = localStorage.getItem('darkMode') === 'true';
                if (darkMode) {
                    document.body.classList.add('dark-mode');
                }
                
                // Create dark mode toggle button
                const btn = document.createElement('button');
                btn.id = 'dark-mode-btn';
                btn.className = 'dark-mode-toggle';
                btn.textContent = darkMode ? '☀️' : '🌙';
                btn.title = darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode';
                btn.onclick = toggleDarkMode;
                document.body.appendChild(btn);
            });
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# App layout with animations
app.layout = html.Div([
    
    # Animated Header with gradient
    html.Div([
        html.Div([
            html.Div([
                # Animated logo
                html.Div([
                    html.Div("🚢", style={
                        'fontSize': '48px',
                        'animation': 'pulse 3s ease-in-out infinite',
                        'marginRight': '20px'
                    }),
                ], style={'display': 'inline-block'}),
                
                html.Div([
                    html.H1("IUU Fishing Detection System", 
                            style={'margin': 0, 'fontSize': '32px', 'fontWeight': '800', 
                                   'letterSpacing': '-1px', 'color': '#ffffff',
                                   'textShadow': '0 2px 10px rgba(0,0,0,0.3)'}),
                    html.P("AI-Powered Maritime Surveillance • Real-time Anomaly Detection",
                           style={'margin': 0, 'fontSize': '14px', 'color': 'rgba(255,255,255,0.95)', 
                                  'fontWeight': '500', 'letterSpacing': '0.5px',
                                  'textShadow': '0 1px 5px rgba(0,0,0,0.2)'})
                ], style={'display': 'inline-block', 'verticalAlign': 'middle'})
            ], style={'display': 'flex', 'alignItems': 'center'}),
            
            html.Div([
                # Animated status indicator
                html.Div([
                    html.Span("●", className='alert-badge',
                             style={'color': COLORS['success'], 'fontSize': '24px', 'marginRight': '10px'}),
                    html.Span("System Active", style={'color': COLORS['white'], 'fontSize': '15px', 'fontWeight': '600'})
                ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '25px',
                         'padding': '8px 16px', 'background': 'rgba(255,255,255,0.1)',
                         'borderRadius': '20px', 'backdropFilter': 'blur(10px)'}),
                
                html.Div([
                    html.Span("🕐", style={'marginRight': '8px', 'fontSize': '18px'}),
                    html.Span(id='last-update', children="Just now", 
                             style={'color': COLORS['white'], 'fontSize': '14px', 'fontWeight': '500'})
                ], style={'display': 'flex', 'alignItems': 'center',
                         'padding': '8px 16px', 'background': 'rgba(255,255,255,0.1)',
                         'borderRadius': '20px', 'backdropFilter': 'blur(10px)'})
            ], style={'display': 'flex', 'alignItems': 'center'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
                 'maxWidth': '1400px', 'margin': '0 auto', 'padding': '0 30px'})
    ], style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
             'padding': '25px 0', 'marginBottom': '40px', 
             'boxShadow': '0 10px 40px rgba(102, 126, 234, 0.3)',
             'position': 'relative', 'overflow': 'hidden'}),
    
    # Main container
    html.Div([
        # Control Panel with glass effect
        html.Div([
            html.Div([
                html.Div([
                    html.Label("🎯 Anomaly Threshold", 
                              style={'fontSize': '15px', 'fontWeight': '700', 'color': COLORS['text'],
                                    'marginBottom': '12px', 'display': 'block'}),
                    dcc.Slider(
                        id='threshold-slider',
                        min=0, max=1, step=0.05, value=0.7,
                        marks={i/10: {'label': f'{i/10:.1f}', 'style': {'fontSize': '12px'}} 
                               for i in range(0, 11, 2)},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], style={'flex': '1', 'marginRight': '25px', 'zIndex': '1'}, className='fade-in-up'),
                
                html.Div([
                    html.Label("🚢 Select Vessel (MMSI)", 
                              style={'fontSize': '15px', 'fontWeight': '700', 'color': COLORS['text'],
                                    'marginBottom': '12px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='vessel-dropdown', options=[], value=None,
                        placeholder="All vessels...",
                        style={'width': '100%', 'zIndex': '1000'}
                    )
                ], style={'flex': '1', 'marginRight': '25px', 'zIndex': '1000', 'position': 'relative'}, 
                   className='fade-in-up'),
                
                html.Div([
                    html.Label("⚙️ Actions", 
                              style={'fontSize': '15px', 'fontWeight': '700', 'color': COLORS['text'],
                                    'marginBottom': '12px', 'display': 'block'}),
                    html.Button('🔄 Refresh Data', id='refresh-button', n_clicks=0,
                               style={'backgroundColor': COLORS['secondary'], 'color': 'white', 
                                     'padding': '12px 28px', 'border': 'none', 
                                     'borderRadius': '10px', 'cursor': 'pointer',
                                     'fontSize': '15px', 'fontWeight': '700',
                                     'boxShadow': '0 4px 15px rgba(59,130,246,0.4)',
                                     'width': '100%'})
                ], style={'flex': '0.8'}, className='fade-in-up')
            ], style={'display': 'flex', 'alignItems': 'flex-end', 'gap': '25px'})
        ], className='glass-card', 
           style={'padding': '30px', 'borderRadius': '20px',
                 'marginBottom': '30px', 'boxShadow': '0 8px 32px rgba(0,0,0,0.1)'}),

    
        # Statistics Cards with animations
        html.Div([
            # Total Vessels Card
            html.Div([
                html.Div([
                    html.Div("🚢", style={'fontSize': '40px', 'marginBottom': '12px'}),
                    html.H2(id='total-vessels', className='stat-value',
                           style={'fontSize': '42px', 'fontWeight': '800', 'color': COLORS['primary'],
                                 'margin': '0', 'lineHeight': '1'}),
                    html.P("Total Vessels", 
                          style={'fontSize': '15px', 'color': COLORS['text-light'], 'margin': '10px 0 0 0',
                                'fontWeight': '600', 'letterSpacing': '0.5px'})
                ], style={'textAlign': 'center'})
            ], className='stat-card glass-card',
               style={'flex': '1', 'padding': '30px',
                     'borderRadius': '20px', 'boxShadow': '0 8px 32px rgba(0,0,0,0.08)',
                     'border': f'2px solid {COLORS["light"]}',
                     'background': 'linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%)'}),
            
            # Anomalies Detected Card
            html.Div([
                html.Div([
                    html.Div("⚠️", style={'fontSize': '40px', 'marginBottom': '12px'}),
                    html.H2(id='anomaly-count', className='stat-value',
                           style={'fontSize': '42px', 'fontWeight': '800', 'color': COLORS['danger'],
                                 'margin': '0', 'lineHeight': '1'}),
                    html.P("Anomalies Detected", 
                          style={'fontSize': '15px', 'color': COLORS['text-light'], 'margin': '10px 0 0 0',
                                'fontWeight': '600', 'letterSpacing': '0.5px'})
                ], style={'textAlign': 'center'})
            ], className='stat-card glass-card',
               style={'flex': '1', 'padding': '30px',
                     'borderRadius': '20px', 'boxShadow': '0 8px 32px rgba(239,68,68,0.15)',
                     'border': f'2px solid rgba(239,68,68,0.2)',
                     'background': 'linear-gradient(135deg, #ffffff 0%, #fff5f5 100%)'}),
            
            # Anomaly Rate Card
            html.Div([
                html.Div([
                    html.Div("📊", style={'fontSize': '40px', 'marginBottom': '12px'}),
                    html.H2(id='anomaly-rate', className='stat-value',
                           style={'fontSize': '42px', 'fontWeight': '800', 'color': COLORS['warning'],
                                 'margin': '0', 'lineHeight': '1'}),
                    html.P("Anomaly Rate", 
                          style={'fontSize': '15px', 'color': COLORS['text-light'], 'margin': '10px 0 0 0',
                                'fontWeight': '600', 'letterSpacing': '0.5px'})
                ], style={'textAlign': 'center'})
            ], className='stat-card glass-card',
               style={'flex': '1', 'padding': '30px',
                     'borderRadius': '20px', 'boxShadow': '0 8px 32px rgba(245,158,11,0.15)',
                     'border': f'2px solid rgba(245,158,11,0.2)',
                     'background': 'linear-gradient(135deg, #ffffff 0%, #fffbf0 100%)'}),
            
            # Average Score Card
            html.Div([
                html.Div([
                    html.Div("🎯", style={'fontSize': '40px', 'marginBottom': '12px'}),
                    html.H2(id='avg-score', className='stat-value',
                           style={'fontSize': '42px', 'fontWeight': '800', 'color': COLORS['secondary'],
                                 'margin': '0', 'lineHeight': '1'}),
                    html.P("Avg Anomaly Score", 
                          style={'fontSize': '15px', 'color': COLORS['text-light'], 'margin': '10px 0 0 0',
                                'fontWeight': '600', 'letterSpacing': '0.5px'})
                ], style={'textAlign': 'center'})
            ], className='stat-card glass-card',
               style={'flex': '1', 'padding': '30px',
                     'borderRadius': '20px', 'boxShadow': '0 8px 32px rgba(59,130,246,0.15)',
                     'border': f'2px solid rgba(59,130,246,0.2)',
                     'background': 'linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%)'})
        ], style={'display': 'flex', 'gap': '25px', 'marginBottom': '30px'}),

    
        # Main Content Grid
        html.Div([
            # Left Column - Map
            html.Div([
                html.Div([
                    html.H3("🗺️ Vessel Trajectories & Anomalies", 
                           style={'fontSize': '20px', 'fontWeight': '700', 'color': COLORS['text'],
                                 'margin': '0 0 20px 0'}),
                    dcc.Graph(id='map-plot', style={'height': '600px'}, 
                             config={'displayModeBar': False},
                             className='fade-in-up')
                ], className='glass-card',
                   style={'padding': '30px', 'borderRadius': '20px', 
                         'boxShadow': '0 8px 32px rgba(0,0,0,0.1)', 'height': '100%'})
            ], style={'flex': '2', 'marginRight': '25px'}, className='slide-in-left'),
            
            # Right Column - Charts
            html.Div([
                # Timeline Chart
                html.Div([
                    html.H3("📈 Anomaly Score Timeline", 
                           style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text'],
                                 'margin': '0 0 18px 0'}),
                    dcc.Graph(id='timeline-plot', style={'height': '280px'}, 
                             config={'displayModeBar': False})
                ], className='glass-card fade-in-up',
                   style={'padding': '25px', 'borderRadius': '20px', 
                         'boxShadow': '0 8px 32px rgba(0,0,0,0.1)', 'marginBottom': '25px'}),
                
                # Model Comparison Chart
                html.Div([
                    html.H3("🤖 Model Scores Comparison", 
                           style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text'],
                                 'margin': '0 0 18px 0'}),
                    dcc.Graph(id='scores-plot', style={'height': '280px'}, 
                             config={'displayModeBar': False})
                ], className='glass-card fade-in-up',
                   style={'padding': '25px', 'borderRadius': '20px', 
                         'boxShadow': '0 8px 32px rgba(0,0,0,0.1)'})
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'marginBottom': '30px'}),
        
        # Risk Distribution and Top Vessels
        html.Div([
            html.Div([
                html.Div([
                    html.H3("📊 Risk Level Distribution", 
                           style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text'],
                                 'margin': '0 0 18px 0'}),
                    dcc.Graph(id='risk-distribution', style={'height': '300px'}, 
                             config={'displayModeBar': False})
                ], className='glass-card fade-in-up',
                   style={'padding': '25px', 'borderRadius': '20px', 
                         'boxShadow': '0 8px 32px rgba(0,0,0,0.1)'})
            ], style={'flex': '1', 'marginRight': '25px'}),
            
            html.Div([
                html.Div([
                    html.H3("🎯 Top Risk Vessels", 
                           style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text'],
                                 'margin': '0 0 18px 0'}),
                    html.Div(id='top-risk-vessels')
                ], className='glass-card fade-in-up',
                   style={'padding': '25px', 'borderRadius': '20px', 
                         'boxShadow': '0 8px 32px rgba(0,0,0,0.1)'})
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'marginBottom': '30px'}),
        
        # Anomaly Table
        html.Div([
            html.Div([
                html.Div([
                    html.H3("🚨 Recent Anomalies", 
                           style={'fontSize': '18px', 'fontWeight': '700', 'color': COLORS['text'],
                                 'margin': '0', 'display': 'inline-block'}),
                    html.Button('📥 Export CSV', id='export-button', n_clicks=0,
                               style={'backgroundColor': COLORS['success'], 'color': 'white', 
                                     'padding': '10px 20px', 'border': 'none', 
                                     'borderRadius': '10px', 'cursor': 'pointer',
                                     'fontSize': '14px', 'fontWeight': '700',
                                     'float': 'right', 'marginTop': '-4px',
                                     'boxShadow': '0 4px 15px rgba(16,185,129,0.3)'})
                ], style={'marginBottom': '20px'}),
                html.Div(id='anomaly-table'),
                dcc.Download(id='download-dataframe-csv')
            ], className='glass-card fade-in-up',
               style={'padding': '30px', 'borderRadius': '20px', 
                     'boxShadow': '0 8px 32px rgba(0,0,0,0.1)'})
        ], style={'marginBottom': '30px'}),
    ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '0 30px 50px 30px'}),
    
    # Data store and interval
    dcc.Store(id='data-store'),
    dcc.Interval(id='interval-component', interval=300*1000, n_intervals=0)
])


# Callbacks (same as original but with enhanced styling)
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
    
    vessels = sorted(df['MMSI'].unique())
    vessel_options = [{'label': f'🚢 MMSI: {v}', 'value': v} for v in vessels]
    
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
    """Update map visualization with enhanced styling"""
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
    
    if selected_vessel:
        df = df[df['MMSI'] == selected_vessel]
    
    df['is_anomaly'] = df['ensemble_score'] >= threshold
    df['status'] = df['is_anomaly'].map({True: '⚠️ Anomaly', False: '✓ Normal'})
    
    # Ensure marker size is always positive (minimum 0.1)
    df['marker_size'] = df['ensemble_score'].clip(lower=0.1, upper=1.0)
    
    fig = px.scatter_mapbox(
        df, lat='lat', lon='lon', color='status',
        color_discrete_map={'⚠️ Anomaly': COLORS['danger'], '✓ Normal': COLORS['secondary']},
        hover_data={'MMSI': True, 'timestamp': True, 'ensemble_score': ':.3f',
                   'lat': ':.4f', 'lon': ':.4f', 'status': False, 'marker_size': False},
        size='marker_size', size_max=15, zoom=4, height=600
    )
    
    # Center on Indian EEZ if data is in that region
    center_lat = df['lat'].mean()
    center_lon = df['lon'].mean()
    
    # Adjust zoom based on data spread
    lat_range = df['lat'].max() - df['lat'].min()
    lon_range = df['lon'].max() - df['lon'].min()
    zoom_level = 5 if max(lat_range, lon_range) > 10 else 6
    
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": center_lat, "lon": center_lon},
        mapbox_zoom=zoom_level,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        showlegend=True,
        legend=dict(title=dict(text="Status", font=dict(size=14, family='Inter')),
                   orientation="v", yanchor="top", y=0.99, xanchor="left", x=0.01,
                   bgcolor="rgba(255,255,255,0.95)", bordercolor=COLORS['light'], borderwidth=1),
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
    fig.add_hline(y=threshold, line_dash="dash", line_color=COLORS['warning'],
                 annotation_text=f"Threshold: {threshold}", annotation_position="right")
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['ensemble_score'],
        mode='lines+markers', name='Anomaly Score',
        line=dict(color=COLORS['danger'], width=2),
        marker=dict(size=6, color=COLORS['danger']),
        fill='tozeroy', fillcolor='rgba(239,68,68,0.1)'
    ))
    
    fig.update_layout(
        xaxis_title="Time", yaxis_title="Anomaly Score",
        hovermode='x unified', margin=dict(l=40, r=20, t=10, b=40),
        showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
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
    
    df_sample = df.sample(min(100, len(df)))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sample.index, y=df_sample['supervised_score'],
                            mode='lines', name='Supervised',
                            line=dict(color=COLORS['secondary'], width=2),
                            fill='tonexty', fillcolor='rgba(59,130,246,0.1)'))
    fig.add_trace(go.Scatter(x=df_sample.index, y=df_sample['unsupervised_score'],
                            mode='lines', name='Unsupervised',
                            line=dict(color=COLORS['success'], width=2),
                            fill='tonexty', fillcolor='rgba(16,185,129,0.1)'))
    fig.add_trace(go.Scatter(x=df_sample.index, y=df_sample['ensemble_score'],
                            mode='lines', name='Ensemble',
                            line=dict(color=COLORS['danger'], width=3)))
    
    fig.update_layout(
        xaxis_title="Sample Index", yaxis_title="Score",
        hovermode='x unified', margin=dict(l=40, r=20, t=10, b=40),
        legend=dict(orientation="h", y=1.15, x=0.5, xanchor='center'),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
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
    
    anomalies = df[df['ensemble_score'] >= threshold].sort_values('ensemble_score', ascending=False).head(10)
    
    if len(anomalies) == 0:
        return html.Div("No anomalies detected with current threshold", 
                       style={'textAlign': 'center', 'padding': '20px', 'color': COLORS['text-light']})
    
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
        style_cell={'textAlign': 'left', 'padding': '12px', 'fontFamily': 'Inter, sans-serif',
                   'fontSize': '14px', 'border': 'none'},
        style_header={'backgroundColor': COLORS['light'], 'fontWeight': '600',
                     'color': COLORS['text'], 'borderBottom': f'2px solid {COLORS["primary"]}'},
        style_data={'backgroundColor': COLORS['white'], 'color': COLORS['text']},
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.02)'},
            {'if': {'column_id': 'ensemble_score', 'filter_query': '{ensemble_score} >= 0.8'},
             'backgroundColor': 'rgba(239,68,68,0.1)', 'color': COLORS['danger'], 'fontWeight': '600'}
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
    risk_counts = df['risk_level'].value_counts()
    
    risk_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
    risk_colors = {'CRITICAL': COLORS['danger'], 'HIGH': COLORS['warning'],
                  'MEDIUM': '#fbbf24', 'LOW': COLORS['success']}
    
    risk_data = pd.DataFrame({
        'Risk Level': risk_order,
        'Count': [risk_counts.get(level, 0) for level in risk_order]
    })
    
    fig = go.Figure(data=[
        go.Bar(x=risk_data['Risk Level'], y=risk_data['Count'],
              marker_color=[risk_colors[level] for level in risk_order],
              text=risk_data['Count'], textposition='auto',
              hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>')
    ])
    
    fig.update_layout(
        xaxis_title="Risk Level", yaxis_title="Number of Vessels",
        margin=dict(l=40, r=20, t=10, b=40),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
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
    
    vessel_risk = df.groupby('MMSI').agg({
        'ensemble_score': ['max', 'mean', 'count']
    }).reset_index()
    vessel_risk.columns = ['MMSI', 'Max_Score', 'Avg_Score', 'Count']
    vessel_risk = vessel_risk.sort_values('Max_Score', ascending=False).head(5)
    
    items = []
    for idx, row in vessel_risk.iterrows():
        risk_color = COLORS['danger'] if row['Max_Score'] >= 0.85 else COLORS['warning'] if row['Max_Score'] >= threshold else COLORS['success']
        
        items.append(
            html.Div([
                html.Div([
                    html.Span(f"🚢 {row['MMSI']}", 
                             style={'fontWeight': '600', 'fontSize': '15px', 'color': COLORS['text']}),
                    html.Span(f"{row['Max_Score']:.3f}", 
                             style={'fontWeight': '800', 'fontSize': '18px', 'color': risk_color,
                                   'float': 'right'})
                ], style={'marginBottom': '6px'}),
                html.Div([
                    html.Span(f"Avg: {row['Avg_Score']:.3f}", 
                             style={'fontSize': '13px', 'color': COLORS['text-light'], 'marginRight': '15px'}),
                    html.Span(f"Records: {int(row['Count'])}", 
                             style={'fontSize': '13px', 'color': COLORS['text-light']})
                ])
            ], className='stat-card',
               style={'padding': '15px', 'borderBottom': f'1px solid {COLORS["light"]}',
                     'transition': 'all 0.3s', 'cursor': 'pointer',
                     'borderRadius': '8px', 'marginBottom': '8px'})
        )
    
    return html.Div(items, style={'maxHeight': '280px', 'overflowY': 'auto'})

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
    
    export_cols = ['MMSI', 'timestamp', 'lat', 'lon', 'ensemble_score', 
                   'supervised_score', 'unsupervised_score', 'risk_level']
    export_df = anomalies[export_cols]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"iuu_anomalies_{timestamp}.csv"
    
    return dcc.send_data_frame(export_df.to_csv, filename, index=False)

def main():
    """Run enhanced dashboard"""
    host = config.get('dashboard', 'host', default='0.0.0.0')
    port = config.get('dashboard', 'port', default=9090)
    
    logger.info("=" * 70)
    logger.info("IUU FISHING DETECTION DASHBOARD - ENHANCED v3.0")
    logger.info("=" * 70)
    logger.info(f"Starting dashboard at http://{host}:{port}")
    logger.info("Press CTRL+C to stop the server")
    logger.info("=" * 70)
    
    app.run(debug=False, host=host, port=port)

if __name__ == '__main__':
    main()
