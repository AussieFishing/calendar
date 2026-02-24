import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import os

# ================== ZONES MAPPING ==================
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

# ================== LOAD DATA SAFELY ==================
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
    
    def safe_load(filename):
        full_path = os.path.join(base_path, filename)
        try:
            return pd.read_csv(full_path)
        except FileNotFoundError:
            st.error(f"File not found: {filename}")
            st.info(f"Make sure {filename} is in the same folder as the app script and committed to GitHub.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error reading {filename}: {str(e)}")
            return pd.DataFrame()

    loc_df   = safe_load("locations.csv")
    fish_df  = safe_load("fishing_data.csv")
    gear_df  = safe_load("gear_data.csv")
    
    return loc_df, fish_df, gear_df

locations_df, fishing_df, gear_df = load_data()

# ================== MAIN APP ==================
st.set_page_config(page_title="Aussie Fishing Calendar", layout="wide")
st.title("🎣 Australian Fishing Calendar")

st.markdown("""
Select a specific fishing location and date to see:
- Local rules & marine reserve info
- Target species for the month
- Recommended gear setups
""")

st.caption("Always verify current regulations via FishSmart (NSW) or Department of Agriculture and Fisheries (QLD) apps/websites. Rules change frequently.")

# ────────────────────────────────────────────────
# INPUTS
# ────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    if locations_df.empty:
        st.warning("No locations loaded. Please add locations.csv file.")
        location_list = ["No locations available"]
    else:
        location_list = sorted(locations_df['location_name'].unique().tolist())
    
    selected_location = st.selectbox(
        "🔍 Search & select location (e.g. Preddy’s Wharf, Urangan Pier, St Georges Basin)",
        options=location_list,
        index=0 if location_list else 0
    )

with col2:
    selected_date = st.date_input(
        "Select date",
        value=datetime.today(),
        min_value=datetime(2025, 1, 1),
        max_value=datetime(2027, 12, 31)
    )

# ────────────────────────────────────────────────
# DISPLAY SELECTED LOCATION INFO
# ────────────────────────────────────────────────
if not locations_df.empty and selected_location in locations_df['location_name'].values:
    loc_row = locations_df[locations_df['location_name'] == selected_location].iloc[0]
    
    zone = loc_row.get('zone', 'Unknown')
    state = loc_row.get('state', 'Unknown')
    month_name = calendar.month_name[selected_date.month]
    
    st.subheader(f"📍 {selected_location}")
    st.caption(f"{month_name} {selected_date.year} • {zone} • {state}")
    
    # Google Maps link
    if 'latitude' in loc_row and 'longitude' in loc_row and pd.notna(loc_row['latitude']) and pd.notna(loc_row['longitude']):
        maps_url = f"https://www.google.com/maps?q={loc_row['latitude']},{loc_row['longitude']}"
        st.markdown(f"🗺️ [Open in Google Maps]({maps_url})")
    
    # Rules & Reserves
    st.markdown("### ⚠️ Local Rules & Reserves")
    st.markdown(f"**Closures / Restrictions:** {loc_row.get('closure_notes', 'Check current regulations')}")
    st.markdown(f"**Marine / Aquatic Reserve:** {loc_row.get('reserve_notes', 'Standard rules apply')}")
    
    if 'official_link' in loc_row and loc_row['official_link']:
        st.markdown(f"[Official information →]({loc_row['official_link']})")
    
    st.markdown("---")
    
    # ────────────────────────────────────────────────
    # SPECIES & GEAR
    # ────────────────────────────────────────────────
    filtered_species = fishing_df[
        (fishing_df['month'] == month_name) &
        (fishing_df['zone'].str.contains(zone.split(' (')[0], na=False))
    ]
    
    if filtered_species.empty:
        st.info(f"No species data recorded for {month_name} in {zone} yet.")
    else:
        st.subheader("🐟 Target Species & Recommended Gear")
        st.caption("General recommendations for the zone/month. Adjust for conditions & check size/bag limits.")
        
        for _, row in filtered_species.iterrows():
            species = row['species']
            
            # Find matching gear
            gear_match = gear_df[gear_df['species'].str.lower() == species.lower()]
            gear = gear_match.iloc[0] if not gear_match.empty else None
            
            with st.expander(f"{species}  ({row.get('rating', '—')})"):
                st.markdown(f"**Best times (general):** {row.get('best_times_notes', 'Dawn & dusk + tide changes')}")
                
                if gear is not None:
                    st.markdown("**Recommended Setup**")
                    st.markdown(f"- Rod: **{gear['rod']}**")
                    st.markdown(f"- Reel: **{gear['reel']}**")
                    st.markdown(f"- Line/Leader: **{gear['line_leader_weight']}**")
                    st.markdown(f"- Rig: **{gear['rig']}**")
                    st.markdown(f"- Bait/Lure: **{gear['bait_or_lure']}**")
                else:
                    st.caption("Gear recommendations not yet available for this species.")
                
                st.markdown("---")

else:
    st.warning("Selected location not found in database. Try another or update locations.csv")

# ────────────────────────────────────────────────
# SIDEBAR RESOURCES
# ────────────────────────────────────────────────
st.sidebar.title("Quick Resources")
st.sidebar.markdown("- [NSW FishSmart App](https://www.dpi.nsw.gov.au/fishing/recreational/resources/fishsmart-app)")
st.sidebar.markdown("- [NSW Fishing Rules & Closures](https://www.dpi.nsw.gov.au/fishing/closures)")
st.sidebar.markdown("- [QLD Fisheries](https://www.daf.qld.gov.au/business-priorities/fisheries)")
st.sidebar.markdown("- [Tides & Solunar – tides4fishing.com/au](https://tides4fishing.com/au)")
st.sidebar.markdown("- [Fishing Reminder](https://fishingreminder.com/au)")
st.sidebar.markdown("---")
st.sidebar.caption("Data approximate • Always verify current regulations")

if st.sidebar.button("Refresh all data"):
    st.cache_data.clear()
    st.rerun()
