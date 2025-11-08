"""
高度な分析モジュール - RFM分析、統計分析、予測分析
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.config import RFM_THRESHOLDS, CUSTOMER_SEGMENTS


def calculate_rfm(df: pd.DataFrame, reference_date: datetime = None) -> pd.DataFrame:
    """
    RFM分析を実行
    
    Args:
        df: DataFrame
        reference_date: 基準日（Noneの場合は最新の購入日）
        
    Returns:
        RFMスコアが追加されたDataFrame
    """
    if df.empty:
        return pd.DataFrame()
    
    # 基準日の設定
    if reference_date is None:
        reference_date = df['購入日'].max()
    
    # 顧客ごとのRFM指標を計算
    rfm = df.groupby('顧客ID').agg({
        '購入日': [lambda x: (reference_date - x.max()).days, 'count'],  # Recency, Frequency
        '購入金額': 'sum'  # Monetary
    })
    
    # カラム名を平坦化
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    rfm = rfm.reset_index()
    
    # RFMスコアを計算（1-5のスコア）
    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # スコアを数値型に変換
    rfm['R_Score'] = rfm['R_Score'].astype(int)
    rfm['F_Score'] = rfm['F_Score'].astype(int)
    rfm['M_Score'] = rfm['M_Score'].astype(int)
    
    # 総合RFMスコア
    rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
    
    # 顧客セグメント分類
    rfm['顧客セグメント'] = rfm['RFM_Score'].apply(classify_customer_segment)
    
    return rfm


def classify_customer_segment(rfm_score: int) -> str:
    """
    RFMスコアに基づいて顧客セグメントを分類
    
    Args:
        rfm_score: RFMスコア
        
    Returns:
        顧客セグメント名
    """
    if rfm_score >= 12:
        return 'VIP'
    elif rfm_score >= 9:
        return '優良顧客'
    elif rfm_score >= 6:
        return '一般顧客'
    elif rfm_score >= 3:
        return '要注意顧客'
    else:
        return '休眠顧客'


def calculate_customer_lifetime_value(df: pd.DataFrame) -> pd.DataFrame:
    """
    顧客生涯価値（CLV）を計算
    
    Args:
        df: DataFrame
        
    Returns:
        CLVが追加されたDataFrame
    """
    if df.empty:
        return pd.DataFrame()
    
    clv = df.groupby('顧客ID').agg({
        '購入金額': ['sum', 'mean', 'count'],
        '購入日': ['min', 'max']
    }).reset_index()
    
    clv.columns = ['顧客ID', '総購入金額', '平均購入金額', '購入回数', '初回購入日', '最終購入日']
    
    # 顧客期間（日数）
    clv['顧客期間_日'] = (clv['最終購入日'] - clv['初回購入日']).dt.days + 1
    
    # 購入頻度（日あたり）
    clv['購入頻度'] = clv['購入回数'] / clv['顧客期間_日']
    
    # 簡易CLV = 総購入金額 * 購入頻度
    clv['CLV'] = clv['総購入金額'] * (1 + clv['購入頻度'])
    
    return clv


def calculate_cohort_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    コホート分析を実行
    
    Args:
        df: DataFrame
        
    Returns:
        コホート分析結果のDataFrame
    """
    if df.empty:
        return pd.DataFrame()
    
    # 顧客の初回購入月を取得
    df_copy = df.copy()
    df_copy['購入月'] = df_copy['購入日'].dt.to_period('M')
    
    cohort = df_copy.groupby('顧客ID')['購入日'].min().reset_index()
    cohort.columns = ['顧客ID', '初回購入日']
    cohort['コホート'] = cohort['初回購入日'].dt.to_period('M')
    
    # 元のデータにコホート情報を結合
    df_copy = df_copy.merge(cohort[['顧客ID', 'コホート']], on='顧客ID')
    
    # コホート月からの経過月数を計算
    df_copy['コホート経過月'] = (df_copy['購入月'] - df_copy['コホート']).apply(lambda x: x.n)
    
    # コホートテーブルを作成
    cohort_data = df_copy.groupby(['コホート', 'コホート経過月'])['顧客ID'].nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index='コホート', columns='コホート経過月', values='顧客ID')
    
    # リテンション率を計算
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0) * 100
    
    return retention


