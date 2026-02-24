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

# ================== SAFE DATA LOADING ==================
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
    
    def safe_load(filename):
        full_path = os.path.join(base_path, filename)
        try:
            df = pd.read_csv(full_path)
            return df
        except FileNotFoundError:
            st.error(f"File not found: {filename}")
            st.info(f"Ensure {filename} is in the same folder as the app and pushed to GitHub.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading {filename}: {str(e)}")
            return pd.DataFrame()

    loc_df   = safe_load("locations.csv")
    fish_df  = safe_load("fishing_data.csv")
    gear_df  = safe_load("gear_data.csv")
    
    return loc_df, fish_df, gear_df

locations_df, fishing_df, gear_df = load_data()

# ================== APP ==================
st.set_page_config(page_title="Aussie Fishing Calendar", layout="wide")
st.title("🎣 Australian Fishing Calendar – Location & Legal Size Guide")

st.markdown("""
Search a specific spot, pick a date, and get:
- Local rules & reserve info
- Target species for the month (filtered by zone)
- Legal min/max sizes
- Recommended gear setups
""")

st.caption("**Important:** Legal sizes & closures are approximate (Feb 2026 rules). Always verify via official apps/sites: FishSmart (NSW), Qld Fisheries, VFA (VIC), PIRSA (SA), Tas Inland Fisheries, NT Fisheries. Rules can change.")

# ────────────────────────────────────────────────
# INPUTS
# ────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    if locations_df.empty:
        st.warning("No locations loaded. Add locations.csv file.")
        location_list = ["No locations available"]
    else:
        location_list = sorted(locations_df['location_name'].unique().tolist())
    
    selected_location = st.selectbox(
        "🔍 Search location (e.g. Preddy’s Wharf, Urangan Pier, Brighton Jetty)",
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
# DISPLAY LOCATION INFO
# ────────────────────────────────────────────────
if not locations_df.empty and selected_location in locations_df['location_name'].values:
    loc_row = locations_df[locations_df['location_name'] == selected_location].iloc[0]
    
    zone = loc_row.get('zone', 'Unknown')
    state = loc_row.get('state', 'Unknown')
    month_name = calendar.month_name[selected_date.month]
    
    st.subheader(f"📍 {selected_location}")
    st.caption(f"{month_name} {selected_date.year} • {zone} • {state}")
    
    # Google Maps
    if 'latitude' in loc_row and 'longitude' in loc_row and pd.notna(loc_row['latitude']) and pd.notna(loc_row['longitude']):
        maps_url = f"https://www.google.com/maps?q={loc_row['latitude']},{loc_row['longitude']}"
        st.markdown(f"🗺️ [Open in Google Maps]({maps_url})")
    
    # Rules
    st.markdown("### ⚠️ Local Rules & Reserves")
    st.markdown(f"**Closures / Restrictions:** {loc_row.get('closure_notes', 'Check current regulations')}")
    st.markdown(f"**Marine / Aquatic Reserve:** {loc_row.get('reserve_notes', 'Standard rules apply')}")
    
    if 'official_link' in loc_row and loc_row['official_link']:
        st.markdown(f"[Official info →]({loc_row['official_link']})")
    
    st.markdown("---")
    
    # ────────────────────────────────────────────────
    # SPECIES & LEGAL SIZES + GEAR
    # ────────────────────────────────────────────────
    filtered_species = fishing_df[
        (fishing_df['month'] == month_name) &
        (fishing_df['zone'].str.contains(zone.split(' (')[0], na=False))
    ]
    
    if filtered_species.empty:
        st.info(f"No species data for {month_name} in {zone} yet. Expand fishing_data.csv.")
    else:
        st.subheader("🐟 Target Species – Legal Sizes & Gear")
        st.caption("Legal sizes are minimum (min) and maximum (max) total length in cm. Closed = no take allowed.")
        
        for _, row in filtered_species.iterrows():
            species = row['species']
            rating = row.get('rating', '—')
            
            # Gear match
            gear_match = gear_df[gear_df['species'].str.lower() == species.lower()]
            gear = gear_match.iloc[0] if not gear_match.empty else None
            
            with st.expander(f"{species} ({rating})"):
                if rating == "Closed":
                    st.warning("Closed season – no take allowed this month.")
                else:
                    min_cm = row.get('legal_min_cm', 'N/A')
                    max_cm = row.get('legal_max_cm', None)
                    size_text = f"Legal min: **{min_cm} cm**"
                    if max_cm and max_cm != '':
                        size_text += f" | Max: **{max_cm} cm**"
                    st.markdown(size_text)
                
                st.markdown(f"**Best times (general):** {row.get('best_times_notes', 'Dawn & dusk + tide changes')}")
                
                if gear is not None:
                    st.markdown("**Recommended Setup**")
                    st.markdown(f"- Rod: **{gear['rod']}**")
                    st.markdown(f"- Reel: **{gear['reel']}**")
                    st.markdown(f"- Line/Leader: **{gear['line_leader_weight']}**")
                    st.markdown(f"- Rig: **{gear['rig']}**")
                    st.markdown(f"- Bait/Lure: **{gear['bait_or_lure']}**")
                else:
                    st.caption("Gear details not yet added – update gear_data.csv.")
                
                st.markdown("---")

else:
    st.warning("Selected location not found. Try another or update locations.csv.")

# ────────────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────────────
st.sidebar.title("Resources")
st.sidebar.markdown("- [NSW FishSmart App](https://www.dpi.nsw.gov.au/fishing/recreational/resources/fishsmart-app)")
st.sidebar.markdown("- [NSW Rules & Closures](https://www.dpi.nsw.gov.au/fishing/closures)")
st.sidebar.markdown("- [QLD Fisheries](https://www.daf.qld.gov.au/business-priorities/fisheries)")
st.sidebar.markdown("- [VIC VFA Guide](https://vfa.vic.gov.au)")
st.sidebar.markdown("- [SA PIRSA](https://pir.sa.gov.au)")
st.sidebar.markdown("- [TAS Fishing](https://fishing.tas.gov.au)")
st.sidebar.markdown("- [NT Fishing](https://nt.gov.au/leisure/fishing)")
st.sidebar.markdown("- [Tides4Fishing AU](https://tides4fishing.com/au)")
st.sidebar.markdown("---")
st.sidebar.caption("Data is indicative • Verify with official sources")

if st.sidebar.button("Clear cache & refresh"):
    st.cache_data.clear()
    st.rerun()
