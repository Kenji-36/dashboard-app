"""
Phase 3 メインアプリケーション - 完全版ダッシュボード
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# パスの設定
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import PAGE_CONFIG, DATA_PATH
from src.utils.data_loader import load_data
from src.utils.data_processor import filter_data, add_age_group, calculate_kpis
from src.utils.analytics import (
    calculate_rfm, generate_insights, calculate_seasonality,
    calculate_trend, calculate_customer_lifetime_value
)
from src.utils.export import export_to_csv, export_to_excel, prepare_export_data, create_summary_report
from src.components.kpi_cards import display_kpi_cards, display_comparison_metrics
from src.components.filters import display_sidebar_filters, display_filter_summary
from src.components import charts

# ページ設定
st.set_page_config(**PAGE_CONFIG)

# カスタムCSSの読み込み
try:
    with open('src/styles/custom.css', encoding='utf-8') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass

# タイトルとヘッダー
st.title("📊 購買データ分析ダッシュボード - Phase 3 完全版")
st.markdown("### 顧客行動と売上の高度な可視化・分析")
st.markdown("---")

# データの読み込み
@st.cache_data
def get_data():
    return load_data(DATA_PATH)

try:
    df = get_data()
    
    if df.empty:
        st.error("❌ データが読み込めませんでした。")
        st.stop()
    
    # サイドバーフィルター
    filters = display_sidebar_filters(df)
    
    # データフィルタリング
    filtered_df = filter_data(df, filters)
    
    # 年齢層を追加
    filtered_df = add_age_group(filtered_df)
    
    # フィルター適用状況の表示
    display_filter_summary(filters, len(filtered_df), len(df))
    
    st.markdown("---")
    
    # KPI計算
    kpis = calculate_kpis(filtered_df)
    
    # 最高・最低購入金額を追加
    if not filtered_df.empty:
        kpis['最高購入金額'] = filtered_df['購入金額'].max()
        kpis['最低購入金額'] = filtered_df['購入金額'].min()
    
    # KPIカード表示
    st.markdown("## 📈 主要指標（KPI）")
    display_kpi_cards(kpis)
    
    st.markdown("---")
    
    # メインタブ
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 売上分析",
        "👥 顧客分析",
        "💳 支払方法分析",
        "🎯 RFM分析",
        "📈 トレンド分析",
        "📋 データテーブル",
        "💡 インサイト"
    ])
    
    # タブ1: 売上分析
    with tab1:
        st.header("📊 売上分析")
        
        # 時系列分析
        st.subheader("📈 時系列分析")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_monthly = charts.create_monthly_sales_chart(filtered_df)
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        with col2:
            fig_daily = charts.create_time_series_area_chart(filtered_df)
            st.plotly_chart(fig_daily, use_container_width=True)
        
        # カテゴリー分析
        st.subheader("🏷️ カテゴリー分析")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_category_pie = charts.create_category_pie_chart(filtered_df)
            st.plotly_chart(fig_category_pie, use_container_width=True)
        
        with col2:
            fig_category_bar = charts.create_category_ranking_bar(filtered_df)
            st.plotly_chart(fig_category_bar, use_container_width=True)
        
        # 地域分析
        st.subheader("🗾 地域分析")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_region = charts.create_region_bar_chart(filtered_df)
            st.plotly_chart(fig_region, use_container_width=True)
        
        with col2:
            fig_heatmap = charts.create_heatmap_region_category(filtered_df)
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # タブ2: 顧客分析
    with tab2:
        st.header("👥 顧客分析")
        
        # 年齢分析
        st.subheader("👤 年齢分析")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_age_dist = charts.create_age_distribution_histogram(filtered_df)
            st.plotly_chart(fig_age_dist, use_container_width=True)
        
        with col2:
            fig_age_group = charts.create_age_group_analysis(filtered_df)
            st.plotly_chart(fig_age_group, use_container_width=True)
        
        # 性別×地域分析
        st.subheader("👥 性別×地域分析")
        fig_gender_region = charts.create_gender_region_grouped_bar(filtered_df)
        st.plotly_chart(fig_gender_region, use_container_width=True)
        
        # 散布図
        st.subheader("📊 年齢×購入金額の関係")
        fig_scatter = charts.create_scatter_age_amount(filtered_df)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # 購入金額分布
        st.subheader("💰 購入金額分布")
        fig_amount_dist = charts.create_purchase_amount_distribution(filtered_df)
        st.plotly_chart(fig_amount_dist, use_container_width=True)
    
    # タブ3: 支払方法分析
    with tab3:
        st.header("💳 支払方法分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_payment = charts.create_payment_donut_chart(filtered_df)
            st.plotly_chart(fig_payment, use_container_width=True)
        
        with col2:
            fig_payment_heatmap = charts.create_payment_category_heatmap(filtered_df)
            st.plotly_chart(fig_payment_heatmap, use_container_width=True)
        
        # 支払方法別統計
        st.subheader("📊 支払方法別統計")
        payment_stats = filtered_df.groupby('支払方法').agg({
            '購入金額': ['sum', 'mean', 'count'],
            '顧客ID': 'nunique'
        }).reset_index()
        payment_stats.columns = ['支払方法', '総売上', '平均購入金額', '取引件数', '顧客数']
        
        # フォーマット
        payment_stats['総売上'] = payment_stats['総売上'].apply(lambda x: f'¥{x:,.0f}')
        payment_stats['平均購入金額'] = payment_stats['平均購入金額'].apply(lambda x: f'¥{x:,.0f}')
        
        st.dataframe(payment_stats, use_container_width=True, hide_index=True)
    
    # タブ4: RFM分析
    with tab4:
        st.header("🎯 RFM分析（顧客セグメンテーション）")
        
        with st.spinner('RFM分析を実行中...'):
            rfm_df = calculate_rfm(filtered_df)
        
        if not rfm_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 顧客セグメント分布")
                fig_segment = charts.create_customer_segment_pie(rfm_df)
                st.plotly_chart(fig_segment, use_container_width=True)
            
            with col2:
                st.subheader("📈 セグメント別統計")
                segment_stats = rfm_df.groupby('顧客セグメント').agg({
                    '顧客ID': 'count',
                    'Monetary': ['sum', 'mean'],
                    'Frequency': 'mean'
                }).reset_index()
                segment_stats.columns = ['顧客セグメント', '顧客数', '総購入金額', '平均購入金額', '平均購入回数']
                
                # フォーマット
                segment_stats['総購入金額'] = segment_stats['総購入金額'].apply(lambda x: f'¥{x:,.0f}')
                segment_stats['平均購入金額'] = segment_stats['平均購入金額'].apply(lambda x: f'¥{x:,.0f}')
                segment_stats['平均購入回数'] = segment_stats['平均購入回数'].apply(lambda x: f'{x:.1f}回')
                
                st.dataframe(segment_stats, use_container_width=True, hide_index=True)
            
            # 3D散布図
            st.subheader("🎨 RFM 3D分析")
            fig_3d = charts.create_rfm_scatter_3d(rfm_df)
            st.plotly_chart(fig_3d, use_container_width=True)
            
            # RFMデータテーブル
            with st.expander("📋 RFM詳細データ"):
                st.dataframe(
                    rfm_df.sort_values('RFM_Score', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.warning("⚠️ RFM分析を実行するには、複数の購入データが必要です。")
    
    # タブ5: トレンド分析
    with tab5:
        st.header("📈 トレンド分析")
        
        # 移動平均付きトレンド
        st.subheader("📊 売上トレンド（移動平均）")
        fig_trend = charts.create_trend_with_moving_average(filtered_df)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # 曜日別分析
        st.subheader("📅 曜日別売上")
        col1, col2 = st.columns(2)
        
        with col1:
            fig_weekday = charts.create_weekday_sales_bar(filtered_df)
            st.plotly_chart(fig_weekday, use_container_width=True)
        
        with col2:
            # 曜日別統計
            weekday_stats = filtered_df.groupby('曜日_日本語').agg({
                '購入金額': ['sum', 'mean', 'count']
            }).reset_index()
            weekday_stats.columns = ['曜日', '総売上', '平均購入金額', '取引件数']
            
            weekday_order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
            weekday_stats['曜日'] = pd.Categorical(weekday_stats['曜日'], categories=weekday_order, ordered=True)
            weekday_stats = weekday_stats.sort_values('曜日')
            
            weekday_stats['総売上'] = weekday_stats['総売上'].apply(lambda x: f'¥{x:,.0f}')
            weekday_stats['平均購入金額'] = weekday_stats['平均購入金額'].apply(lambda x: f'¥{x:,.0f}')
            
            st.dataframe(weekday_stats, use_container_width=True, hide_index=True)
        
        # 月×カテゴリーヒートマップ
        st.subheader("🗓️ 月×カテゴリーヒートマップ")
        fig_monthly_heatmap = charts.create_monthly_category_heatmap(filtered_df)
        st.plotly_chart(fig_monthly_heatmap, use_container_width=True)
        
        # 季節性分析
        st.subheader("🌸 季節性分析")
        seasonality_df = calculate_seasonality(filtered_df)
        if not seasonality_df.empty:
            seasonality_df['総売上'] = seasonality_df['総売上'].apply(lambda x: f'¥{x:,.0f}')
            seasonality_df['平均購入金額'] = seasonality_df['平均購入金額'].apply(lambda x: f'¥{x:,.0f}')
            seasonality_df['平均比'] = seasonality_df['平均比'].apply(lambda x: f'{x:+.1f}%')
            
            st.dataframe(seasonality_df, use_container_width=True, hide_index=True)
    
    # タブ6: データテーブル
    with tab6:
        st.header("📋 データテーブル")
        
        # 表示オプション
        col1, col2, col3 = st.columns(3)
        
        with col1:
            display_columns = st.multiselect(
                "表示する列を選択",
                filtered_df.columns.tolist(),
                default=['顧客ID', '年齢', '性別', '地域', '購入カテゴリー', '購入金額', '購入日', '支払方法']
            )
        
        with col2:
            if display_columns:
                sort_column = st.selectbox("並び替え列", display_columns)
            else:
                sort_column = None
        
        with col3:
            sort_order = st.radio("並び替え順", ["昇順", "降順"], horizontal=True)
        
        # データ表示
        if display_columns and sort_column:
            display_df = filtered_df[display_columns].copy()
            display_df = display_df.sort_values(
                by=sort_column,
                ascending=(sort_order == "昇順")
            )
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            
            # エクスポート機能
            st.subheader("📥 データエクスポート")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # CSVエクスポート
                csv_data = display_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📄 CSVダウンロード",
                    data=csv_data,
                    file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Excelエクスポート（複数シート）
                export_dict = prepare_export_data(filtered_df, include_analysis=True)
                excel_data = export_to_excel(export_dict)
                st.download_button(
                    label="📊 Excelダウンロード",
                    data=excel_data,
                    file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col3:
                # サマリーレポート
                rfm_df = calculate_rfm(filtered_df) if len(filtered_df) > 0 else pd.DataFrame()
                insights = generate_insights(filtered_df, rfm_df)
                summary_report = create_summary_report(filtered_df, kpis, insights)
                summary_csv = summary_report.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📋 サマリーレポート",
                    data=summary_csv,
                    file_name=f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("⚠️ 表示する列を選択してください。")
    
    # タブ7: インサイト
    with tab7:
        st.header("💡 自動生成インサイト")
        
        with st.spinner('インサイトを生成中...'):
            rfm_df = calculate_rfm(filtered_df) if len(filtered_df) > 0 else pd.DataFrame()
            insights = generate_insights(filtered_df, rfm_df)
        
        # インサイト表示
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 トップパフォーマンス")
            
            if 'top_category' in insights:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>最も売上が高いカテゴリー</h4>
                    <p><strong>{insights['top_category']}</strong></p>
                    <p>売上金額: <strong>¥{insights['top_category_sales']:,.0f}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            if 'top_age_group' in insights:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>最も購入金額が高い年齢層</h4>
                    <p><strong>{insights['top_age_group']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            if 'top_payment_method' in insights:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>最も利用されている支払方法</h4>
                    <p><strong>{insights['top_payment_method']}</strong></p>
                    <p>利用回数: <strong>{insights['top_payment_count']}回</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📊 ビジネス指標")
            
            if 'top_month' in insights:
                st.markdown(f"""
                <div class="insight-box">
                    <h4>売上が最も高い月</h4>
                    <p><strong>{insights['top_month']}</strong></p>
                    <p>売上金額: <strong>¥{insights['top_month_sales']:,.0f}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            if 'customer_segments' in insights:
                st.markdown("""
                <div class="insight-box">
                    <h4>顧客セグメント分布</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for segment, count in insights['customer_segments'].items():
                    st.write(f"**{segment}**: {count}人")
        
        # 統計サマリー
        st.subheader("📈 統計サマリー")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### カテゴリー別統計")
            category_summary = filtered_df.groupby('購入カテゴリー').agg({
                '購入金額': ['count', 'sum', 'mean', 'max', 'min']
            }).reset_index()
            category_summary.columns = ['カテゴリー', '購入件数', '総売上', '平均購入金額', '最高購入金額', '最低購入金額']
            
            # フォーマット
            for col in ['総売上', '平均購入金額', '最高購入金額', '最低購入金額']:
                category_summary[col] = category_summary[col].apply(lambda x: f'¥{x:,.0f}')
            
            st.dataframe(category_summary, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### 地域別統計")
            region_summary = filtered_df.groupby('地域').agg({
                '購入金額': ['count', 'sum', 'mean'],
                '顧客ID': 'nunique'
            }).reset_index()
            region_summary.columns = ['地域', '購入件数', '総売上', '平均購入金額', '顧客数']
            
            # フォーマット
            for col in ['総売上', '平均購入金額']:
                region_summary[col] = region_summary[col].apply(lambda x: f'¥{x:,.0f}')
            
            st.dataframe(region_summary, use_container_width=True, hide_index=True)
    
    # フッター
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        <p><strong>データ件数:</strong> {len(filtered_df):,}件 / {len(df):,}件</p>
        <p><strong>最終更新:</strong> {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        <p>📊 Phase 3 完全版ダッシュボード | Powered by Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"❌ データファイルが見つかりません: {DATA_PATH}")
    st.info("💡 'data/sample-data.csv'が存在することを確認してください。")
except Exception as e:
    st.error(f"❌ エラーが発生しました: {str(e)}")
    st.exception(e)

