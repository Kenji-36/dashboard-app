"""
KPIカードコンポーネント
"""
import streamlit as st
from src.config import KPI_ICONS


def display_kpi_cards(kpis: dict, comparison_kpis: dict = None):
    """
    KPIカードを表示
    
    Args:
        kpis: 現在のKPI値の辞書
        comparison_kpis: 比較用のKPI値の辞書（オプション）
    """
    # 4列のレイアウト
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        icon = KPI_ICONS.get('総売上', '💰')
        value = kpis.get('総売上', 0)
        delta = None
        if comparison_kpis:
            prev_value = comparison_kpis.get('総売上', 0)
            if prev_value > 0:
                delta = f"{((value - prev_value) / prev_value * 100):+.1f}%"
        
        st.metric(
            label=f"{icon} 総売上",
            value=f"¥{value:,.0f}",
            delta=delta
        )
    
    with col2:
        icon = KPI_ICONS.get('総顧客数', '👥')
        value = kpis.get('総顧客数', 0)
        delta = None
        if comparison_kpis:
            prev_value = comparison_kpis.get('総顧客数', 0)
            if prev_value > 0:
                delta = f"{value - prev_value:+.0f}人"
        
        st.metric(
            label=f"{icon} 総顧客数",
            value=f"{value:,}人",
            delta=delta
        )
    
    with col3:
        icon = KPI_ICONS.get('平均購入金額', '💳')
        value = kpis.get('平均購入金額', 0)
        delta = None
        if comparison_kpis:
            prev_value = comparison_kpis.get('平均購入金額', 0)
            if prev_value > 0:
                delta = f"{((value - prev_value) / prev_value * 100):+.1f}%"
        
        st.metric(
            label=f"{icon} 平均購入金額",
            value=f"¥{value:,.0f}",
            delta=delta
        )
    
    with col4:
        icon = KPI_ICONS.get('総取引件数', '🛒')
        value = kpis.get('総取引件数', 0)
        delta = None
        if comparison_kpis:
            prev_value = comparison_kpis.get('総取引件数', 0)
            if prev_value > 0:
                delta = f"{value - prev_value:+.0f}件"
        
        st.metric(
            label=f"{icon} 総取引件数",
            value=f"{value:,}件",
            delta=delta
        )
    
    # 2行目のKPI
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        icon = KPI_ICONS.get('平均年齢', '👤')
        value = kpis.get('平均年齢', 0)
        st.metric(
            label=f"{icon} 平均年齢",
            value=f"{value:.1f}歳"
        )
    
    with col6:
        icon = KPI_ICONS.get('リピート率', '🔄')
        value = kpis.get('リピート率', 0)
        st.metric(
            label=f"{icon} リピート率",
            value=f"{value:.1f}%"
        )
    
    with col7:
        # 最高購入金額
        if '最高購入金額' in kpis:
            st.metric(
                label="🏆 最高購入金額",
                value=f"¥{kpis['最高購入金額']:,.0f}"
            )
    
    with col8:
        # 最低購入金額
        if '最低購入金額' in kpis:
            st.metric(
                label="📊 最低購入金額",
                value=f"¥{kpis['最低購入金額']:,.0f}"
            )


def display_mini_kpi(label: str, value: str, icon: str = "📊"):
    """
    ミニKPIカードを表示
    
    Args:
        label: ラベル
        value: 値
        icon: アイコン
    """
    st.markdown(f"""
    <div style="
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f2f6;
        text-align: center;
        margin: 5px 0;
    ">
        <div style="font-size: 24px;">{icon}</div>
        <div style="font-size: 12px; color: #666;">{label}</div>
        <div style="font-size: 20px; font-weight: bold;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def display_comparison_metrics(current_kpis: dict, previous_kpis: dict, period_name: str = "前期"):
    """
    比較メトリクスを表示
    
    Args:
        current_kpis: 現在のKPI
        previous_kpis: 前期のKPI
        period_name: 期間名
    """
    st.subheader(f"📊 {period_name}比較")
    
    comparison_data = []
    
    for key in ['総売上', '総顧客数', '平均購入金額', '総取引件数']:
        if key in current_kpis and key in previous_kpis:
            current = current_kpis[key]
            previous = previous_kpis[key]
            
            if previous > 0:
                change = current - previous
                change_pct = (change / previous) * 100
                
                comparison_data.append({
                    '指標': key,
                    '現在': current,
                    period_name: previous,
                    '差分': change,
                    '変化率': f"{change_pct:+.1f}%"
                })
    
    if comparison_data:
        import pandas as pd
        df_comparison = pd.DataFrame(comparison_data)
        
        # 金額系の列をフォーマット
        for col in ['現在', period_name, '差分']:
            if col in df_comparison.columns:
                df_comparison[col] = df_comparison[col].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)

