"""
グラフコンポーネント - 15+種類のグラフを提供
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from src.config import CATEGORY_COLORS, PLOTLY_CONFIG, PLOTLY_LAYOUT


def create_monthly_sales_chart(df: pd.DataFrame, title: str = "月別売上推移") -> go.Figure:
    """月別売上推移グラフ"""
    monthly_sales = df.groupby('年月')['購入金額'].sum().reset_index()
    
    fig = px.line(
        monthly_sales,
        x='年月',
        y='購入金額',
        markers=True,
        title=title
    )
    
    fig.update_traces(
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8)
    )
    
    layout_config = PLOTLY_LAYOUT.copy()
    layout_config.update({
        'xaxis_title': "年月",
        'yaxis_title': "売上金額 (円)",
        'hovermode': 'x unified'
    })
    fig.update_layout(**layout_config)
    
    return fig


def create_category_pie_chart(df: pd.DataFrame, title: str = "カテゴリー別売上構成") -> go.Figure:
    """カテゴリー別円グラフ"""
    category_sales = df.groupby('購入カテゴリー')['購入金額'].sum().reset_index()
    
    colors = [CATEGORY_COLORS.get(cat, '#cccccc') for cat in category_sales['購入カテゴリー']]
    
    fig = px.pie(
        category_sales,
        values='購入金額',
        names='購入カテゴリー',
        title=title,
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>売上: ¥%{value:,.0f}<br>割合: %{percent}<extra></extra>'
    )
    
    fig.update_layout(**PLOTLY_LAYOUT)
    
    return fig


def create_region_bar_chart(df: pd.DataFrame, title: str = "地域別売上") -> go.Figure:
    """地域別棒グラフ"""
    region_sales = df.groupby('地域')['購入金額'].sum().reset_index()
    region_sales = region_sales.sort_values('購入金額', ascending=False)
    
    fig = px.bar(
        region_sales,
        x='地域',
        y='購入金額',
        title=title,
        color='購入金額',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="地域",
        yaxis_title="売上金額 (円)",
        showlegend=False
    )
    
    return fig


def create_payment_donut_chart(df: pd.DataFrame, title: str = "支払方法別利用割合") -> go.Figure:
    """支払方法別ドーナツグラフ"""
    payment_counts = df['支払方法'].value_counts().reset_index()
    payment_counts.columns = ['支払方法', '件数']
    
    fig = go.Figure(data=[go.Pie(
        labels=payment_counts['支払方法'],
        values=payment_counts['件数'],
        hole=0.4,
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
    )])
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>件数: %{value}<br>割合: %{percent}<extra></extra>'
    )
    
    fig.update_layout(**PLOTLY_LAYOUT, title=title)
    
    return fig


def create_age_distribution_histogram(df: pd.DataFrame, title: str = "年齢分布") -> go.Figure:
    """年齢分布ヒストグラム"""
    fig = px.histogram(
        df,
        x='年齢',
        nbins=30,
        title=title,
        color_discrete_sequence=['#636EFA']
    )
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="年齢",
        yaxis_title="人数",
        bargap=0.1
    )
    
    return fig


def create_gender_region_grouped_bar(df: pd.DataFrame, title: str = "性別×地域別売上") -> go.Figure:
    """性別×地域別グループ化棒グラフ"""
    gender_region = df.groupby(['性別', '地域'])['購入金額'].sum().reset_index()
    
    fig = px.bar(
        gender_region,
        x='地域',
        y='購入金額',
        color='性別',
        title=title,
        barmode='group',
        color_discrete_map={'男性': '#1f77b4', '女性': '#e377c2'}
    )
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="地域",
        yaxis_title="売上金額 (円)"
    )
    
    return fig


def create_age_group_analysis(df: pd.DataFrame, title: str = "年齢層別分析") -> go.Figure:
    """年齢層別の複合グラフ（棒グラフ+折れ線グラフ）"""
    df_copy = df.copy()
    df_copy['年齢層'] = pd.cut(
        df_copy['年齢'],
        bins=[0, 20, 30, 40, 50, 60, 100],
        labels=['10代', '20代', '30代', '40代', '50代', '60代以上']
    )
    
    age_stats = df_copy.groupby('年齢層').agg({
        '購入金額': ['sum', 'mean'],
        '顧客ID': 'count'
    }).reset_index()
    
    age_stats.columns = ['年齢層', '総売上', '平均購入金額', '購入件数']
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=age_stats['年齢層'],
            y=age_stats['総売上'],
            name='総売上',
            marker_color='lightblue'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=age_stats['年齢層'],
            y=age_stats['平均購入金額'],
            name='平均購入金額',
            mode='lines+markers',
            marker=dict(size=10, color='red'),
            line=dict(width=3, color='red')
        ),
        secondary_y=True
    )
    
    layout_config = PLOTLY_LAYOUT.copy()
    layout_config.update({
        'title': title,
        'hovermode': 'x unified'
    })
    fig.update_layout(**layout_config)
    
    fig.update_xaxes(title_text="年齢層")
    fig.update_yaxes(title_text="総売上 (円)", secondary_y=False)
    fig.update_yaxes(title_text="平均購入金額 (円)", secondary_y=True)
    
    return fig


def create_heatmap_region_category(df: pd.DataFrame, title: str = "地域×カテゴリーヒートマップ") -> go.Figure:
    """地域×カテゴリーのヒートマップ"""
    pivot_data = pd.pivot_table(
        df,
        values='購入金額',
        index='地域',
        columns='購入カテゴリー',
        aggfunc='sum',
        fill_value=0
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Blues',
        hovertemplate='地域: %{y}<br>カテゴリー: %{x}<br>売上: ¥%{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=title,
        xaxis_title="購入カテゴリー",
        yaxis_title="地域"
    )
    
    return fig


def create_time_series_area_chart(df: pd.DataFrame, title: str = "日別売上推移") -> go.Figure:
    """日別売上推移エリアチャート"""
    daily_sales = df.groupby('購入日')['購入金額'].sum().reset_index()
    
    fig = px.area(
        daily_sales,
        x='購入日',
        y='購入金額',
        title=title
    )
    
    fig.update_traces(
        line=dict(color='#1f77b4'),
        fillcolor='rgba(31, 119, 180, 0.3)'
    )
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="日付",
        yaxis_title="売上金額 (円)"
    )
    
    return fig


def create_category_ranking_bar(df: pd.DataFrame, title: str = "カテゴリー別売上ランキング") -> go.Figure:
    """カテゴリー別横棒グラフ（ランキング）"""
    category_sales = df.groupby('購入カテゴリー')['購入金額'].sum().reset_index()
    category_sales = category_sales.sort_values('購入金額', ascending=True)
    
    colors = [CATEGORY_COLORS.get(cat, '#cccccc') for cat in category_sales['購入カテゴリー']]
    
    fig = go.Figure(go.Bar(
        x=category_sales['購入金額'],
        y=category_sales['購入カテゴリー'],
        orientation='h',
        marker=dict(color=colors),
        text=category_sales['購入金額'].apply(lambda x: f'¥{x:,.0f}'),
        textposition='outside'
    ))
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=title,
        xaxis_title="売上金額 (円)",
        yaxis_title="カテゴリー"
    )
    
    return fig


def create_scatter_age_amount(df: pd.DataFrame, title: str = "年齢×購入金額の散布図") -> go.Figure:
    """年齢と購入金額の散布図"""
    fig = px.scatter(
        df,
        x='年齢',
        y='購入金額',
        color='性別',
        title=title,
        opacity=0.6,
        color_discrete_map={'男性': '#1f77b4', '女性': '#e377c2'}
    )
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="年齢",
        yaxis_title="購入金額 (円)"
    )
    
    return fig


def create_payment_category_heatmap(df: pd.DataFrame, title: str = "支払方法×カテゴリーヒートマップ") -> go.Figure:
    """支払方法×カテゴリーのヒートマップ"""
    pivot_data = pd.pivot_table(
        df,
        values='顧客ID',
        index='支払方法',
        columns='購入カテゴリー',
        aggfunc='count',
        fill_value=0
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Viridis',
        hovertemplate='支払方法: %{y}<br>カテゴリー: %{x}<br>件数: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=title,
        xaxis_title="購入カテゴリー",
        yaxis_title="支払方法"
    )
    
    return fig


def create_weekday_sales_bar(df: pd.DataFrame, title: str = "曜日別売上") -> go.Figure:
    """曜日別売上棒グラフ"""
    weekday_order = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
    
    weekday_sales = df.groupby('曜日_日本語')['購入金額'].sum().reset_index()
    weekday_sales['曜日_日本語'] = pd.Categorical(
        weekday_sales['曜日_日本語'],
        categories=weekday_order,
        ordered=True
    )
    weekday_sales = weekday_sales.sort_values('曜日_日本語')
    
    fig = px.bar(
        weekday_sales,
        x='曜日_日本語',
        y='購入金額',
        title=title,
        color='購入金額',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="曜日",
        yaxis_title="売上金額 (円)",
        showlegend=False
    )
    
    return fig


def create_monthly_category_heatmap(df: pd.DataFrame, title: str = "月×カテゴリーヒートマップ") -> go.Figure:
    """月×カテゴリーのヒートマップ"""
    pivot_data = pd.pivot_table(
        df,
        values='購入金額',
        index='月',
        columns='購入カテゴリー',
        aggfunc='sum',
        fill_value=0
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='RdYlBu_r',
        hovertemplate='月: %{y}月<br>カテゴリー: %{x}<br>売上: ¥%{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=title,
        xaxis_title="購入カテゴリー",
        yaxis_title="月"
    )
    
    return fig


def create_purchase_amount_distribution(df: pd.DataFrame, title: str = "購入金額分布") -> go.Figure:
    """購入金額の分布ヒストグラム"""
    fig = px.histogram(
        df,
        x='購入金額',
        nbins=50,
        title=title,
        color_discrete_sequence=['#ff7f0e']
    )
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="購入金額 (円)",
        yaxis_title="件数",
        bargap=0.1
    )
    
    return fig


def create_rfm_scatter_3d(rfm_df: pd.DataFrame, title: str = "RFM分析 3Dスコア") -> go.Figure:
    """RFM分析の3D散布図"""
    fig = px.scatter_3d(
        rfm_df,
        x='Recency',
        y='Frequency',
        z='Monetary',
        color='顧客セグメント',
        title=title,
        hover_data=['顧客ID', 'RFM_Score']
    )
    
    fig.update_layout(
        **PLOTLY_LAYOUT,
        scene=dict(
            xaxis_title='Recency (日)',
            yaxis_title='Frequency (回)',
            zaxis_title='Monetary (円)'
        )
    )
    
    return fig


def create_customer_segment_pie(rfm_df: pd.DataFrame, title: str = "顧客セグメント分布") -> go.Figure:
    """顧客セグメント分布円グラフ"""
    segment_counts = rfm_df['顧客セグメント'].value_counts().reset_index()
    segment_counts.columns = ['顧客セグメント', '顧客数']
    
    from src.config import CUSTOMER_SEGMENTS
    colors = [CUSTOMER_SEGMENTS.get(seg, {}).get('color', '#cccccc') for seg in segment_counts['顧客セグメント']]
    
    fig = px.pie(
        segment_counts,
        values='顧客数',
        names='顧客セグメント',
        title=title,
        color_discrete_sequence=colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    fig.update_layout(**PLOTLY_LAYOUT)
    
    return fig


def create_trend_with_moving_average(df: pd.DataFrame, title: str = "売上トレンド（移動平均付き）") -> go.Figure:
    """移動平均線付き売上トレンド"""
    daily_sales = df.groupby('購入日')['購入金額'].sum().reset_index()
    daily_sales = daily_sales.sort_values('購入日')
    
    # 7日移動平均
    daily_sales['MA_7'] = daily_sales['購入金額'].rolling(window=7, min_periods=1).mean()
    # 30日移動平均
    daily_sales['MA_30'] = daily_sales['購入金額'].rolling(window=30, min_periods=1).mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_sales['購入日'],
        y=daily_sales['購入金額'],
        name='実績',
        mode='lines',
        line=dict(color='lightgray', width=1),
        opacity=0.5
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_sales['購入日'],
        y=daily_sales['MA_7'],
        name='7日移動平均',
        mode='lines',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_sales['購入日'],
        y=daily_sales['MA_30'],
        name='30日移動平均',
        mode='lines',
        line=dict(color='#ff7f0e', width=2)
    ))
    
    layout_config = PLOTLY_LAYOUT.copy()
    layout_config.update({
        'title': title,
        'xaxis_title': "日付",
        'yaxis_title': "売上金額 (円)",
        'hovermode': 'x unified'
    })
    fig.update_layout(**layout_config)
    
    return fig

