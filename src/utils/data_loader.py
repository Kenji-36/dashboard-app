"""
データ読み込みモジュール
"""
import pandas as pd
import streamlit as st
from datetime import datetime


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    CSVファイルからデータを読み込み、前処理を行う
    
    Args:
        file_path: CSVファイルのパス
        
    Returns:
        前処理済みのDataFrame
    """
    try:
        df = pd.read_csv(file_path)
        
        # 日付型に変換
        df['購入日'] = pd.to_datetime(df['購入日'])
        
        # 年月カラムを追加
        df['年月'] = df['購入日'].dt.to_period('M').astype(str)
        
        # 年カラムを追加
        df['年'] = df['購入日'].dt.year
        
        # 月カラムを追加
        df['月'] = df['購入日'].dt.month
        
        # 曜日カラムを追加
        df['曜日'] = df['購入日'].dt.day_name()
        df['曜日_日本語'] = df['購入日'].dt.dayofweek.map({
            0: '月曜日', 1: '火曜日', 2: '水曜日', 3: '木曜日',
            4: '金曜日', 5: '土曜日', 6: '日曜日'
        })
        
        # 四半期カラムを追加
        df['四半期'] = df['購入日'].dt.quarter
        
        return df
        
    except FileNotFoundError:
        st.error(f"❌ ファイルが見つかりません: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ データ読み込みエラー: {str(e)}")
        return pd.DataFrame()


def get_date_range(df: pd.DataFrame) -> tuple:
    """
    データの日付範囲を取得
    
    Args:
        df: DataFrame
        
    Returns:
        (最小日付, 最大日付)のタプル
    """
    if df.empty or '購入日' not in df.columns:
        return None, None
    
    return df['購入日'].min(), df['購入日'].max()


def get_unique_values(df: pd.DataFrame, column: str) -> list:
    """
    指定カラムのユニークな値を取得
    
    Args:
        df: DataFrame
        column: カラム名
        
    Returns:
        ユニークな値のリスト
    """
    if df.empty or column not in df.columns:
        return []
    
    return sorted(df[column].unique().tolist())

