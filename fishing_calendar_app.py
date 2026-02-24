import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import os

# ================== SAFE DATA LOADING ==================
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()

    def safe_load(filename, required_columns=None):
        full_path = os.path.join(base_path, filename)
        try:
            df = pd.read_csv(full_path)
            if required_columns:
                missing = [col for col in required_columns if col not in df.columns]
                if missing:
                    st.error(f"Missing columns in {filename}: {', '.join(missing)}")
                    return pd.DataFrame()
            return df
        except FileNotFoundError:
            st.error(f"File not found: {filename}")
            st.info(f"Make sure {filename} exists in the repository root and is committed/pushed.")
            return pd.DataFrame()
        except pd.errors.ParserError as e:
            st.error(f"CSV parsing error in {filename}: {str(e)}")
            st.info("Common causes: mismatched column count, unquoted commas inside fields, trailing commas, missing header.")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading {filename}: {str(e)}")
            return pd.DataFrame()

    loc_df   = safe_load("locations.csv",   required_columns=["location_name", "zone"])
    fish_df  = safe_load("fishing_data.csv", required_columns=["month", "zone", "species"])
    gear_df  = safe_load("gear_data.csv",    required_columns=["species"])

    return loc_df, fish_df, gear_df

locations_df, fishing_df, gear_df = load_data()

# ================== MAIN APP ==================
st.set_page_config(page_title="Aussie Fishing Calendar", layout="wide")
st.title("🎣 Australian Fishing Calendar")

st.markdown("""
Select a location and date to see:
- Local rules & marine reserve information
- Target species for the selected month + zone
- Legal minimum & maximum sizes (where available)
- Recommended gear setups
""")

st.caption("**Always verify** current bag/size/closure rules via official sources: FishSmart (NSW), Qld Fisheries, VFA (VIC), PIRSA (SA), Tas Inland Fisheries, NT Fisheries. Data is indicative as of 2026.")

# ────────────────────────────────────────────────
# INPUTS
# ────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    if locations_df.empty:
        st.warning("No locations loaded. Please add / fix locations.csv")
        location_list = ["No locations available"]
    else:
        location_list = sorted(locations_df['location_name'].unique().tolist())

    selected_location = st.selectbox(
        "🔍 Search & select location",
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
# DISPLAY SELECTED LOCATION
# ────────────────────────────────────────────────
if not locations_df.empty and selected_location in locations_df['location_name'].values:
    loc_row = locations_df[locations_df['location_name'] == selected_location].iloc[0]

    zone       = loc_row.get('zone', 'Unknown')
    state      = loc_row.get('state', 'Unknown')
    month_name = calendar.month_name[selected_date.month]

    st.subheader(f"📍 {selected_location}")
    st.caption(f"{month_name} {selected_date.year}  •  Zone: **{zone}**  •  {state}")

    # Google Maps link
    if 'latitude' in loc_row and 'longitude' in loc_row and pd.notna(loc_row['latitude']) and pd.notna(loc_row['longitude']):
        maps_url = f"https://www.google.com/maps?q={loc_row['latitude']},{loc_row['longitude']}"
        st.markdown(f"🗺️ [View on Google Maps]({maps_url})")

    # Rules & Reserves
    st.markdown("### ⚠️ Rules & Reserves")
    st.markdown(f"**Closures / Restrictions:** {loc_row.get('closure_notes', 'Check current regulations')}")
    st.markdown(f"**Marine / Aquatic Reserve:** {loc_row.get('reserve_notes', 'Standard rules apply')}")

    if 'official_link' in loc_row and pd.notna(loc_row['official_link']) and loc_row['official_link']:
        st.markdown(f"[Official rules →]({loc_row['official_link']})")

    st.markdown("---")

    # ────────────────────────────────────────────────
    # SPECIES + LEGAL SIZES + GEAR
    # ────────────────────────────────────────────────
    filtered = fishing_df[
        (fishing_df['month'] == month_name) &
        (fishing_df['zone'].str.contains(zone.split(' (')[0], case=False, na=False))
    ]

    if filtered.empty:
        st.info(f"No species data recorded for **{month_name}** in **{zone}** yet.")
        st.caption("Add rows to fishing_data.csv for this month/zone combination.")
    else:
        st.subheader("🐟 Target Species – Legal Sizes & Gear")
        st.caption("Sizes are minimum (min) and maximum (max) total length in cm. Closed = no take allowed.")

        for _, row in filtered.iterrows():
            species = row['species']
            rating  = row.get('rating', '—')

            gear_match = gear_df[gear_df['species'].str.lower() == species.lower()]
            gear = gear_match.iloc[0] if not gear_match.empty else None

            with st.expander(f"{species}  ({rating})"):
                if rating.lower() in ['closed', 'no take', 'closed season']:
                    st.warning("Closed season – no take permitted this month.")
                else:
                    min_cm = row.get('legal_min_cm', 'N/A')
                    max_cm = row.get('legal_max_cm', None)
                    size_str = f"**Legal min:** {min_cm} cm"
                    if pd.notna(max_cm) and max_cm != '':
                        size_str += f"  |  **Max:** {max_cm} cm"
                    st.markdown(size_str)

                st.markdown(f"**Best times:** {row.get('best_times_notes', 'Dawn & dusk + tide changes')}")

                if gear is not None:
                    st.markdown("**Recommended gear**")
                    st.markdown(f"- Rod: **{gear.get('rod', '—')}**")
                    st.markdown(f"- Reel: **{gear.get('reel', '—')}**")
                    st.markdown(f"- Line/Leader: **{gear.get('line_leader_weight', '—')}**")
                    st.markdown(f"- Rig: **{gear.get('rig', '—')}**")
                    st.markdown(f"- Bait/Lure: **{gear.get('bait_or_lure', '—')}**")
                else:
                    st.caption("No gear recommendation yet – update gear_data.csv")

                st.markdown("---")

else:
    if locations_df.empty:
        st.error("locations.csv could not be loaded. Check file exists and has correct columns.")
    else:
        st.warning("Selected location not found in database. Try another.")

# ────────────────────────────────────────────────
# SIDEBAR RESOURCES
# ────────────────────────────────────────────────
st.sidebar.title("Quick Links")
st.sidebar.markdown("[NSW FishSmart App](https://www.dpi.nsw.gov.au/fishing/recreational/resources/fishsmart-app)")
st.sidebar.markdown("[NSW Rules & Closures](https://www.dpi.nsw.gov.au/fishing/closures)")
st.sidebar.markdown("[QLD Fisheries](https://www.daf.qld.gov.au/business-priorities/fisheries)")
st.sidebar.markdown("[VIC VFA](https://vfa.vic.gov.au)")
st.sidebar.markdown("[SA PIRSA](https://pir.sa.gov.au)")
st.sidebar.markdown("[TAS Fishing](https://fishing.tas.gov.au)")
st.sidebar.markdown("[NT Fishing](https://nt.gov.au/leisure/fishing)")
st.sidebar.markdown("[Tides & Solunar – tides4fishing.com/au](https://tides4fishing.com/au)")
st.sidebar.markdown("---")
st.sidebar.caption("Data approximate • Always check official sources")

if st.sidebar.button("Refresh / Clear Cache"):
    st.cache_data.clear()
    st.rerun()
