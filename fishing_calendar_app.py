import streamlit as st
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

# ... (rest of your code unchanged until the display part)

# After getting loc_row
loc_row = locations_df[locations_df['location_name'] == selected_location].iloc[0]
zone = loc_row['zone']
month_name = calendar.month_name[selected_date.month]

# ... (species filtering unchanged)

st.subheader(f"📍 {selected_location} — {month_name} {selected_date.year}")
st.info(f"**Zone:** {zone} | **State:** {loc_row.get('state', 'Unknown')}")

# Rules / Warnings (unchanged)
st.markdown("### ⚠️ DPI & Reserve Rules")
st.markdown(f"**Closures:** {loc_row.get('closure_notes', 'Check current rules via official site')}")
st.markdown(f"**Marine/Aquatic Reserve:** {loc_row.get('reserve_notes', 'Standard unless noted')}")
st.markdown(f"[Official info]({loc_row.get('official_link', '#')})")

# NEW: Google Maps link
if 'latitude' in loc_row and 'longitude' in loc_row and pd.notna(loc_row['latitude']) and pd.notna(loc_row['longitude']):
    maps_url = f"https://www.google.com/maps?q={loc_row['latitude']},{loc_row['longitude']}"
    st.markdown(f"**View on Google Maps:** [Open {selected_location} in Maps]({maps_url})")
    st.caption("Click to see exact location, directions, street view, etc.")
else:
    st.caption("No GPS coordinates available for this spot yet.")

st.markdown("---")

# ... (rest of species/gear display unchanged)
