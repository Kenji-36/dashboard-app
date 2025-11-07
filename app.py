import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# ページ設定
st.set_page_config(
    page_title="販売データダッシュボード",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトル
st.title("📊 販売データダッシュボード")
st.markdown("---")

# データの読み込み
@st.cache_data
def load_data():
    df = pd.read_csv('data/sample-data.csv')
    df['購入日'] = pd.to_datetime(df['購入日'])
    df['年月'] = df['購入日'].dt.to_period('M').astype(str)
    return df

try:
    df = load_data()
    
    # サイドバー - フィルター
    st.sidebar.header("🔍 フィルター")
    
    # 地域フィルター
    regions = ['全て'] + sorted(df['地域'].unique().tolist())
    selected_region = st.sidebar.selectbox("地域", regions)
    
    # 性別フィルター
    genders = ['全て'] + sorted(df['性別'].unique().tolist())
    selected_gender = st.sidebar.selectbox("性別", genders)
    
    # カテゴリーフィルター
    categories = ['全て'] + sorted(df['購入カテゴリー'].unique().tolist())
    selected_category = st.sidebar.selectbox("購入カテゴリー", categories)
    
    # データフィルタリング
    filtered_df = df.copy()
    if selected_region != '全て':
        filtered_df = filtered_df[filtered_df['地域'] == selected_region]
    if selected_gender != '全て':
        filtered_df = filtered_df[filtered_df['性別'] == selected_gender]
    if selected_category != '全て':
        filtered_df = filtered_df[filtered_df['購入カテゴリー'] == selected_category]
    
    # KPI表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="総売上",
            value=f"¥{filtered_df['購入金額'].sum():,.0f}",
            delta=f"{len(filtered_df)}件"
        )
    
    with col2:
        st.metric(
            label="平均購入金額",
            value=f"¥{filtered_df['購入金額'].mean():,.0f}",
        )
    
    with col3:
        st.metric(
            label="顧客数",
            value=f"{filtered_df['顧客ID'].nunique():,}人"
        )
    
    with col4:
        st.metric(
            label="平均年齢",
            value=f"{filtered_df['年齢'].mean():.1f}歳"
        )
    
    st.markdown("---")
    
    # グラフ表示
    tab1, tab2, tab3, tab4 = st.tabs(["📈 時系列分析", "📊 カテゴリー分析", "👥 顧客分析", "📋 データテーブル"])
    
    with tab1:
        st.subheader("月別売上推移")
        monthly_sales = filtered_df.groupby('年月')['購入金額'].sum().reset_index()
        fig1 = px.line(
            monthly_sales,
            x='年月',
            y='購入金額',
            markers=True,
            title="月別売上推移"
        )
        fig1.update_layout(
            xaxis_title="年月",
            yaxis_title="売上金額 (円)",
            hovermode='x unified'
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("支払方法別売上")
            payment_sales = filtered_df.groupby('支払方法')['購入金額'].sum().reset_index()
            fig2 = px.pie(
                payment_sales,
                values='購入金額',
                names='支払方法',
                title="支払方法別売上構成"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            st.subheader("地域別売上")
            region_sales = filtered_df.groupby('地域')['購入金額'].sum().reset_index()
            fig3 = px.bar(
                region_sales,
                x='地域',
                y='購入金額',
                title="地域別売上",
                color='購入金額',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig3, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("カテゴリー別売上")
            category_sales = filtered_df.groupby('購入カテゴリー')['購入金額'].sum().reset_index()
            fig4 = px.bar(
                category_sales,
                x='購入カテゴリー',
                y='購入金額',
                title="カテゴリー別売上",
                color='購入金額',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            st.subheader("カテゴリー別購入件数")
            category_count = filtered_df['購入カテゴリー'].value_counts().reset_index()
            category_count.columns = ['購入カテゴリー', '件数']
            fig5 = px.pie(
                category_count,
                values='件数',
                names='購入カテゴリー',
                title="カテゴリー別購入件数"
            )
            st.plotly_chart(fig5, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("年齢分布")
            fig6 = px.histogram(
                filtered_df,
                x='年齢',
                nbins=20,
                title="顧客年齢分布",
                color_discrete_sequence=['#636EFA']
            )
            fig6.update_layout(
                xaxis_title="年齢",
                yaxis_title="人数"
            )
            st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            st.subheader("性別×地域別売上")
            gender_region = filtered_df.groupby(['性別', '地域'])['購入金額'].sum().reset_index()
            fig7 = px.bar(
                gender_region,
                x='地域',
                y='購入金額',
                color='性別',
                title="性別×地域別売上",
                barmode='group'
            )
            st.plotly_chart(fig7, use_container_width=True)
        
        st.subheader("年齢層別購入金額")
        filtered_df['年齢層'] = pd.cut(
            filtered_df['年齢'],
            bins=[0, 20, 30, 40, 50, 60, 100],
            labels=['~20代', '30代', '40代', '50代', '60代', '70代~']
        )
        age_group_sales = filtered_df.groupby('年齢層')['購入金額'].agg(['sum', 'mean', 'count']).reset_index()
        age_group_sales.columns = ['年齢層', '合計金額', '平均金額', '購入件数']
        
        fig8 = go.Figure()
        fig8.add_trace(go.Bar(
            x=age_group_sales['年齢層'],
            y=age_group_sales['合計金額'],
            name='合計金額',
            yaxis='y',
            marker_color='lightblue'
        ))
        fig8.add_trace(go.Scatter(
            x=age_group_sales['年齢層'],
            y=age_group_sales['平均金額'],
            name='平均金額',
            yaxis='y2',
            marker_color='red',
            mode='lines+markers'
        ))
        fig8.update_layout(
            title='年齢層別購入金額（合計と平均）',
            yaxis=dict(title='合計金額 (円)'),
            yaxis2=dict(title='平均金額 (円)', overlaying='y', side='right'),
            hovermode='x unified'
        )
        st.plotly_chart(fig8, use_container_width=True)
    
    with tab4:
        st.subheader("データテーブル")
        
        # 表示列の選択
        all_columns = filtered_df.columns.tolist()
        selected_columns = st.multiselect(
            "表示する列を選択",
            all_columns,
            default=['顧客ID', '年齢', '性別', '地域', '購入カテゴリー', '購入金額', '購入日', '支払方法']
        )
        
        if selected_columns:
            # データの並び替え
            sort_column = st.selectbox("並び替え列", selected_columns)
            sort_order = st.radio("並び替え順", ["昇順", "降順"], horizontal=True)
            
            display_df = filtered_df[selected_columns].copy()
            display_df = display_df.sort_values(
                by=sort_column,
                ascending=(sort_order == "昇順")
            )
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
            
            # CSVダウンロード
            csv = display_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSVダウンロード",
                data=csv,
                file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("表示する列を選択してください。")
    
    # フッター
    st.markdown("---")
    st.markdown(f"**データ件数:** {len(filtered_df):,}件 / {len(df):,}件")

except FileNotFoundError:
    st.error("❌ データファイルが見つかりません。'data/sample-data.csv'が存在することを確認してください。")
except Exception as e:
    st.error(f"❌ エラーが発生しました: {str(e)}")

