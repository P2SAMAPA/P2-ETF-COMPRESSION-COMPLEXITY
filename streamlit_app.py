import streamlit as st
import pandas as pd
import json
import plotly.express as px
from huggingface_hub import HfFileSystem
import config
from us_calendar import next_trading_day

st.set_page_config(page_title="Compression Complexity", layout="wide")
st.title("📚 Algorithmic Complexity via Compression")
st.caption("Normalised Compression Distance (zlib) | Lower ratio → more compressible → more predictable")

# Custom CSS
st.markdown("""
<style>
    .metric-card { background-color: #f0f2f6; padding: 0.5rem; border-radius: 0.5rem; text-align: center; }
    .good { color: green; }
    .medium { color: orange; }
    .bad { color: red; }
</style>
""", unsafe_allow_html=True)

OUTPUT_REPO = config.OUTPUT_REPO
HF_TOKEN = config.HF_TOKEN

@st.cache_data(ttl=3600)
def list_repo_files():
    fs = HfFileSystem(token=HF_TOKEN)
    try:
        files = [f['name'] for f in fs.ls(f"datasets/{OUTPUT_REPO}", detail=True, recursive=True) if f['type'] == 'file']
        return files
    except Exception as e:
        return [f"Error: {e}"]

def find_latest_json(files):
    json_files = [f for f in files if f.endswith('.json') and 'complexity' in f]
    if not json_files:
        return None
    json_files.sort(reverse=True)
    return json_files[0]

@st.cache_data(ttl=3600)
def load_json(path):
    fs = HfFileSystem(token=HF_TOKEN)
    try:
        with fs.open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

files = list_repo_files()
latest = find_latest_json(files)
if not latest:
    st.error("No complexity results found. Run trainer first.")
    st.stop()

data = load_json(latest)
if "error" in data:
    st.error(f"Error loading JSON: {data['error']}")
    st.stop()

st.sidebar.header("ℹ️ Info")
st.sidebar.write(f"**Run date:** {data['run_date']}")
st.sidebar.write(f"**Next trading day:** {next_trading_day()}")
st.sidebar.write("**Method:** zlib compression of log returns. Lower ratio = more compressible = more predictable.")

universes = data["universes"]
if not universes:
    st.warning("No universe data.")
    st.stop()

# ========== TOP PICKS PER UNIVERSE ==========
st.header("🎯 Most Predictable ETFs (Lowest Compression Ratio)")

for universe_name, uni_data in universes.items():
    top_picks = uni_data.get("top_picks", [])
    if not top_picks:
        continue
    st.subheader(f"📌 {universe_name}")
    cols = st.columns(min(len(top_picks), 3))
    for idx, pick in enumerate(top_picks):
        with cols[idx]:
            st.metric(pick["ticker"], f"{pick['compression_ratio']:.3f}", "compressible")
            st.caption(f"Rank #{pick['rank']}")
    st.divider()

# ========== DETAILED VIEW ==========
universe_names = list(universes.keys())
selected = st.selectbox("Select Universe for detailed view", universe_names)

if selected:
    uni_data = universes[selected]
    all_ratios = uni_data.get("all_ratios", {})
    if not all_ratios:
        st.info("No ratio data.")
    else:
        # Sort by ratio ascending for display
        sorted_ratios = sorted(all_ratios.items(), key=lambda x: x[1])
        df = pd.DataFrame(sorted_ratios, columns=["ETF", "Compression Ratio"])
        st.subheader(f"📊 Compression Ratios – {selected}")
        st.caption("Lower ratio = more compressible (more predictable).")
        fig = px.bar(df, x="ETF", y="Compression Ratio", title="Compression Ratio per ETF",
                     color="Compression Ratio", color_continuous_scale="viridis_r")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top 5 Most Predictable")
        st.dataframe(df.head(5), hide_index=True, use_container_width=True)

st.caption("Interpretation: Low compression ratio suggests repetitive/patterned behaviour – potential inefficiency. Not directional.")
