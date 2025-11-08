"""
設定ファイル - ダッシュボードの各種設定を管理
"""

# カラーパレット設定
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
}

# カテゴリー別カラー設定
CATEGORY_COLORS = {
    '家電': '#1f77b4',      # 青
    'ファッション': '#e377c2',  # ピンク
    'スポーツ': '#2ca02c',   # 緑
    '食品': '#ff7f0e',       # オレンジ
    '書籍': '#9467bd',       # 紫
}

# グラフのデフォルトレイアウト設定
PLOTLY_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
}

PLOTLY_LAYOUT = {
    'font': {'family': 'Arial, sans-serif', 'size': 12},
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50},
    'hovermode': 'closest',
}

# 年齢層の定義
AGE_BINS = [0, 20, 30, 40, 50, 60, 70, 100]
AGE_LABELS = ['10代', '20代', '30代', '40代', '50代', '60代', '70代以上']

# RFM分析のスコア閾値
RFM_THRESHOLDS = {
    'recency': [30, 60, 90],      # 日数
    'frequency': [2, 5, 10],       # 購入回数
    'monetary': [20000, 50000, 100000]  # 購入金額
}

# 顧客セグメント定義
CUSTOMER_SEGMENTS = {
    'VIP': {'rfm_score_min': 9, 'color': '#d4af37'},
    '優良顧客': {'rfm_score_min': 7, 'color': '#2ca02c'},
    '一般顧客': {'rfm_score_min': 5, 'color': '#1f77b4'},
    '要注意顧客': {'rfm_score_min': 3, 'color': '#ff7f0e'},
    '休眠顧客': {'rfm_score_min': 0, 'color': '#d62728'},
}

# データファイルパス
DATA_PATH = 'data/sample-data.csv'

# ページ設定
PAGE_CONFIG = {
    'page_title': '購買データ分析ダッシュボード - Phase 3',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
}

# KPIカードのアイコン
KPI_ICONS = {
    '総売上': '💰',
    '総顧客数': '👥',
    '平均購入金額': '💳',
    '総取引件数': '🛒',
    '平均年齢': '👤',
    'リピート率': '🔄',
}

# エクスポート設定
EXPORT_CONFIG = {
    'csv_encoding': 'utf-8-sig',
    'excel_engine': 'openpyxl',
    'image_format': 'png',
    'image_width': 1200,
    'image_height': 800,
}

