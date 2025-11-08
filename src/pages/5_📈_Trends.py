"""
Phase 4 - トレンド分析ページ
時系列データの詳細な分析とトレンド把握
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
from src.utils.analytics import calculate_rfm, generate_insights

# ページ設定
st.set_page_config(
    page_title="トレンド分析 | 購買データ分析ダッシュボード",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS読み込み
css_path = project_root / "src" / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# タイトル
st.title("📈 トレンド分析")
st.markdown("### 時系列データの詳細な分析と傾向把握")

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
    
    # 売上トレンド（移動平均付き）
    st.header("📊 売上トレンド（移動平均）")
    
    fig_trend = charts.create_sales_trend_with_ma(filtered_df)
    st.plotly_chart(fig_trend, use_container_width=True)
    
    st.divider()
    
    # 曜日別分析
    st.header("📅 曜日別売上パターン")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_weekday = charts.create_weekday_sales_chart(filtered_df)
        st.plotly_chart(fig_weekday, use_container_width=True)
    
    with col2:
        # 曜日別統計
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['曜日'] = filtered_df_copy['購入日'].dt.day_name()
        weekday_stats = filtered_df_copy.groupby('曜日').agg({
            '購入金額': ['sum', 'mean', 'count']
        }).round(0)
        
        weekday_stats.columns = ['総売上', '平均購入金額', '購入件数']
        
        # 曜日の順序を設定
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_stats = weekday_stats.reindex(weekday_order)
        
        st.write("**曜日別統計:**")
        st.dataframe(
            weekday_stats.style.format({
                '総売上': '¥{:,.0f}',
                '平均購入金額': '¥{:,.0f}',
                '購入件数': '{:,.0f}'
            }),
            use_container_width=True
        )
    
    st.divider()
    
    # 月×カテゴリーヒートマップ
    st.header("🔥 月×カテゴリー ヒートマップ")
    
    fig_heatmap = charts.create_month_category_heatmap(filtered_df)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.divider()
    
    # 支払方法×カテゴリーヒートマップ
    st.header("💳 支払方法×カテゴリー ヒートマップ")
    
    fig_payment_heatmap = charts.create_payment_category_heatmap(filtered_df)
    st.plotly_chart(fig_payment_heatmap, use_container_width=True)
    
    st.divider()
    
    # RFM分析
    st.header("🎯 RFM分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("顧客セグメント分布")
        fig_rfm_pie = charts.create_rfm_segment_pie(filtered_df)
        st.plotly_chart(fig_rfm_pie, use_container_width=True)
    
    with col2:
        st.subheader("RFM 3D散布図")
        fig_rfm_3d = charts.create_rfm_3d_scatter(filtered_df)
        st.plotly_chart(fig_rfm_3d, use_container_width=True)
    
    st.divider()
    
    # インサイト生成
    st.header("💡 自動生成インサイト")
    
    with st.spinner("インサイトを生成中..."):
        insights = generate_insights(filtered_df)
    
    if insights:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📊 売上インサイト")
            if 'トップカテゴリー' in insights:
                st.success(f"**トップカテゴリー:** {insights['トップカテゴリー']}")
            if 'トップ地域' in insights:
                st.success(f"**トップ地域:** {insights['トップ地域']}")
            if '総売上' in insights:
                st.metric("総売上", f"¥{insights['総売上']:,.0f}")
        
        with col2:
            st.subheader("👥 顧客インサイト")
            if 'ユニーク顧客数' in insights:
                st.info(f"**ユニーク顧客数:** {insights['ユニーク顧客数']:,}人")
            if '平均年齢' in insights:
                st.info(f"**平均年齢:** {insights['平均年齢']:.1f}歳")
            if 'リピート率' in insights:
                st.metric("リピート率", f"{insights['リピート率']:.1f}%")
        
        with col3:
            st.subheader("💳 購入インサイト")
            if '平均購入金額' in insights:
                st.warning(f"**平均購入金額:** ¥{insights['平均購入金額']:,.0f}")
            if '最高購入金額' in insights:
                st.warning(f"**最高購入金額:** ¥{insights['最高購入金額']:,.0f}")
            if '総取引件数' in insights:
                st.metric("総取引件数", f"{insights['総取引件数']:,}件")
    
    st.divider()
    
    # 期間比較
    st.header("📊 期間比較分析")
    
    # 月別比較
    monthly_sales = filtered_df.groupby(filtered_df['購入日'].dt.to_period('M')).agg({
        '購入金額': 'sum',
        '顧客ID': 'nunique',
        '購入日': 'count'
    }).reset_index()
    
    monthly_sales.columns = ['月', '売上', '顧客数', '購入件数']
    monthly_sales['月'] = monthly_sales['月'].astype(str)
    
    # 前月比の計算
    if len(monthly_sales) > 1:
        monthly_sales['売上前月比(%)'] = monthly_sales['売上'].pct_change() * 100
        monthly_sales['顧客数前月比(%)'] = monthly_sales['顧客数'].pct_change() * 100
    
    st.dataframe(
        monthly_sales.style.format({
            '売上': '¥{:,.0f}',
            '顧客数': '{:,.0f}',
            '購入件数': '{:,.0f}',
            '売上前月比(%)': '{:+.1f}%',
            '顧客数前月比(%)': '{:+.1f}%'
        }),
        use_container_width=True
    )
    
    # フッター
    st.divider()
    st.caption("📈 トレンド分析ページ | Phase 4")

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
    st.exception(e)

