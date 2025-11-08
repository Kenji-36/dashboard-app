"""
Phase 4 - 顧客分析ページ
顧客に関する詳細な分析とセグメンテーション
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
    page_title="顧客分析 | 購買データ分析ダッシュボード",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS読み込み
css_path = project_root / "src" / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# タイトル
st.title("👥 顧客分析")
st.markdown("### 顧客行動とセグメンテーションの分析")

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
    
    # 顧客サマリー
    st.header("👥 顧客サマリー")
    
    col1, col2, col3, col4 = st.columns(4)
    
    unique_customers = filtered_df['顧客ID'].nunique()
    avg_age = filtered_df['年齢'].mean()
    avg_purchase_per_customer = len(filtered_df) / unique_customers if unique_customers > 0 else 0
    
    # リピート顧客の計算
    customer_counts = filtered_df.groupby('顧客ID').size()
    repeat_customers = (customer_counts > 1).sum()
    repeat_rate = (repeat_customers / unique_customers * 100) if unique_customers > 0 else 0
    
    with col1:
        st.metric(
            label="ユニーク顧客数",
            value=f"{unique_customers:,}"
        )
    
    with col2:
        st.metric(
            label="平均年齢",
            value=f"{avg_age:.1f}歳"
        )
    
    with col3:
        st.metric(
            label="顧客あたり平均購入回数",
            value=f"{avg_purchase_per_customer:.1f}回"
        )
    
    with col4:
        st.metric(
            label="リピート率",
            value=f"{repeat_rate:.1f}%"
        )
    
    st.divider()
    
    # 年齢分析
    st.header("📊 年齢分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("年齢分布")
        fig_age_dist = charts.create_age_distribution_chart(filtered_df)
        st.plotly_chart(fig_age_dist, use_container_width=True)
    
    with col2:
        st.subheader("年齢層別分析")
        fig_age_group = charts.create_age_group_analysis_chart(filtered_df)
        st.plotly_chart(fig_age_group, use_container_width=True)
    
    st.divider()
    
    # 性別分析
    st.header("⚧️ 性別分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("性別×地域別売上")
        fig_gender_region = charts.create_gender_region_chart(filtered_df)
        st.plotly_chart(fig_gender_region, use_container_width=True)
    
    with col2:
        st.subheader("性別別統計")
        gender_stats = filtered_df.groupby('性別').agg({
            '購入金額': ['sum', 'mean', 'count'],
            '顧客ID': 'nunique'
        }).round(0)
        
        gender_stats.columns = ['総売上', '平均購入金額', '購入件数', '顧客数']
        gender_stats['顧客あたり購入額'] = (gender_stats['総売上'] / gender_stats['顧客数']).round(0)
        
        st.dataframe(
            gender_stats.style.format({
                '総売上': '¥{:,.0f}',
                '平均購入金額': '¥{:,.0f}',
                '購入件数': '{:,.0f}',
                '顧客数': '{:,.0f}',
                '顧客あたり購入額': '¥{:,.0f}'
            }),
            use_container_width=True
        )
    
    st.divider()
    
    # 購入金額分析
    st.header("💰 購入金額分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("購入金額分布")
        fig_amount_dist = charts.create_purchase_amount_distribution(filtered_df)
        st.plotly_chart(fig_amount_dist, use_container_width=True)
    
    with col2:
        st.subheader("年齢×購入金額 散布図")
        fig_age_amount = charts.create_age_amount_scatter(filtered_df)
        st.plotly_chart(fig_age_amount, use_container_width=True)
    
    st.divider()
    
    # 顧客ランキング
    st.header("🏆 顧客ランキング")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("購入金額トップ10顧客")
        top_customers = filtered_df.groupby('顧客ID').agg({
            '購入金額': 'sum',
            '購入日': 'count',
            '地域': 'first',
            '性別': 'first'
        }).sort_values('購入金額', ascending=False).head(10)
        
        top_customers.columns = ['総購入金額', '購入回数', '地域', '性別']
        top_customers['平均購入金額'] = (top_customers['総購入金額'] / top_customers['購入回数']).round(0)
        
        st.dataframe(
            top_customers.style.format({
                '総購入金額': '¥{:,.0f}',
                '購入回数': '{:,.0f}',
                '平均購入金額': '¥{:,.0f}'
            }),
            use_container_width=True
        )
    
    with col2:
        st.subheader("購入回数トップ10顧客")
        frequent_customers = filtered_df.groupby('顧客ID').agg({
            '購入日': 'count',
            '購入金額': 'sum',
            '地域': 'first',
            '性別': 'first'
        }).sort_values('購入日', ascending=False).head(10)
        
        frequent_customers.columns = ['購入回数', '総購入金額', '地域', '性別']
        frequent_customers['平均購入金額'] = (frequent_customers['総購入金額'] / frequent_customers['購入回数']).round(0)
        
        st.dataframe(
            frequent_customers.style.format({
                '購入回数': '{:,.0f}',
                '総購入金額': '¥{:,.0f}',
                '平均購入金額': '¥{:,.0f}'
            }),
            use_container_width=True
        )
    
    st.divider()
    
    # 地域別顧客分析
    st.header("🗺️ 地域別顧客分析")
    
    region_customer_stats = filtered_df.groupby('地域').agg({
        '顧客ID': 'nunique',
        '購入金額': ['sum', 'mean'],
        '購入日': 'count'
    }).round(0)
    
    region_customer_stats.columns = ['顧客数', '総売上', '平均購入金額', '購入件数']
    region_customer_stats['顧客あたり売上'] = (region_customer_stats['総売上'] / region_customer_stats['顧客数']).round(0)
    region_customer_stats = region_customer_stats.sort_values('総売上', ascending=False)
    
    st.dataframe(
        region_customer_stats.style.format({
            '顧客数': '{:,.0f}',
            '総売上': '¥{:,.0f}',
            '平均購入金額': '¥{:,.0f}',
            '購入件数': '{:,.0f}',
            '顧客あたり売上': '¥{:,.0f}'
        }),
        use_container_width=True
    )
    
    # フッター
    st.divider()
    st.caption("👥 顧客分析ページ | Phase 4")

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
    st.exception(e)

