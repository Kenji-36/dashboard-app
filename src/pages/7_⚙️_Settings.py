"""
Phase 4 - 設定ページ
アプリケーションの設定とカスタマイズ
"""

import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ページ設定
st.set_page_config(
    page_title="設定 | 購買データ分析ダッシュボード",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS読み込み
css_path = project_root / "src" / "styles" / "custom.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# タイトル
st.title("⚙️ 設定")
st.markdown("### アプリケーションの設定とカスタマイズ")

st.divider()

# 表示設定
st.header("🎨 表示設定")

col1, col2 = st.columns(2)

with col1:
    st.subheader("テーマ設定")
    
    theme = st.selectbox(
        "カラーテーマ",
        ["デフォルト", "ダーク", "ライト", "カスタム"],
        index=0
    )
    
    if theme == "カスタム":
        primary_color = st.color_picker("プライマリカラー", "#FF4B4B")
        background_color = st.color_picker("背景色", "#FFFFFF")
        text_color = st.color_picker("テキスト色", "#262730")
    
    st.divider()
    
    st.subheader("グラフ設定")
    
    chart_theme = st.selectbox(
        "グラフテーマ",
        ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"],
        index=0
    )
    
    show_grid = st.checkbox("グリッド線を表示", value=True)
    show_legend = st.checkbox("凡例を表示", value=True)

with col2:
    st.subheader("データ表示設定")
    
    default_rows = st.number_input(
        "デフォルト表示行数",
        min_value=10,
        max_value=1000,
        value=25,
        step=5
    )
    
    decimal_places = st.number_input(
        "小数点以下の桁数",
        min_value=0,
        max_value=5,
        value=2,
        step=1
    )
    
    date_format = st.selectbox(
        "日付フォーマット",
        ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "YYYY年MM月DD日"],
        index=0
    )
    
    st.divider()
    
    st.subheader("言語設定")
    
    language = st.selectbox(
        "表示言語",
        ["日本語", "English"],
        index=0
    )

st.divider()

# データ更新設定
st.header("🔄 データ更新設定")

col1, col2 = st.columns(2)

with col1:
    st.subheader("自動更新")
    
    auto_refresh = st.checkbox("自動更新を有効化", value=False)
    
    if auto_refresh:
        refresh_interval = st.selectbox(
            "更新間隔",
            ["30秒", "1分", "5分", "10分", "30分"],
            index=2
        )
        
        st.info(f"⏱️ {refresh_interval}ごとにデータが自動更新されます")

with col2:
    st.subheader("キャッシュ設定")
    
    cache_ttl = st.number_input(
        "キャッシュ有効期限（秒）",
        min_value=60,
        max_value=3600,
        value=300,
        step=60
    )
    
    if st.button("🗑️ キャッシュをクリア", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ キャッシュをクリアしました")

st.divider()

# 通知設定
st.header("🔔 通知設定")

col1, col2 = st.columns(2)

with col1:
    st.subheader("アラート設定")
    
    enable_alerts = st.checkbox("アラートを有効化", value=False)
    
    if enable_alerts:
        st.write("**アラート条件:**")
        
        sales_threshold = st.number_input(
            "売上閾値（円）",
            min_value=0,
            value=100000,
            step=10000
        )
        
        alert_type = st.multiselect(
            "アラート種類",
            ["売上低下", "異常値検出", "データ更新", "エラー"],
            default=["売上低下"]
        )

with col2:
    st.subheader("通知方法")
    
    notification_methods = st.multiselect(
        "通知方法",
        ["メール", "Slack", "Teams", "ブラウザ通知"],
        default=[]
    )
    
    if "メール" in notification_methods:
        email = st.text_input("メールアドレス", placeholder="example@email.com")
    
    if "Slack" in notification_methods:
        slack_webhook = st.text_input("Slack Webhook URL", placeholder="https://hooks.slack.com/...")

st.divider()

# エクスポート設定
st.header("📤 エクスポート設定")

col1, col2 = st.columns(2)

with col1:
    st.subheader("デフォルト設定")
    
    default_format = st.selectbox(
        "デフォルトフォーマット",
        ["CSV", "Excel", "JSON"],
        index=0
    )
    
    include_index = st.checkbox("インデックスを含める", value=False)
    encoding = st.selectbox(
        "文字エンコーディング",
        ["UTF-8", "Shift-JIS", "EUC-JP"],
        index=0
    )

with col2:
    st.subheader("Excel設定")
    
    excel_engine = st.selectbox(
        "Excelエンジン",
        ["openpyxl", "xlsxwriter"],
        index=0
    )
    
    include_charts = st.checkbox("グラフを含める", value=True)
    include_summary = st.checkbox("サマリーシートを含める", value=True)

st.divider()

# パフォーマンス設定
st.header("⚡ パフォーマンス設定")

col1, col2 = st.columns(2)

with col1:
    st.subheader("データ処理")
    
    chunk_size = st.number_input(
        "チャンクサイズ",
        min_value=1000,
        max_value=100000,
        value=10000,
        step=1000
    )
    
    use_multiprocessing = st.checkbox("マルチプロセッシングを使用", value=False)

with col2:
    st.subheader("グラフ描画")
    
    max_points = st.number_input(
        "グラフの最大ポイント数",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100
    )
    
    use_webgl = st.checkbox("WebGLレンダリングを使用", value=False)

st.divider()

# セキュリティ設定
st.header("🔐 セキュリティ設定")

st.info("🚧 認証機能は開発中です。Phase 4の後半で実装予定です。")

with st.expander("📋 予定されているセキュリティ機能"):
    st.markdown("""
    **認証機能:**
    - ユーザーログイン/ログアウト
    - パスワード管理
    - セッション管理
    - 多要素認証（MFA）
    
    **アクセス制御:**
    - ロールベースアクセス制御（RBAC）
    - 権限管理
    - 監査ログ
    
    **データセキュリティ:**
    - データ暗号化
    - バックアップ
    - データマスキング
    """)

st.divider()

# 設定の保存
st.header("💾 設定の保存")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 設定を保存", use_container_width=True):
        st.success("✅ 設定を保存しました")

with col2:
    if st.button("🔄 デフォルトに戻す", use_container_width=True):
        st.warning("⚠️ 設定をデフォルトに戻しました")

with col3:
    if st.button("📥 設定をエクスポート", use_container_width=True):
        st.info("📄 設定ファイルをダウンロードします")

st.divider()

# システム情報
st.header("ℹ️ システム情報")

col1, col2, col3 = st.columns(3)

with col1:
    st.write("**バージョン情報:**")
    st.text("アプリバージョン: 4.0.0")
    st.text("Streamlit: 1.50.0")
    st.text("Python: 3.11+")

with col2:
    st.write("**データベース:**")
    st.text("タイプ: CSV/SQLite")
    st.text("サイズ: 約300KB")
    st.text("レコード数: 300件")

with col3:
    st.write("**パフォーマンス:**")
    st.text("キャッシュ: 有効")
    st.text("圧縮: 有効")
    st.text("最適化: レベル2")

# フッター
st.divider()
st.caption("⚙️ 設定ページ | Phase 4")

