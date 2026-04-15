"""
株式スクリーニングアプリ - ホームページ
"""
import streamlit as st

st.set_page_config(
    page_title="株式スクリーニング",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📈 株式スクリーニング")
st.caption("日本株・米国株 | 財務指標フィルタリング + Claude AI 分析")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🇯🇵 日本株スクリーニング
    東証上場銘柄をPER・PBR・ROE・自己資本比率など
    日本株特有の指標でスクリーニング。

    **対応指標**
    - PER / PBR / EV/EBITDA
    - ROE / ROA / 営業利益率
    - 自己資本比率 (財務健全性)
    - 配当利回り / 配当性向
    - 売上高成長率 / 利益成長率
    """)
    if st.button("日本株スクリーニングへ →", type="primary", use_container_width=True):
        st.switch_page("pages/1_🇯🇵_日本株.py")

with col2:
    st.markdown("""
    ### 🇺🇸 米国株スクリーニング
    NYSE/NASDAQ上場銘柄をP/E・PEG・D/Eレシオなど
    米国株に最適な指標でスクリーニング。

    **対応指標**
    - P/E / P/B / PEG Ratio
    - ROE / ROA / 営業利益率
    - D/E Ratio (財務レバレッジ)
    - 配当利回り / EPS成長率
    - 売上高成長率
    """)
    if st.button("米国株スクリーニングへ →", type="primary", use_container_width=True):
        st.switch_page("pages/2_🇺🇸_米国株.py")

st.markdown("---")

st.markdown("""
### 🤖 AI 分析機能 (Claude)
銘柄詳細画面から「AI 分析を実行」ボタンで、Anthropic Claude による財務分析レポートを生成します。

- 財務データの総合サマリー
- **強み** と **リスク要因** の列挙
- **強気 / 中立 / 弱気** の投資判断
- prompt caching でAPI コスト最適化

> ⚠️ 本アプリは情報提供目的のみです。投資判断はご自身の責任で行ってください。
""")

with st.sidebar:
    st.markdown("### セットアップ")
    has_key = bool(st.secrets.get("ANTHROPIC_API_KEY", ""))
    if has_key:
        st.success("✅ ANTHROPIC_API_KEY 設定済み")
    else:
        st.warning("⚠️ ANTHROPIC_API_KEY 未設定\nAI分析は利用できません")
        st.code("# .streamlit/secrets.toml\nANTHROPIC_API_KEY = \"sk-ant-...\"", language="toml")
