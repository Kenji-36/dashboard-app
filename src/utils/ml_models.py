"""
機械学習モデル - 売上予測と顧客分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

def predict_sales_simple(df, days=30):
    """
    シンプルな移動平均による売上予測
    
    Parameters:
    -----------
    df : DataFrame
        購買データ
    days : int
        予測する日数
    
    Returns:
    --------
    DataFrame : 予測結果
    """
    try:
        # 日別売上を集計
        daily_sales = df.groupby(df['購入日'].dt.date)['購入金額'].sum().reset_index()
        daily_sales.columns = ['日付', '売上']
        daily_sales['日付'] = pd.to_datetime(daily_sales['日付'])
        daily_sales = daily_sales.sort_values('日付')
        
        # 移動平均の計算（7日、14日、30日）
        daily_sales['MA7'] = daily_sales['売上'].rolling(window=7, min_periods=1).mean()
        daily_sales['MA14'] = daily_sales['売上'].rolling(window=14, min_periods=1).mean()
        daily_sales['MA30'] = daily_sales['売上'].rolling(window=30, min_periods=1).mean()
        
        # 最新の移動平均を使用して予測
        last_date = daily_sales['日付'].max()
        last_ma7 = daily_sales['MA7'].iloc[-1]
        last_ma14 = daily_sales['MA14'].iloc[-1]
        last_ma30 = daily_sales['MA30'].iloc[-1]
        
        # 予測値の計算（3つの移動平均の加重平均）
        predicted_value = (last_ma7 * 0.5 + last_ma14 * 0.3 + last_ma30 * 0.2)
        
        # 予測データの作成
        future_dates = [last_date + timedelta(days=i+1) for i in range(days)]
        predictions = []
        
        for i, date in enumerate(future_dates):
            # トレンドを考慮（直近のトレンドを反映）
            if len(daily_sales) >= 7:
                recent_trend = (daily_sales['売上'].iloc[-1] - daily_sales['売上'].iloc[-7]) / 7
                trend_adjustment = recent_trend * (i + 1) * 0.3  # トレンドの影響を30%に抑える
            else:
                trend_adjustment = 0
            
            # 曜日効果を考慮
            weekday = date.weekday()
            weekday_factor = get_weekday_factor(df, weekday)
            
            # 予測値の計算
            base_prediction = predicted_value + trend_adjustment
            adjusted_prediction = base_prediction * weekday_factor
            
            # 信頼区間の計算（標準偏差を使用）
            std = daily_sales['売上'].std()
            lower_bound = max(0, adjusted_prediction - 1.96 * std)
            upper_bound = adjusted_prediction + 1.96 * std
            
            predictions.append({
                '日付': date,
                '予測売上': adjusted_prediction,
                '下限': lower_bound,
                '上限': upper_bound
            })
        
        predictions_df = pd.DataFrame(predictions)
        
        return daily_sales, predictions_df
    
    except Exception as e:
        st.error(f"予測エラー: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()


def get_weekday_factor(df, weekday):
    """
    曜日ごとの売上係数を計算
    
    Parameters:
    -----------
    df : DataFrame
        購買データ
    weekday : int
        曜日（0=月曜日, 6=日曜日）
    
    Returns:
    --------
    float : 曜日係数
    """
    try:
        df_copy = df.copy()
        df_copy['曜日'] = df_copy['購入日'].dt.weekday
        
        # 曜日別の平均売上
        weekday_avg = df_copy.groupby('曜日')['購入金額'].mean()
        overall_avg = df_copy['購入金額'].mean()
        
        if weekday in weekday_avg.index and overall_avg > 0:
            return weekday_avg[weekday] / overall_avg
        else:
            return 1.0
    except:
        return 1.0


def calculate_forecast_accuracy(actual, predicted):
    """
    予測精度の計算
    
    Parameters:
    -----------
    actual : array-like
        実際の値
    predicted : array-like
        予測値
    
    Returns:
    --------
    dict : 精度指標
    """
    try:
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # MAE (Mean Absolute Error)
        mae = np.mean(np.abs(actual - predicted))
        
        # RMSE (Root Mean Squared Error)
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # MAPE (Mean Absolute Percentage Error)
        mask = actual != 0
        mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        
        # R² Score
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            'MAE': mae,
            'RMSE': rmse,
            'MAPE': mape,
            'R2': r2
        }
    except Exception as e:
        return {
            'MAE': 0,
            'RMSE': 0,
            'MAPE': 0,
            'R2': 0
        }


def predict_customer_segment(df):
    """
    顧客セグメント予測（簡易版K-means風）
    
    Parameters:
    -----------
    df : DataFrame
        購買データ
    
    Returns:
    --------
    DataFrame : セグメント情報
    """
    try:
        # 顧客ごとの集計
        customer_stats = df.groupby('顧客ID').agg({
            '購入金額': ['sum', 'mean', 'count'],
            '購入日': ['min', 'max']
        }).reset_index()
        
        customer_stats.columns = ['顧客ID', '総購入金額', '平均購入金額', '購入回数', '初回購入日', '最終購入日']
        
        # Recency（最終購入からの経過日数）
        latest_date = df['購入日'].max()
        customer_stats['Recency'] = (latest_date - customer_stats['最終購入日']).dt.days
        
        # Frequency（購入回数）
        customer_stats['Frequency'] = customer_stats['購入回数']
        
        # Monetary（総購入金額）
        customer_stats['Monetary'] = customer_stats['総購入金額']
        
        # 正規化（0-1スケール）
        for col in ['Recency', 'Frequency', 'Monetary']:
            min_val = customer_stats[col].min()
            max_val = customer_stats[col].max()
            if max_val > min_val:
                customer_stats[f'{col}_normalized'] = (customer_stats[col] - min_val) / (max_val - min_val)
            else:
                customer_stats[f'{col}_normalized'] = 0.5
        
        # セグメント分類（簡易版）
        def classify_segment(row):
            r = row['Recency_normalized']
            f = row['Frequency_normalized']
            m = row['Monetary_normalized']
            
            # VIP: 最近購入、高頻度、高額
            if r < 0.3 and f > 0.7 and m > 0.7:
                return 'VIP'
            # 優良顧客: 最近購入、中〜高頻度、中〜高額
            elif r < 0.4 and f > 0.5 and m > 0.5:
                return '優良顧客'
            # 一般顧客: 平均的
            elif r < 0.6 and f > 0.3:
                return '一般顧客'
            # 要注意: 最近購入なし
            elif r > 0.6 and f > 0.3:
                return '要注意'
            # 休眠顧客: 長期間購入なし
            else:
                return '休眠顧客'
        
        customer_stats['セグメント'] = customer_stats.apply(classify_segment, axis=1)
        
        return customer_stats
    
    except Exception as e:
        st.error(f"セグメント予測エラー: {str(e)}")
        return pd.DataFrame()


def calculate_churn_probability(df):
    """
    顧客離脱確率の計算（簡易版）
    
    Parameters:
    -----------
    df : DataFrame
        購買データ
    
    Returns:
    --------
    DataFrame : 離脱確率情報
    """
    try:
        # 顧客ごとの統計
        customer_stats = df.groupby('顧客ID').agg({
            '購入日': ['min', 'max', 'count'],
            '購入金額': 'sum'
        }).reset_index()
        
        customer_stats.columns = ['顧客ID', '初回購入日', '最終購入日', '購入回数', '総購入金額']
        
        # 最終購入からの経過日数
        latest_date = df['購入日'].max()
        customer_stats['経過日数'] = (latest_date - customer_stats['最終購入日']).dt.days
        
        # 平均購入間隔
        customer_stats['顧客期間'] = (customer_stats['最終購入日'] - customer_stats['初回購入日']).dt.days
        customer_stats['平均購入間隔'] = customer_stats['顧客期間'] / customer_stats['購入回数'].replace(0, 1)
        
        # 離脱確率の計算（経過日数 / 平均購入間隔）
        customer_stats['離脱確率'] = (customer_stats['経過日数'] / customer_stats['平均購入間隔'].replace(0, 1)).clip(0, 1)
        
        # パーセンテージに変換
        customer_stats['離脱確率(%)'] = (customer_stats['離脱確率'] * 100).round(1)
        
        # リスクレベルの分類
        def classify_risk(prob):
            if prob >= 80:
                return '高リスク'
            elif prob >= 50:
                return '中リスク'
            else:
                return '低リスク'
        
        customer_stats['リスクレベル'] = customer_stats['離脱確率(%)'].apply(classify_risk)
        
        return customer_stats.sort_values('離脱確率(%)', ascending=False)
    
    except Exception as e:
        st.error(f"離脱確率計算エラー: {str(e)}")
        return pd.DataFrame()


def recommend_products(df, customer_id=None, top_n=5):
    """
    商品レコメンデーション（簡易版）
    
    Parameters:
    -----------
    df : DataFrame
        購買データ
    customer_id : str, optional
        顧客ID
    top_n : int
        推奨する商品数
    
    Returns:
    --------
    DataFrame : 推奨商品リスト
    """
    try:
        if customer_id:
            # 特定顧客の購入履歴
            customer_purchases = df[df['顧客ID'] == customer_id]['購入カテゴリー'].unique()
            
            # 同じカテゴリーを購入した他の顧客が買っている商品
            similar_customers = df[df['購入カテゴリー'].isin(customer_purchases)]['顧客ID'].unique()
            recommendations = df[
                (df['顧客ID'].isin(similar_customers)) &
                (~df['購入カテゴリー'].isin(customer_purchases))
            ]
        else:
            # 全体の人気商品
            recommendations = df
        
        # カテゴリー別の人気度
        category_popularity = recommendations.groupby('購入カテゴリー').agg({
            '購入金額': ['sum', 'count', 'mean']
        }).reset_index()
        
        category_popularity.columns = ['カテゴリー', '総売上', '購入回数', '平均購入金額']
        category_popularity['人気スコア'] = (
            category_popularity['総売上'] * 0.4 +
            category_popularity['購入回数'] * 1000 * 0.4 +
            category_popularity['平均購入金額'] * 0.2
        )
        
        return category_popularity.sort_values('人気スコア', ascending=False).head(top_n)
    
    except Exception as e:
        st.error(f"レコメンデーションエラー: {str(e)}")
        return pd.DataFrame()