def calculate_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    数値項目間の相関行列を計算
    
    Args:
        df: DataFrame
        
    Returns:
        相関行列
    """
    if df.empty:
        return pd.DataFrame()
    
    # 数値カラムのみを選択
    numeric_columns = ['年齢', '購入金額']
    
    if all(col in df.columns for col in numeric_columns):
        correlation = df[numeric_columns].corr()
        return correlation
    
    return pd.DataFrame()


def detect_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
    """
    異常値を検出
    
    Args:
        df: DataFrame
        column: 対象カラム
        method: 検出方法 ('iqr' or 'zscore')
        
    Returns:
        異常値フラグが追加されたDataFrame
    """
    if df.empty or column not in df.columns:
        return df
    
    df_copy = df.copy()
    
    if method == 'iqr':
        # IQR法
        Q1 = df_copy[column].quantile(0.25)
        Q3 = df_copy[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df_copy['異常値'] = (df_copy[column] < lower_bound) | (df_copy[column] > upper_bound)
        
    elif method == 'zscore':
        # Zスコア法
        mean = df_copy[column].mean()
        std = df_copy[column].std()
        z_scores = np.abs((df_copy[column] - mean) / std)
        
        df_copy['異常値'] = z_scores > 3
    
    return df_copy


def calculate_trend(df: pd.DataFrame, date_column: str, value_column: str, periods: int = 30) -> dict:
    """
    トレンド分析（移動平均と予測）
    
    Args:
        df: DataFrame
        date_column: 日付カラム
        value_column: 値カラム
        periods: 予測期間
        
    Returns:
        トレンド情報の辞書
    """
    if df.empty:
        return {}
    
    df_copy = df.copy()
    df_copy = df_copy.sort_values(date_column)
    
    # 日次集計
    daily_data = df_copy.groupby(date_column)[value_column].sum().reset_index()
    
    # 移動平均（7日、30日）
    daily_data['MA_7'] = daily_data[value_column].rolling(window=7, min_periods=1).mean()
    daily_data['MA_30'] = daily_data[value_column].rolling(window=30, min_periods=1).mean()
    
    # 簡易的な線形トレンド
    if len(daily_data) > 1:
        x = np.arange(len(daily_data))
        y = daily_data[value_column].values
        
        # 線形回帰
        coefficients = np.polyfit(x, y, 1)
        trend_line = np.poly1d(coefficients)
        
        daily_data['トレンド'] = trend_line(x)
        
        # 予測
        future_x = np.arange(len(daily_data), len(daily_data) + periods)
        predictions = trend_line(future_x)
        
        return {
            'data': daily_data,
            'trend_coefficient': coefficients[0],
            'predictions': predictions,
            'is_increasing': coefficients[0] > 0
        }
    
    return {'data': daily_data}


def calculate_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """
    季節性分析（月別パターン）
    
    Args:
        df: DataFrame
        
    Returns:
        月別の統計情報
    """
    if df.empty:
        return pd.DataFrame()
    
    df_copy = df.copy()
    
    # 月別集計
    monthly_stats = df_copy.groupby('月').agg({
        '購入金額': ['sum', 'mean', 'count'],
        '顧客ID': 'nunique'
    }).reset_index()
    
    monthly_stats.columns = ['月', '総売上', '平均購入金額', '取引件数', '顧客数']
    
    # 全体平均との比較
    overall_avg = df_copy['購入金額'].sum() / 12
    monthly_stats['平均比'] = (monthly_stats['総売上'] / overall_avg - 1) * 100
    
    return monthly_stats


def calculate_purchase_interval(df: pd.DataFrame) -> pd.DataFrame:
    """
    顧客の購入間隔を計算
    
    Args:
        df: DataFrame
        
    Returns:
        購入間隔の統計情報
    """
    if df.empty:
        return pd.DataFrame()
    
    df_copy = df.copy()
    df_copy = df_copy.sort_values(['顧客ID', '購入日'])
    
    # 顧客ごとの購入間隔を計算
    df_copy['前回購入日'] = df_copy.groupby('顧客ID')['購入日'].shift(1)
    df_copy['購入間隔_日'] = (df_copy['購入日'] - df_copy['前回購入日']).dt.days
    
    # 購入間隔の統計
    interval_stats = df_copy[df_copy['購入間隔_日'].notna()].groupby('顧客ID')['購入間隔_日'].agg([
        'mean', 'median', 'min', 'max', 'std'
    ]).reset_index()
    
    interval_stats.columns = ['顧客ID', '平均購入間隔', '中央値購入間隔', '最短間隔', '最長間隔', '標準偏差']
    
    return interval_stats


def generate_insights(df: pd.DataFrame, rfm_df: pd.DataFrame = None) -> dict:
    """
    データから自動的にインサイトを生成
    
    Args:
        df: DataFrame
        rfm_df: RFM分析結果のDataFrame
        
    Returns:
        インサイトの辞書
    """
    if df.empty:
        return {}
    
    insights = {}
    
    # 最も売上が高いカテゴリー
    category_sales = df.groupby('購入カテゴリー')['購入金額'].sum()
    insights['top_category'] = category_sales.idxmax()
    insights['top_category_sales'] = category_sales.max()
    
    # 最も購入金額が高い年齢層
    df_with_age = df.copy()
    df_with_age['年齢層'] = pd.cut(df_with_age['年齢'], bins=[0, 20, 30, 40, 50, 60, 100],
                                     labels=['10代', '20代', '30代', '40代', '50代', '60代以上'])
    age_sales = df_with_age.groupby('年齢層')['購入金額'].sum()
    insights['top_age_group'] = age_sales.idxmax()
    insights['top_age_group_sales'] = age_sales.max()
    
    # 最も利用されている支払方法
    payment_counts = df['支払方法'].value_counts()
    insights['top_payment_method'] = payment_counts.idxmax()
    insights['top_payment_count'] = payment_counts.max()
    
    # 売上が最も高い月
    monthly_sales = df.groupby('年月')['購入金額'].sum()
    insights['top_month'] = monthly_sales.idxmax()
    insights['top_month_sales'] = monthly_sales.max()
    
    # 地域別の特徴
    region_stats = df.groupby('地域').agg({
        '購入金額': ['sum', 'mean'],
        '顧客ID': 'nunique'
    })
    insights['region_stats'] = region_stats
    
    # RFM分析がある場合
    if rfm_df is not None and not rfm_df.empty:
        segment_counts = rfm_df['顧客セグメント'].value_counts()
        insights['customer_segments'] = segment_counts.to_dict()
        insights['vip_count'] = segment_counts.get('VIP', 0)
    
    return insights

