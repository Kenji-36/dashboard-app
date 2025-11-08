"""
Phase 4 - AI予測ページ
機械学習による売上予測と顧客分析
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_loader import load_data
from src.utils.data_processor import filter_data
from src.components.filters import display_sidebar_filters
from src.utils.ml_models import (
    predict_sales_simple,
    calculate_forecast_accuracy,
    predict_customer_segment,
    calculate_churn_probability,
    recommend_products
)

# ページ設定
st.set_page_config(
    page_title="AI予測 | 購買データ分析ダッシュボード",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS読み込み
css_path = project_root / "src" / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# タイトル
st.title("🤖 AI予測分析")
st.markdown("### 機械学習による売上予測と顧客行動分析")

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
    
    # フィルター情報表示
    st.info(f"📊 表示中のデータ: {len(filtered_df):,}件 / 全体: {len(df):,}件")
    
    st.divider()
    
    # タブで機能を分割
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 売上予測",
        "👥 顧客セグメント",
        "⚠️ 離脱予測",
        "🎁 レコメンデーション"
    ])
    
    # タブ1: 売上予測
    with tab1:
        st.header("📈 売上予測")
        st.markdown("過去のデータから将来の売上を予測します")
        
        # 予測期間の選択
        col1, col2 = st.columns([1, 3])
        
        with col1:
            forecast_days = st.selectbox(
                "予測期間",
                [7, 14, 30, 60, 90],
                index=2,
                format_func=lambda x: f"{x}日間"
            )
        
        with col2:
            st.info("💡 移動平均とトレンド分析を使用して予測を行います")
        
        # 予測実行
        with st.spinner("予測を計算中..."):
            historical_df, predictions_df = predict_sales_simple(filtered_df, days=forecast_days)
        
        if not predictions_df.empty:
            # 予測グラフ
            st.subheader("📊 予測結果")
            
            fig = go.Figure()
            
            # 実績データ
            fig.add_trace(go.Scatter(
                x=historical_df['日付'],
                y=historical_df['売上'],
                mode='lines',
                name='実績売上',
                line=dict(color='#1f77b4', width=2)
            ))
            
            # 移動平均
            fig.add_trace(go.Scatter(
                x=historical_df['日付'],
                y=historical_df['MA7'],
                mode='lines',
                name='7日移動平均',
                line=dict(color='#ff7f0e', width=1, dash='dash')
            ))
            
            # 予測データ
            fig.add_trace(go.Scatter(
                x=predictions_df['日付'],
                y=predictions_df['予測売上'],
                mode='lines+markers',
                name='予測売上',
                line=dict(color='#2ca02c', width=2),
                marker=dict(size=6)
            ))
            
            # 信頼区間
            fig.add_trace(go.Scatter(
                x=predictions_df['日付'].tolist() + predictions_df['日付'].tolist()[::-1],
                y=predictions_df['上限'].tolist() + predictions_df['下限'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(44, 160, 44, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% 信頼区間',
                showlegend=True
            ))
            
            fig.update_layout(
                title=f'売上予測 ({forecast_days}日間)',
                xaxis_title='日付',
                yaxis_title='売上金額 (円)',
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 予測サマリー
            st.subheader("📊 予測サマリー")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_predicted = predictions_df['予測売上'].sum()
            avg_predicted = predictions_df['予測売上'].mean()
            max_predicted = predictions_df['予測売上'].max()
            min_predicted = predictions_df['予測売上'].min()
            
            with col1:
                st.metric(
                    label=f"{forecast_days}日間の予測総売上",
                    value=f"¥{total_predicted:,.0f}"
                )
            
            with col2:
                st.metric(
                    label="1日あたり平均予測売上",
                    value=f"¥{avg_predicted:,.0f}"
                )
            
            with col3:
                st.metric(
                    label="最高予測売上",
                    value=f"¥{max_predicted:,.0f}"
                )
            
            with col4:
                st.metric(
                    label="最低予測売上",
                    value=f"¥{min_predicted:,.0f}"
                )
            
            # 予測データテーブル
            with st.expander("📋 予測データ詳細"):
                display_predictions = predictions_df.copy()
                display_predictions['日付'] = display_predictions['日付'].dt.strftime('%Y-%m-%d')
                display_predictions['曜日'] = predictions_df['日付'].dt.day_name()
                
                st.dataframe(
                    display_predictions.style.format({
                        '予測売上': '¥{:,.0f}',
                        '下限': '¥{:,.0f}',
                        '上限': '¥{:,.0f}'
                    }),
                    use_container_width=True
                )
    
    # タブ2: 顧客セグメント
    with tab2:
        st.header("👥 顧客セグメント予測")
        st.markdown("RFM分析に基づいて顧客をセグメント化します")
        
        with st.spinner("セグメント分析中..."):
            customer_segments = predict_customer_segment(filtered_df)
        
        if not customer_segments.empty:
            # セグメント分布
            st.subheader("📊 セグメント分布")
            
            segment_counts = customer_segments['セグメント'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    values=segment_counts.values,
                    names=segment_counts.index,
                    title='顧客セグメント分布',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # セグメント別統計
                segment_stats = customer_segments.groupby('セグメント').agg({
                    '顧客ID': 'count',
                    '総購入金額': 'sum',
                    '平均購入金額': 'mean',
                    '購入回数': 'mean'
                }).round(0)
                
                segment_stats.columns = ['顧客数', '総売上', '平均購入金額', '平均購入回数']
                
                st.dataframe(
                    segment_stats.style.format({
                        '顧客数': '{:,.0f}',
                        '総売上': '¥{:,.0f}',
                        '平均購入金額': '¥{:,.0f}',
                        '平均購入回数': '{:.1f}'
                    }),
                    use_container_width=True
                )
            
            # RFM散布図
            st.subheader("📈 RFM分析 散布図")
            
            fig = px.scatter_3d(
                customer_segments,
                x='Recency',
                y='Frequency',
                z='Monetary',
                color='セグメント',
                title='RFM 3D散布図',
                labels={
                    'Recency': '最終購入からの日数',
                    'Frequency': '購入回数',
                    'Monetary': '総購入金額'
                },
                hover_data=['顧客ID']
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # セグメント別詳細
            with st.expander("📋 セグメント別顧客リスト"):
                selected_segment = st.selectbox(
                    "セグメントを選択",
                    customer_segments['セグメント'].unique()
                )
                
                segment_customers = customer_segments[
                    customer_segments['セグメント'] == selected_segment
                ].sort_values('総購入金額', ascending=False)
                
                st.dataframe(
                    segment_customers[['顧客ID', '総購入金額', '平均購入金額', '購入回数', 'Recency']].style.format({
                        '総購入金額': '¥{:,.0f}',
                        '平均購入金額': '¥{:,.0f}',
                        '購入回数': '{:.0f}',
                        'Recency': '{:.0f}日'
                    }),
                    use_container_width=True
                )
    
    # タブ3: 離脱予測
    with tab3:
        st.header("⚠️ 顧客離脱予測")
        st.markdown("購入パターンから離脱リスクの高い顧客を特定します")
        
        with st.spinner("離脱リスク分析中..."):
            churn_data = calculate_churn_probability(filtered_df)
        
        if not churn_data.empty:
            # リスクレベル分布
            st.subheader("📊 リスクレベル分布")
            
            col1, col2 = st.columns(2)
            
            with col1:
                risk_counts = churn_data['リスクレベル'].value_counts()
                
                fig = px.bar(
                    x=risk_counts.index,
                    y=risk_counts.values,
                    title='リスクレベル別顧客数',
                    labels={'x': 'リスクレベル', 'y': '顧客数'},
                    color=risk_counts.index,
                    color_discrete_map={
                        '高リスク': '#d62728',
                        '中リスク': '#ff7f0e',
                        '低リスク': '#2ca02c'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # リスクレベル別統計
                risk_stats = churn_data.groupby('リスクレベル').agg({
                    '顧客ID': 'count',
                    '総購入金額': 'sum',
                    '離脱確率(%)': 'mean'
                }).round(0)
                
                risk_stats.columns = ['顧客数', '総売上', '平均離脱確率(%)']
                
                st.dataframe(
                    risk_stats.style.format({
                        '顧客数': '{:,.0f}',
                        '総売上': '¥{:,.0f}',
                        '平均離脱確率(%)': '{:.1f}%'
                    }),
                    use_container_width=True
                )
            
            # 高リスク顧客リスト
            st.subheader("🚨 高リスク顧客トップ20")
            
            high_risk = churn_data.head(20)[['顧客ID', '離脱確率(%)', 'リスクレベル', '経過日数', '総購入金額', '購入回数']]
            
            st.dataframe(
                high_risk.style.format({
                    '離脱確率(%)': '{:.1f}%',
                    '経過日数': '{:.0f}日',
                    '総購入金額': '¥{:,.0f}',
                    '購入回数': '{:.0f}'
                }).background_gradient(subset=['離脱確率(%)'], cmap='Reds'),
                use_container_width=True
            )
            
            # 推奨アクション
            st.subheader("💡 推奨アクション")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("""
                **高リスク顧客への対応:**
                - 特別オファーの送付
                - パーソナライズドメール
                - 限定クーポンの提供
                """)
            
            with col2:
                st.warning("""
                **中リスク顧客への対応:**
                - 定期的なニュースレター
                - 新商品の案内
                - ポイントプログラム
                """)
            
            with col3:
                st.success("""
                **低リスク顧客への対応:**
                - ロイヤリティプログラム
                - VIP特典の提供
                - 紹介プログラム
                """)
    
    # タブ4: レコメンデーション
    with tab4:
        st.header("🎁 商品レコメンデーション")
        st.markdown("購買パターンに基づいて人気商品を推奨します")
        
        # 全体の人気商品
        st.subheader("🏆 全体の人気商品トップ5")
        
        with st.spinner("レコメンデーション生成中..."):
            recommendations = recommend_products(filtered_df, top_n=5)
        
        if not recommendations.empty:
            st.dataframe(
                recommendations.style.format({
                    '総売上': '¥{:,.0f}',
                    '購入回数': '{:,.0f}',
                    '平均購入金額': '¥{:,.0f}',
                    '人気スコア': '{:,.0f}'
                }),
                use_container_width=True
            )
            
            # 人気スコアの可視化
            fig = px.bar(
                recommendations,
                x='カテゴリー',
                y='人気スコア',
                title='カテゴリー別人気スコア',
                color='人気スコア',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 顧客別レコメンデーション
        st.subheader("👤 顧客別レコメンデーション")
        
        customer_ids = filtered_df['顧客ID'].unique()
        selected_customer = st.selectbox(
            "顧客IDを選択",
            customer_ids
        )
        
        if selected_customer:
            # 顧客の購入履歴
            customer_history = filtered_df[filtered_df['顧客ID'] == selected_customer]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**購入履歴:**")
                st.dataframe(
                    customer_history[['購入日', '購入カテゴリー', '購入金額']].sort_values('購入日', ascending=False).head(10),
                    hide_index=True,
                    use_container_width=True
                )
            
            with col2:
                st.write("**推奨商品:**")
                customer_recommendations = recommend_products(filtered_df, customer_id=selected_customer, top_n=5)
                
                if not customer_recommendations.empty:
                    st.dataframe(
                        customer_recommendations[['カテゴリー', '総売上', '購入回数']].style.format({
                            '総売上': '¥{:,.0f}',
                            '購入回数': '{:,.0f}'
                        }),
                        hide_index=True,
                        use_container_width=True
                    )
    
    # フッター
    st.divider()
    st.caption("🤖 AI予測分析ページ | Phase 4")

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
    st.exception(e)

