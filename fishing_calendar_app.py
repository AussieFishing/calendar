import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

# ================== ZONES (unchanged from previous) ==================
zones = {
    "Sydney": "NSW East", "Newcastle": "NSW East", "Wollongong": "NSW East",
    "Brisbane": "QLD South", "Gold Coast": "QLD South", "Sunshine Coast": "QLD South",
    "Cairns": "QLD North", "Townsville": "QLD North",
    "Darwin": "NT",
    "Perth": "WA", "Fremantle": "WA",
    "Melbourne": "VIC South", "Geelong": "VIC South",
    "Adelaide": "SA",
    "Hobart": "TAS",
    "Other / National": "National (default)"
}

# ================== LOAD ALL DATA ==================
@st.cache_data
def load_data():
    try:
        loc_df = pd.read_csv("locations.csv")
        fish_df = pd.read_csv("fishing_data.csv")
        gear_df = pd.read_csv("gear_data.csv")
        return loc_df, fish_df, gear_df
    except FileNotFoundError as e:
        st.error(f"Missing file: {e}. Ensure locations.csv, fishing_data.csv, and gear_data.csv exist.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

locations_df, fishing_df, gear_df = load_data()

# ================== APP ==================
st.set_page_config(page_title="Aussie Fishing Calendar", layout="wide")
st.title("🎣 Australian Fishing Calendar – Specific Locations & Gear")

st.markdown("Search a specific spot, pick a date, and get compliant rules + targeted gear setups. **Always verify with FishSmart app / DPI site** before heading out.")

col1, col2 = st.columns([2, 1])

with col1:
    location_list = sorted(locations_df['location_name'].tolist())
    selected_location = st.selectbox(
        "🔍 Search location/estuary (e.g. Preddy’s Wharf)",
        options=location_list,
        index=0
    )

with col2:
    selected_date = st.date_input("Pick a Date", value=datetime.today())

# Derive details
loc_row = locations_df[locations_df['location_name'] == selected_location].iloc[0]
zone = loc_row['zone']
month_name = calendar.month_name[selected_date.month]

# Filter species for zone + month
filtered_species = fishing_df[
    (fishing_df['month'] == month_name) &
    (fishing_df['zone'].str.contains(zone.split(' (')[0]))
]

st.subheader(f"📍 {selected_location} — {month_name} {selected_date.year}")
st.info(f"**Zone:** {zone}")

# Rules / Warnings
st.markdown("### ⚠️ DPI & Reserve Rules")
st.markdown(f"**Closures:** {loc_row['closure_notes']}")
st.markdown(f"**Marine/Aquatic Reserve:** {loc_row['reserve_notes']}")
st.markdown(f"[Official DPI info]({loc_row['official_link']})")

st.markdown("---")

if filtered_species.empty:
    st.warning("No species data for this zone/month – expand fishing_data.csv.")
else:
    st.subheader("🐟 Target Species & Recommended Gear Setups")
    st.caption("Gear is general/recommended for the species — adjust for conditions. Check bag/size limits.")

    for _, row in filtered_species.iterrows():
        species = row['species']
        
        # Match gear
        gear_match = gear_df[gear_df['species'].str.lower() == species.lower()]
        if not gear_match.empty:
            gear = gear_match.iloc[0]
        else:
            gear = None  # fallback if species missing in gear file

        with st.expander(f"{species} ({row['rating']})"):
            st.markdown(f"**Best times (general):** {row['best_times_notes']}")
            st.markdown(f"**Gear/Rig Notes:** {row['gear_rig']}")

            if gear is not None:
                st.markdown("**Recommended Setup:**")
                st.markdown(f"- **Rod:** {gear['rod']}")
                st.markdown(f"- **Reel:** {gear['reel']}")
                st.markdown(f"- **Line/Leader:** {gear['line_leader_weight']}")
                st.markdown(f"- **Rig:** {gear['rig']}")
                st.markdown(f"- **Bait/Lure:** {gear['bait_or_lure']}")
            else:
                st.caption("Gear details not yet added for this species – update gear_data.csv.")

            st.markdown("---")

# Sidebar
st.sidebar.markdown("### Quick Resources")
st.sidebar.markdown("[FishSmart NSW App](https://www.dpi.nsw.gov.au/fishing/recreational/resources/fishsmart-app)")
st.sidebar.markdown("[DPI Closures](https://www.dpi.nsw.gov.au/fishing/closures)")
st.sidebar.markdown("[Tides & Solunar](https://tides4fishing.com/au)")
st.sidebar.markdown("[Buy Gear @ BCF (affiliate)](https://www.bcf.com.au/)")  # Add real affiliate if ready

if st.button("Refresh"):
    st.rerun()
