"""
Phase 4 - 売上分析ページ
売上に関する詳細な分析とグラフ
"""

import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_loader import load_data
from src.utils.data_processor import filter_data, add_age_group
from src.components.filters import display_sidebar_filters
from src.components import charts

# ページ設定
st.set_page_config(
    page_title="売上分析 | 購買データ分析ダッシュボード",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS読み込み
css_path = project_root / "src" / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# タイトル
st.title("📊 売上分析")
st.markdown("### 売上データの詳細な可視化と分析")

# データ読み込み
@st.cache_data(ttl=300)
def get_data():
    df = load_data()
    return df

try:
    df = get_data()
    
    # サイドバーフィルター
    filters = display_sidebar_filters(df)
    
    # データフィルタリング
    filtered_df = filter_data(df, filters)
    filtered_df = add_age_group(filtered_df)
    
    # フィルター情報表示
    st.info(f"📊 表示中のデータ: {len(filtered_df):,}件 / 全体: {len(df):,}件")
    
    st.divider()
    
    # サマリーメトリクス
    st.header("💰 売上サマリー")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = filtered_df['購入金額'].sum()
    avg_sales = filtered_df['購入金額'].mean()
    max_sales = filtered_df['購入金額'].max()
    min_sales = filtered_df['購入金額'].min()
    
    with col1:
        st.metric(
            label="総売上",
            value=f"¥{total_sales:,.0f}"
        )
    
    with col2:
        st.metric(
            label="平均購入金額",
            value=f"¥{avg_sales:,.0f}"
        )
    
    with col3:
        st.metric(
            label="最高購入金額",
            value=f"¥{max_sales:,.0f}"
        )
    
    with col4:
        st.metric(
            label="最低購入金額",
            value=f"¥{min_sales:,.0f}"
        )
    
    st.divider()
    
    # 時系列分析
    st.header("📈 時系列分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("月別売上推移")
        fig_monthly = charts.create_monthly_sales_chart(filtered_df)
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        st.subheader("日別売上推移")
        fig_daily = charts.create_daily_sales_chart(filtered_df)
        st.plotly_chart(fig_daily, use_container_width=True)
    
    st.divider()
    
    # カテゴリー分析
    st.header("🏷️ カテゴリー別分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("カテゴリー別売上構成")
        fig_category_pie = charts.create_category_pie_chart(filtered_df)
        st.plotly_chart(fig_category_pie, use_container_width=True)
    
    with col2:
        st.subheader("カテゴリー別売上ランキング")
        fig_category_bar = charts.create_category_bar_chart(filtered_df)
        st.plotly_chart(fig_category_bar, use_container_width=True)
    
    st.divider()
    
    # 地域分析
    st.header("🗺️ 地域別分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("地域別売上比較")
        fig_region = charts.create_region_sales_chart(filtered_df)
        st.plotly_chart(fig_region, use_container_width=True)
    
    with col2:
        st.subheader("地域×カテゴリー ヒートマップ")
        fig_heatmap = charts.create_region_category_heatmap(filtered_df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.divider()
    
    # 曜日・時間分析
    st.header("📅 曜日別分析")
    
    st.subheader("曜日別売上パターン")
    fig_weekday = charts.create_weekday_sales_chart(filtered_df)
    st.plotly_chart(fig_weekday, use_container_width=True)
    
    st.divider()
    
    # 月×カテゴリーヒートマップ
    st.header("🔥 月×カテゴリー ヒートマップ")
    fig_month_category = charts.create_month_category_heatmap(filtered_df)
    st.plotly_chart(fig_month_category, use_container_width=True)
    
    st.divider()
    
    # 詳細統計
    st.header("📊 カテゴリー別詳細統計")
    
    category_stats = filtered_df.groupby('購入カテゴリー').agg({
        '購入金額': ['sum', 'mean', 'count', 'min', 'max']
    }).round(0)
    
    category_stats.columns = ['総売上', '平均購入金額', '購入件数', '最小金額', '最大金額']
    category_stats = category_stats.sort_values('総売上', ascending=False)
    
    # 構成比を追加
    category_stats['構成比(%)'] = (category_stats['総売上'] / category_stats['総売上'].sum() * 100).round(1)
    
    st.dataframe(
        category_stats.style.format({
            '総売上': '¥{:,.0f}',
            '平均購入金額': '¥{:,.0f}',
            '購入件数': '{:,.0f}',
            '最小金額': '¥{:,.0f}',
            '最大金額': '¥{:,.0f}',
            '構成比(%)': '{:.1f}%'
        }),
        use_container_width=True
    )
    
    # フッター
    st.divider()
    st.caption("📊 売上分析ページ | Phase 4")

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
    st.exception(e)

