"""
データ処理モジュール - フィルタリング、集計、変換など
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.config import AGE_BINS, AGE_LABELS


def filter_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    フィルター条件に基づいてデータをフィルタリング
    
    Args:
        df: 元のDataFrame
        filters: フィルター条件の辞書
        
    Returns:
        フィルタリング済みのDataFrame
    """
    filtered_df = df.copy()
    
    # 日付範囲フィルター
    if 'date_range' in filters and filters['date_range']:
        start_date, end_date = filters['date_range']
        filtered_df = filtered_df[
            (filtered_df['購入日'] >= pd.Timestamp(start_date)) &
            (filtered_df['購入日'] <= pd.Timestamp(end_date))
        ]
    
    # 地域フィルター
    if 'regions' in filters and filters['regions']:
        filtered_df = filtered_df[filtered_df['地域'].isin(filters['regions'])]
    
    # 性別フィルター
    if 'genders' in filters and filters['genders']:
        filtered_df = filtered_df[filtered_df['性別'].isin(filters['genders'])]
    
    # カテゴリーフィルター
    if 'categories' in filters and filters['categories']:
        filtered_df = filtered_df[filtered_df['購入カテゴリー'].isin(filters['categories'])]
    
    # 支払方法フィルター
    if 'payment_methods' in filters and filters['payment_methods']:
        filtered_df = filtered_df[filtered_df['支払方法'].isin(filters['payment_methods'])]
    
    # 年齢範囲フィルター
    if 'age_range' in filters and filters['age_range']:
        min_age, max_age = filters['age_range']
        filtered_df = filtered_df[
            (filtered_df['年齢'] >= min_age) &
            (filtered_df['年齢'] <= max_age)
        ]
    
    return filtered_df


def add_age_group(df: pd.DataFrame) -> pd.DataFrame:
    """
    年齢層カラムを追加
    
    Args:
        df: DataFrame
        
    Returns:
        年齢層カラムが追加されたDataFrame
    """
    df_copy = df.copy()
    df_copy['年齢層'] = pd.cut(
        df_copy['年齢'],
        bins=AGE_BINS,
        labels=AGE_LABELS,
        include_lowest=True
    )
    return df_copy


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    主要なKPIを計算
    
    Args:
        df: DataFrame
        
    Returns:
        KPI値の辞書
    """
    if df.empty:
        return {
            '総売上': 0,
            '総顧客数': 0,
            '平均購入金額': 0,
            '総取引件数': 0,
            '平均年齢': 0,
            'リピート率': 0,
        }
    
    # 顧客ごとの購入回数を計算
    customer_purchases = df.groupby('顧客ID').size()
    repeat_customers = (customer_purchases > 1).sum()
    
    kpis = {
        '総売上': df['購入金額'].sum(),
        '総顧客数': df['顧客ID'].nunique(),
        '平均購入金額': df['購入金額'].mean(),
        '総取引件数': len(df),
        '平均年齢': df['年齢'].mean(),
        'リピート率': (repeat_customers / df['顧客ID'].nunique() * 100) if df['顧客ID'].nunique() > 0 else 0,
    }
    
    return kpis


def aggregate_by_period(df: pd.DataFrame, period: str = 'M') -> pd.DataFrame:
    """
    期間ごとに売上を集計
    
    Args:
        df: DataFrame
        period: 集計期間 ('D': 日, 'W': 週, 'M': 月, 'Q': 四半期, 'Y': 年)
        
    Returns:
        集計されたDataFrame
    """
    if df.empty:
        return pd.DataFrame()
    
    df_copy = df.copy()
    df_copy = df_copy.set_index('購入日')
    
    aggregated = df_copy.resample(period).agg({
        '購入金額': ['sum', 'mean', 'count'],
        '顧客ID': 'nunique'
    }).reset_index()
    
    aggregated.columns = ['日付', '総売上', '平均購入金額', '取引件数', '顧客数']
    
    return aggregated


def calculate_moving_average(df: pd.DataFrame, column: str, window: int = 7) -> pd.Series:
    """
    移動平均を計算
    
    Args:
        df: DataFrame
        column: 対象カラム
        window: 移動平均の期間
        
    Returns:
        移動平均のSeries
    """
    return df[column].rolling(window=window, min_periods=1).mean()


def get_top_n(df: pd.DataFrame, group_by: str, value_column: str, n: int = 10) -> pd.DataFrame:
    """
    上位N件を取得
    
    Args:
        df: DataFrame
        group_by: グループ化するカラム
        value_column: 集計するカラム
        n: 取得件数
        
    Returns:
        上位N件のDataFrame
    """
    if df.empty:
        return pd.DataFrame()
    
    result = df.groupby(group_by)[value_column].sum().reset_index()
    result = result.sort_values(value_column, ascending=False).head(n)
    
    return result


def calculate_growth_rate(df: pd.DataFrame, period_column: str, value_column: str) -> pd.DataFrame:
    """
    成長率を計算
    
    Args:
        df: DataFrame
        period_column: 期間カラム
        value_column: 値カラム
        
    Returns:
        成長率が追加されたDataFrame
    """
    if df.empty:
        return pd.DataFrame()
    
    df_copy = df.copy()
    df_copy = df_copy.sort_values(period_column)
    df_copy['前期比'] = df_copy[value_column].pct_change() * 100
    df_copy['前期差'] = df_copy[value_column].diff()
    
    return df_copy


def create_pivot_table(df: pd.DataFrame, index: str, columns: str, values: str, aggfunc: str = 'sum') -> pd.DataFrame:
    """
    ピボットテーブルを作成
    
    Args:
        df: DataFrame
        index: 行のカラム
        columns: 列のカラム
        values: 値のカラム
        aggfunc: 集計関数
        
    Returns:
        ピボットテーブル
    """
    if df.empty:
        return pd.DataFrame()
    
    pivot = pd.pivot_table(
        df,
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc,
        fill_value=0
    )
    
    return pivot

