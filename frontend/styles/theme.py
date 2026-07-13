CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    color: #e2e8f0;
}

.main .block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.glass-card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.gradient-text {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 2.5rem;
}

.metric-card {
    background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15));
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #3b82f6;
}

.metric-label {
    color: #94a3b8;
    font-size: 0.85rem;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

.stButton > button {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
}

div[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95);
    border-right: 1px solid rgba(59, 130, 246, 0.2);
}

div[data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.6);
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid rgba(59, 130, 246, 0.15);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(30, 41, 59, 0.5);
    border-radius: 8px;
    color: #94a3b8;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, rgba(59,130,246,0.3), rgba(139,92,246,0.3));
    color: #e2e8f0;
}
</style>
"""
