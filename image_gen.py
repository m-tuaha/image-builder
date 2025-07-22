import streamlit as st
import openai
from PIL import Image
import os

# ---- THEME COLORS (HEX) ----
MINT = "#DFF6EF"
BLUE = "#C7E7FB"
LAVENDER = "#D7DBFB"
GREY = "#EAEAEA"
GMS_GREEN = "#18BC62"

# ---- SET PAGE CONFIG ----
st.set_page_config(page_title="Content Builder MVP", page_icon=None, layout="centered")

# ---- CUSTOM CSS ----
st.markdown(f"""
    <style>
    body {{
        background: linear-gradient(90deg, {MINT} 0%, {BLUE} 33%, {LAVENDER} 66%, {GREY} 100%) !important;
    }}
    .main {{
        background: transparent !important;
    }}
    .stButton>button {{
        background-color: {LAVENDER} !important;
        color: #222 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5em 2em !important;
        font-weight: bold !important;
        font-size: 1.07rem !important;
        margin-top: 1em !important;
    }}
    .st-b2, .st-bq, .st-c7 {{
        background: white !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 28px #bcc3d480 !important;
        padding: 2.3em 2em 2em 2em !important;
        margin-top: 2em !important;
    }}
    .gms-title {{
        color: {GMS_GREEN};
        font-size: 2.4rem;
        font-weight: 800;
        text-align: center;
        margin-top: 0.5em;
        margin-bottom: 0.3em;
        letter-spacing: -1px;
    }}
    .gms-logo {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 110px;
        margin-bottom: 0.3em;
    }}
    </style>
""", unsafe_allow_html=True)

# ---- GMS LOGO ----
st.image("gms_logo.png", width=160)
st.markdown('<div class="gms-title">AI Image Generator MVP</div>', unsafe_allow_html=True)

with st.container():
    st.markdown("#### Campaign Details")
    # ---- Vertical and Product Dropdowns ----
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

    with st.form("campaign_form"):
        col1, col2 = st.columns(2)
        with col1:
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
        with col2:
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
                # Set up your API key
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
