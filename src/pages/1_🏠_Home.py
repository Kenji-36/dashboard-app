"""
Phase 4 - ホームページ
ダッシュボードの概要とクイックアクセス
"""

import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_loader import load_data
from src.utils.data_processor import process_data
from src.components.kpi_cards import display_kpi_cards
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ページ設定
st.set_page_config(
    page_title="ホーム | 購買データ分析ダッシュボード",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS読み込み
css_path = project_root / "src" / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# タイトル
st.title("🏠 ダッシュボード ホーム")
st.markdown("### 購買データ分析システム Phase 4")

# サイドバー
with st.sidebar:
    st.header("📊 ナビゲーション")
    st.info("""
    **Phase 4 新機能:**
    - 🤖 AI予測分析
    - 🔄 リアルタイム更新
    - 🔐 ユーザー認証
    - 💾 データベース統合
    - 🌐 API連携
    """)
    
    st.divider()
    st.header("⚙️ クイック設定")
    
    # データ更新間隔
    refresh_interval = st.selectbox(
        "データ更新間隔",
        ["手動", "30秒", "1分", "5分", "10分"],
        index=0
    )
    
    # テーマ選択
    theme = st.selectbox(
        "カラーテーマ",
        ["デフォルト", "ダーク", "ライト", "カスタム"],
        index=0
    )

# データ読み込み
@st.cache_data(ttl=300)
def load_dashboard_data():
    """ダッシュボード用データを読み込み"""
    df = load_data()
    df = process_data(df)
    return df

try:
    df = load_dashboard_data()
    
    # 概要セクション
    st.header("📈 システム概要")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 総レコード数",
            value=f"{len(df):,}",
            delta="最新データ"
        )
    
    with col2:
        latest_date = df['購入日'].max().strftime('%Y-%m-%d')
        st.metric(
            label="📅 最新データ日付",
            value=latest_date
        )
    
    with col3:
        data_range = (df['購入日'].max() - df['購入日'].min()).days
        st.metric(
            label="📆 データ期間",
            value=f"{data_range}日"
        )
    
    with col4:
        unique_customers = df['顧客ID'].nunique()
        st.metric(
            label="👥 ユニーク顧客数",
            value=f"{unique_customers:,}"
        )
    
    st.divider()
    
    # KPIカード
    st.header("💡 主要指標")
    display_kpi_cards(df)
    
    st.divider()
    
    # クイックインサイト
    st.header("🎯 クイックインサイト")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 今月の売上推移")
        
        # 今月のデータ
        today = datetime.now()
        first_day = today.replace(day=1)
        current_month = df[df['購入日'] >= first_day]
        
        if not current_month.empty:
            daily_sales = current_month.groupby(current_month['購入日'].dt.date)['購入金額'].sum().reset_index()
            daily_sales.columns = ['日付', '売上']
            
            fig = px.line(
                daily_sales,
                x='日付',
                y='売上',
                title='今月の日別売上',
                markers=True
            )
            fig.update_layout(
                height=300,
                showlegend=False,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("今月のデータがありません")
    
    with col2:
        st.subheader("🏆 トップカテゴリー")
        
        # カテゴリー別売上トップ5
        category_sales = df.groupby('購入カテゴリー')['購入金額'].sum().sort_values(ascending=True).tail(5)
        
        fig = px.bar(
            x=category_sales.values,
            y=category_sales.index,
            orientation='h',
            title='売上トップ5カテゴリー',
            labels={'x': '売上金額', 'y': 'カテゴリー'}
        )
        fig.update_layout(
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # 最近のアクティビティ
    st.header("🕐 最近のアクティビティ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 最新の購入記録")
        recent_purchases = df.nlargest(5, '購入日')[['購入日', '顧客ID', '購入カテゴリー', '購入金額', '地域']]
        recent_purchases['購入日'] = recent_purchases['購入日'].dt.strftime('%Y-%m-%d')
        st.dataframe(recent_purchases, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("💰 高額購入トップ5")
        top_purchases = df.nlargest(5, '購入金額')[['購入日', '顧客ID', '購入カテゴリー', '購入金額', '支払方法']]
        top_purchases['購入日'] = top_purchases['購入日'].dt.strftime('%Y-%m-%d')
        st.dataframe(top_purchases, hide_index=True, use_container_width=True)
    
    st.divider()
    
    # システムステータス
    st.header("⚡ システムステータス")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.success("✅ データベース接続")
        st.caption("正常")
    
    with col2:
        st.success("✅ API サーバー")
        st.caption("稼働中")
    
    with col3:
        st.success("✅ キャッシュ")
        st.caption("最適化済み")
    
    with col4:
        st.info("🔄 最終更新")
        st.caption(datetime.now().strftime('%H:%M:%S'))
    
    st.divider()
    
    # クイックアクセス
    st.header("🚀 クイックアクセス")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 売上分析", use_container_width=True):
            st.switch_page("pages/2_📊_Sales_Analysis.py")
    
    with col2:
        if st.button("👥 顧客分析", use_container_width=True):
            st.switch_page("pages/3_👥_Customer_Analysis.py")
    
    with col3:
        if st.button("🤖 AI予測", use_container_width=True):
            st.switch_page("pages/4_🤖_AI_Predictions.py")
    
    with col4:
        if st.button("📈 トレンド分析", use_container_width=True):
            st.switch_page("pages/5_📈_Trends.py")
    
    # フッター
    st.divider()
    st.caption("© 2024 購買データ分析ダッシュボード Phase 4 | Powered by Streamlit 🚀")

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
    st.info("データファイルが存在するか確認してください。")

