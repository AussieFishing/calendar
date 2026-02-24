import streamlit as st
from datetime import datetime
import calendar  # for month names

# ================== DATA (expand as needed) ==================
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

# Example monthly data (add more months/species from earlier response or sources)
# In real version, load from CSV/JSON for easy updates
monthly_targets = {
    "January": {
        "times": "Dawn & dusk + 2 hrs around high/low tide. Major solunar periods best.",
        "species": [
            ("Barramundi", "Great in NT/QLD North", "Medium-heavy spin rod 6-15kg, hardbodies or live bait, 40-80lb leader."),
            ("Snapper", "Good nationwide", "Medium 4-8kg rod, paternoster rig with pilchards/squid, 4/0-8/0 circle hooks."),
            ("Flathead", "Good", "Light spin 1-4kg, soft plastics on 1/4oz jighead or running sinker."),
            ("Kingfish", "Great in NSW", "Heavy 8-15kg, live bait or poppers.")
        ]
    },
    "February": {
        "times": "Same as above — focus on major solunar + incoming tides for estuaries.",
        "species": [
            ("Striped Marlin", "Great NSW offshore", "Heavy trolling 15-24kg, skirted lures."),
            ("Snapper", "Good", "Paternoster rig."),
            ("Flathead", "Good", "Soft plastics."),
            ("Kingfish", "Excellent", "Live bait rigs.")
        ]
    },
    # Add March–December similarly...
    # For full year, consider loading from a CSV file with pd.read_csv()
}

# Fallback
default_month = datetime.now().strftime("%B")
if default_month not in monthly_targets:
    default_month = "January"

# ================== APP ==================
st.set_page_config(page_title="Aussie Fishing Calendar", layout="wide")
st.title("🎣 Australian Fishing Calendar")
st.markdown("Enter your location and month for best bite times, target species, and gear suggestions. Always check state rules (e.g., NSW DPI, QLD Fisheries).")

col1, col2 = st.columns(2)

with col1:
    location = st.selectbox("General Location", options=list(zones.keys()), index=0)  # Sydney default

with col2:
    month_options = list(calendar.month_name)[1:]  # Jan–Dec
    selected_month = st.selectbox("Month", options=month_options, index=month_options.index(default_month))

# Optional: Add date picker for precise day (future enhancement)
# selected_date = st.date_input("Pick a specific date (optional)", value=datetime.now())

zone = zones.get(location, "National (default)")

data = monthly_targets.get(selected_month, monthly_targets["January"])

st.subheader(f"📅 {selected_month} 2026 – {location} ({zone})")

st.info(f"⏰ Best Times: {data['times']}")
st.markdown("• Dawn/dusk strongest • Check daily tides/solunar: tides4fishing.com/au or fishingreminder.com")
st.markdown("• Major periods: moon overhead/underfoot • Minor: moonrise/set")

st.subheader("🐟 Top Target Species & Recommended Gear/Rigs")
for species, rating, gear in data["species"]:
    st.markdown(f"**{species}** ({rating})")
    st.markdown(f"Gear/Rig: {gear}")
    st.markdown("---")

# Monetization placeholders (add later)
st.sidebar.markdown("### Support the App")
st.sidebar.markdown("[Affiliate: Buy gear at BCF](https://www.bcf.com.au/?aff=yourid)")  # Replace with real link
st.sidebar.markdown("Want premium features? (hyper-local, alerts, PDFs) → Coming soon!")

if st.button("Refresh / Update"):
    st.rerun()
