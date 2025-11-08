"""
エクスポート機能モジュール - CSV/Excel/画像のエクスポート
"""
import pandas as pd
import io
from datetime import datetime
from src.config import EXPORT_CONFIG


def export_to_csv(df: pd.DataFrame, filename: str = None) -> bytes:
    """
    DataFrameをCSVにエクスポート
    
    Args:
        df: DataFrame
        filename: ファイル名（省略時は自動生成）
        
    Returns:
        CSVデータ（bytes）
    """
    if filename is None:
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    csv_data = df.to_csv(index=False, encoding=EXPORT_CONFIG['csv_encoding'])
    return csv_data.encode(EXPORT_CONFIG['csv_encoding'])


def export_to_excel(dataframes: dict, filename: str = None) -> bytes:
    """
    複数のDataFrameをExcelの複数シートにエクスポート
    
    Args:
        dataframes: {シート名: DataFrame}の辞書
        filename: ファイル名（省略時は自動生成）
        
    Returns:
        Excelデータ（bytes）
    """
    if filename is None:
        filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine=EXPORT_CONFIG['excel_engine']) as writer:
        for sheet_name, df in dataframes.items():
            # シート名の長さ制限（Excelは31文字まで）
            safe_sheet_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
    
    output.seek(0)
    return output.getvalue()


def create_summary_report(df: pd.DataFrame, kpis: dict, insights: dict) -> pd.DataFrame:
    """
    サマリーレポートを作成
    
    Args:
        df: DataFrame
        kpis: KPI辞書
        insights: インサイト辞書
        
    Returns:
        レポートDataFrame
    """
    report_data = []
    
    # KPIセクション
    report_data.append(['=== 主要指標 ===', ''])
    for key, value in kpis.items():
        if isinstance(value, float):
            report_data.append([key, f'{value:,.2f}'])
        else:
            report_data.append([key, f'{value:,}'])
    
    report_data.append(['', ''])
    
    # インサイトセクション
    report_data.append(['=== インサイト ===', ''])
    if 'top_category' in insights:
        report_data.append(['最も売上が高いカテゴリー', insights['top_category']])
        report_data.append(['  売上金額', f"¥{insights['top_category_sales']:,.0f}"])
    
    if 'top_age_group' in insights:
        report_data.append(['最も購入金額が高い年齢層', insights['top_age_group']])
    
    if 'top_payment_method' in insights:
        report_data.append(['最も利用されている支払方法', insights['top_payment_method']])
    
    if 'top_month' in insights:
        report_data.append(['売上が最も高い月', insights['top_month']])
    
    report_data.append(['', ''])
    report_data.append(['レポート作成日時', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    
    report_df = pd.DataFrame(report_data, columns=['項目', '値'])
    
    return report_df


def prepare_export_data(df: pd.DataFrame, include_analysis: bool = True) -> dict:
    """
    エクスポート用のデータを準備
    
    Args:
        df: DataFrame
        include_analysis: 分析シートを含めるかどうか
        
    Returns:
        {シート名: DataFrame}の辞書
    """
    export_dict = {}
    
    # メインデータ
    export_dict['購入データ'] = df.copy()
    
    if include_analysis:
        # カテゴリー別集計
        category_summary = df.groupby('購入カテゴリー').agg({
            '購入金額': ['sum', 'mean', 'count'],
            '顧客ID': 'nunique'
        }).reset_index()
        category_summary.columns = ['購入カテゴリー', '総売上', '平均購入金額', '購入件数', '顧客数']
        export_dict['カテゴリー別集計'] = category_summary
        
        # 地域別集計
        region_summary = df.groupby('地域').agg({
            '購入金額': ['sum', 'mean', 'count'],
            '顧客ID': 'nunique'
        }).reset_index()
        region_summary.columns = ['地域', '総売上', '平均購入金額', '購入件数', '顧客数']
        export_dict['地域別集計'] = region_summary
        
        # 月別集計
        if '年月' in df.columns:
            monthly_summary = df.groupby('年月').agg({
                '購入金額': ['sum', 'mean', 'count'],
                '顧客ID': 'nunique'
            }).reset_index()
            monthly_summary.columns = ['年月', '総売上', '平均購入金額', '購入件数', '顧客数']
            export_dict['月別集計'] = monthly_summary
    
    return export_dict


def format_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    DataFrameを表示用にフォーマット
    
    Args:
        df: DataFrame
        
    Returns:
        フォーマット済みDataFrame
    """
    df_display = df.copy()
    
    # 金額カラムをフォーマット
    money_columns = ['購入金額', '総売上', '平均購入金額', 'Monetary', '総購入金額']
    for col in money_columns:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f'¥{x:,.0f}' if pd.notna(x) else '')
    
    # 日付カラムをフォーマット
    date_columns = ['購入日', '初回購入日', '最終購入日']
    for col in date_columns:
        if col in df_display.columns:
            df_display[col] = pd.to_datetime(df_display[col]).dt.strftime('%Y-%m-%d')
    
    # パーセンテージカラムをフォーマット
    percentage_columns = ['リピート率', '前期比', '平均比']
    for col in percentage_columns:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: f'{x:.1f}%' if pd.notna(x) else '')
    
    return df_display

