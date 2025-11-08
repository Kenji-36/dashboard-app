"""
フィルターコンポーネント
"""
import streamlit as st
from datetime import datetime, timedelta


def display_sidebar_filters(df, key_prefix: str = ""):
    """
    サイドバーにフィルターを表示
    
    Args:
        df: DataFrame
        key_prefix: セッションステートのキープレフィックス
        
    Returns:
        フィルター条件の辞書
    """
    st.sidebar.header("🔍 フィルター設定")
    
    filters = {}
    
    # 日付範囲フィルター
    st.sidebar.subheader("📅 期間")
    min_date = df['購入日'].min().date()
    max_date = df['購入日'].max().date()
    
    date_range = st.sidebar.date_input(
        "期間を選択",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key=f"{key_prefix}date_range"
    )
    
    if len(date_range) == 2:
        filters['date_range'] = date_range
    else:
        filters['date_range'] = (min_date, max_date)
    
    # クイック期間選択
    st.sidebar.markdown("**クイック選択**")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📅 今月", key=f"{key_prefix}this_month"):
            today = datetime.now().date()
            first_day = today.replace(day=1)
            filters['date_range'] = (first_day, today)
    
    with col2:
        if st.button("📅 先月", key=f"{key_prefix}last_month"):
            today = datetime.now().date()
            first_day_this_month = today.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            first_day_last_month = last_day_last_month.replace(day=1)
            filters['date_range'] = (first_day_last_month, last_day_last_month)
    
    col3, col4 = st.sidebar.columns(2)
    
    with col3:
        if st.button("📅 直近30日", key=f"{key_prefix}last_30_days"):
            today = datetime.now().date()
            filters['date_range'] = (today - timedelta(days=30), today)
    
    with col4:
        if st.button("📅 直近90日", key=f"{key_prefix}last_90_days"):
            today = datetime.now().date()
            filters['date_range'] = (today - timedelta(days=90), today)
    
    st.sidebar.markdown("---")
    
    # 地域フィルター
    st.sidebar.subheader("🗾 地域")
    regions = sorted(df['地域'].unique().tolist())
    selected_regions = st.sidebar.multiselect(
        "地域を選択",
        options=regions,
        default=regions,
        key=f"{key_prefix}regions"
    )
    filters['regions'] = selected_regions if selected_regions else regions
    
    # 性別フィルター
    st.sidebar.subheader("👥 性別")
    genders = sorted(df['性別'].unique().tolist())
    selected_genders = st.sidebar.multiselect(
        "性別を選択",
        options=genders,
        default=genders,
        key=f"{key_prefix}genders"
    )
    filters['genders'] = selected_genders if selected_genders else genders
    
    # カテゴリーフィルター
    st.sidebar.subheader("🏷️ 購入カテゴリー")
    categories = sorted(df['購入カテゴリー'].unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "カテゴリーを選択",
        options=categories,
        default=categories,
        key=f"{key_prefix}categories"
    )
    filters['categories'] = selected_categories if selected_categories else categories
    
    # 支払方法フィルター
    st.sidebar.subheader("💳 支払方法")
    payment_methods = sorted(df['支払方法'].unique().tolist())
    selected_payment_methods = st.sidebar.multiselect(
        "支払方法を選択",
        options=payment_methods,
        default=payment_methods,
        key=f"{key_prefix}payment_methods"
    )
    filters['payment_methods'] = selected_payment_methods if selected_payment_methods else payment_methods
    
    # 年齢範囲フィルター
    st.sidebar.subheader("👤 年齢")
    min_age = int(df['年齢'].min())
    max_age = int(df['年齢'].max())
    
    age_range = st.sidebar.slider(
        "年齢範囲",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age),
        key=f"{key_prefix}age_range"
    )
    filters['age_range'] = age_range
    
    st.sidebar.markdown("---")
    
    # フィルターリセットボタン
    if st.sidebar.button("🔄 フィルターをリセット", key=f"{key_prefix}reset"):
        st.rerun()
    
    return filters


def display_filter_summary(filters: dict, filtered_count: int, total_count: int):
    """
    適用されているフィルターのサマリーを表示
    
    Args:
        filters: フィルター条件の辞書
        filtered_count: フィルター後のレコード数
        total_count: 全レコード数
    """
    st.markdown("### 📋 フィルター適用状況")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("表示中のレコード", f"{filtered_count:,}件")
    
    with col2:
        st.metric("全レコード", f"{total_count:,}件")
    
    with col3:
        percentage = (filtered_count / total_count * 100) if total_count > 0 else 0
        st.metric("表示割合", f"{percentage:.1f}%")
    
    # フィルター詳細
    with st.expander("🔍 適用中のフィルター詳細"):
        if 'date_range' in filters:
            st.write(f"**期間:** {filters['date_range'][0]} 〜 {filters['date_range'][1]}")
        
        if 'regions' in filters and filters['regions']:
            st.write(f"**地域:** {', '.join(filters['regions'])}")
        
        if 'genders' in filters and filters['genders']:
            st.write(f"**性別:** {', '.join(filters['genders'])}")
        
        if 'categories' in filters and filters['categories']:
            st.write(f"**カテゴリー:** {', '.join(filters['categories'])}")
        
        if 'payment_methods' in filters and filters['payment_methods']:
            st.write(f"**支払方法:** {', '.join(filters['payment_methods'])}")
        
        if 'age_range' in filters:
            st.write(f"**年齢範囲:** {filters['age_range'][0]}歳 〜 {filters['age_range'][1]}歳")

