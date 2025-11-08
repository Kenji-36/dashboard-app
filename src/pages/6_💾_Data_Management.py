"""
Phase 4 - データ管理ページ
データの表示、エクスポート、アップロード機能
"""

import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.data_loader import load_data
from src.utils.data_processor import filter_data
from src.components.filters import display_sidebar_filters
from src.utils.export import export_to_csv, export_to_excel, create_summary_report

# ページ設定
st.set_page_config(
    page_title="データ管理 | 購買データ分析ダッシュボード",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS読み込み
css_path = project_root / "src" / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# タイトル
st.title("💾 データ管理")
st.markdown("### データの表示、フィルタリング、エクスポート")

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
    
    # データ情報
    st.header("📊 データ概要")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("総レコード数", f"{len(df):,}")
    
    with col2:
        st.metric("フィルター後", f"{len(filtered_df):,}")
    
    with col3:
        st.metric("列数", len(filtered_df.columns))
    
    with col4:
        filter_rate = (len(filtered_df) / len(df) * 100) if len(df) > 0 else 0
        st.metric("フィルター率", f"{filter_rate:.1f}%")
    
    st.divider()
    
    # データプレビュー
    st.header("👀 データプレビュー")
    
    # 表示設定
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_rows = st.selectbox(
            "表示行数",
            [10, 25, 50, 100, 500, "全て"],
            index=1
        )
    
    with col2:
        sort_column = st.selectbox(
            "並び替え列",
            filtered_df.columns.tolist()
        )
    
    with col3:
        sort_order = st.radio(
            "並び順",
            ["降順", "昇順"],
            horizontal=True
        )
    
    # データの並び替え
    ascending = (sort_order == "昇順")
    sorted_df = filtered_df.sort_values(by=sort_column, ascending=ascending)
    
    # 表示行数の適用
    if show_rows == "全て":
        display_df = sorted_df
    else:
        display_df = sorted_df.head(show_rows)
    
    # データ表示
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    st.divider()
    
    # データ統計
    st.header("📈 データ統計")
    
    tab1, tab2, tab3 = st.tabs(["基本統計", "カテゴリー統計", "欠損値"])
    
    with tab1:
        st.subheader("数値列の基本統計")
        numeric_stats = filtered_df.describe()
        st.dataframe(numeric_stats, use_container_width=True)
    
    with tab2:
        st.subheader("カテゴリー列の統計")
        
        categorical_columns = ['性別', '地域', '購入カテゴリー', '支払方法']
        
        for col in categorical_columns:
            if col in filtered_df.columns:
                st.write(f"**{col}:**")
                value_counts = filtered_df[col].value_counts()
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.bar_chart(value_counts)
                
                with col2:
                    st.dataframe(
                        value_counts.to_frame(name='件数'),
                        use_container_width=True
                    )
                
                st.divider()
    
    with tab3:
        st.subheader("欠損値の確認")
        
        missing_data = filtered_df.isnull().sum()
        missing_percent = (missing_data / len(filtered_df) * 100).round(2)
        
        missing_df = pd.DataFrame({
            '欠損数': missing_data,
            '欠損率(%)': missing_percent
        })
        
        missing_df = missing_df[missing_df['欠損数'] > 0]
        
        if len(missing_df) > 0:
            st.warning("⚠️ 欠損値が検出されました")
            st.dataframe(missing_df, use_container_width=True)
        else:
            st.success("✅ 欠損値はありません")
    
    st.divider()
    
    # データエクスポート
    st.header("📤 データエクスポート")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("CSV エクスポート")
        
        csv_data = export_to_csv(filtered_df)
        
        st.download_button(
            label="📥 CSVダウンロード",
            data=csv_data,
            file_name=f"sales_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.caption(f"レコード数: {len(filtered_df):,}件")
    
    with col2:
        st.subheader("Excel エクスポート")
        
        excel_data = export_to_excel(filtered_df)
        
        st.download_button(
            label="📥 Excelダウンロード",
            data=excel_data,
            file_name=f"sales_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.caption("複数シート形式")
    
    with col3:
        st.subheader("サマリーレポート")
        
        report_data = create_summary_report(filtered_df)
        
        st.download_button(
            label="📥 レポートダウンロード",
            data=report_data,
            file_name=f"sales_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        st.caption("テキスト形式")
    
    st.divider()
    
    # データアップロード（将来の機能）
    st.header("📥 データアップロード")
    
    st.info("🚧 この機能は開発中です。将来のバージョンで利用可能になります。")
    
    with st.expander("📋 アップロード機能について"):
        st.markdown("""
        **予定されている機能:**
        - CSVファイルのアップロード
        - データバリデーション
        - 既存データとのマージ
        - データクレンジング
        - バックアップ機能
        
        **対応予定フォーマット:**
        - CSV (カンマ区切り)
        - Excel (.xlsx, .xls)
        - JSON
        """)
    
    # フッター
    st.divider()
    st.caption("💾 データ管理ページ | Phase 4")

except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
    st.exception(e)

# pandasのインポート（必要）
import pandas as pd

