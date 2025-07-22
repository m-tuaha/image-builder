import streamlit as st
import openai
import os

# ---- THEME COLORS (HEX) ----
LAVENDER = "#D7DBFB"
GMS_GREEN = "#18BC62"

# ---- Custom CSS for consistent field width ----
st.markdown("""
    <style>
    .stTextInput, .stSelectbox, .stMultiSelect {
        min-width: 340px !important;
        max-width: 380px !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #D7DBFB !important;
        color: #222 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.09em !important;
        margin-top: 1em !important;
    }
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
        background: linear-gradient(90deg, #DFF6EF 0%, #C7E7FB 33%, #D7DBFB 66%, #EAEAEA 100%) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---- GMS LOGO AND HEADER ----
st.image("gms_logo.png", width=160)
st.markdown(f'<div style="color:{GMS_GREEN}; font-size:2.1rem; font-weight:800; text-align:center; margin-bottom:0.6em;">Content Builder MVP</div>', unsafe_allow_html=True)
st.markdown("### Campaign Details")

# ---- OPTIONS ----
vertical_options = {
    "Healthcare": [
        "Health checkup", "Dental care", "Vaccination drive", "Telemedicine", "Health tips", "Medical equipment"
    ],
    "E-commerce": [
        "Joggers", "Shoes", "Smartphones", "Home appliances", "Flash sale", "Mega deals", "New arrivals", "Gift cards"
    ],
    "Retail": [
        "Groceries", "Apparel", "Furniture", "Grand opening", "Loyalty program", "Weekend sale"
    ],
    "Logistics": [
        "Courier service", "Delivery updates", "Package tracking", "Express shipping", "Onboarding"
    ],
    "Banking": [
        "Credit cards", "Loan offers", "Insurance", "Account opening", "Digital wallet", "Personal finance tips"
    ],
    "Other": [
        "Event invites", "Webinar", "Survey", "Service reminder"
    ]
}

themes = [
    "Urban", "Gym", "Outdoor", "Nature", "Office", "Home", "Studio", "Park", "Beach", "Clinic", "Supermarket"
]

styles = [
    "Bold", "Minimalist", "Energetic", "Luxury", "Playful", "Trustworthy", "Modern", "Professional"
]

channels = {
    "WhatsApp (Square)": "1024x1024",
    "Instagram Post (Square)": "1024x1024",
    "OTT Banner (Wide)": "1792x1024",
    "Instagram Story (Tall)": "1024x1792"
}

colors = [
    "Black", "White", "Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Pink", "Navy", "Teal", "Grey"
]

audiences = [
    "General", "Young Adults", "Teenagers", "Families", "Parents", "Seniors", "Asian", "African", "European", "Middle Eastern", "Custom..."
]

# ---- FORM ----
with st.form("campaign_form", clear_on_submit=False):
    vertical = st.selectbox("Vertical", list(vertical_options.keys()))
    product = st.selectbox("Product / Campaign Type", vertical_options[vertical] + ["Custom..."])
    if product == "Custom...":
        product = st.text_input("Custom Product/Campaign Type")
    theme = st.selectbox("Theme / Background", themes + ["Custom..."])
    if theme == "Custom...":
        theme = st.text_input("Custom Theme/Background")
    style = st.selectbox("Visual Style / Tone", styles + ["Custom..."])
    if style == "Custom...":
        style = st.text_input("Custom Visual Style/Tone")
    promo_text = st.text_input("Promo Text / Overlay", placeholder="e.g., June Sale – 25% Off")
    channel = st.selectbox("Target Channel / Format", list(channels.keys()))
    size = channels[channel]
    color_palette = st.multiselect("Color Palette (up to 3)", colors)
    custom_colors = ""
    if "Custom..." in color_palette:
        custom_colors = st.text_input("Custom Colors (comma-separated)")
        color_palette = [c for c in color_palette if c != "Custom..."]
    audience = st.selectbox("Target Audience / Persona", audiences)
    if audience == "Custom...":
        audience = st.text_input("Custom Audience/Persona")

    st.markdown("&nbsp;", unsafe_allow_html=True)
    generate = st.form_submit_button("Generate Visual")

# ---- Build Prompt and Generate Image ----
def build_prompt():
    colors_used = ", ".join(color_palette)
    if custom_colors:
        colors_used = (colors_used + ", " + custom_colors).strip(", ")
    prompt = (
        f"Create a {style.lower()} promotional image for a {vertical.lower()} campaign featuring {product.lower()}."
        f" The background should be {theme.lower()}."
        f" Use a {colors_used.lower()} color palette."
        f" The target audience is {audience.lower()}."
        f" Overlay large text: '{promo_text.strip()}'"
        f" Format: {size}."
        f" Brand-safe, commercial use. Do not include logos or trademarked symbols."
    )
    return prompt

if generate:
    with st.spinner("Generating your visual..."):
        prompt = build_prompt()
        st.markdown("**Generated Prompt:**")
        st.code(prompt)
        try:
            api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
            openai.api_key = api_key

            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            st.image(image_url, caption="AI-generated campaign visual", use_column_width=True)
            st.success("Visual generated! Right-click the image to save it.")
        except Exception as e:
            st.error(f"Image generation failed: {e}")
