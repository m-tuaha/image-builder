import streamlit as st
from streamlit_tags import st_tags
import openai
import requests
import os

# Theme and layout
MINT = "#DFF6EF"
GMS_GREEN = "#18BC62"

st.set_page_config(page_title="Content Builder MVP", layout="centered")
st.markdown(f"""
    <style>
    body {{
        background: {MINT} !important;
    }}
    .stButton>button {{
        background-color: #D7DBFB !important;
        color: #222 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.09em !important;
        width: 100% !important;
        margin-top: 1em !important;
    }}
    .block-container {{
        padding-top: 2.2rem;
        padding-bottom: 2.2rem;
    }}
    .gms-title {{
        color: {GMS_GREEN};
        font-size: 2.1rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5em;
    }}
    .card {{
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 3px 18px #bcc3d485;
        max-width: 520px;
        margin-left: auto;
        margin-right: auto;
        padding: 2.3em 2em 2em 2em;
    }}
    </style>
""", unsafe_allow_html=True)

# Logo & title
st.image("gms_logo.png", width=150)
st.markdown('<div class="gms-title">Content Builder MVP</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Campaign Details")

    # Default tag options
    verticals = ["Healthcare", "E-commerce", "Retail", "Logistics", "Banking", "Other"]
    products = {
        "Healthcare": ["Health checkup", "Dental care", "Vaccination drive", "Telemedicine"],
        "E-commerce": ["Joggers", "Shoes", "Smartphones", "Home appliances", "Flash sale", "Mega deals"],
        "Retail": ["Groceries", "Apparel", "Furniture", "Grand opening", "Weekend sale"],
        "Logistics": ["Courier service", "Delivery updates", "Package tracking", "Express shipping"],
        "Banking": ["Credit cards", "Loan offers", "Insurance", "Account opening"],
        "Other": ["Event invites", "Webinar", "Survey", "Service reminder"]
    }
    themes = ["Urban", "Gym", "Outdoor", "Nature", "Office", "Studio", "Clinic"]
    styles = ["Bold", "Minimalist", "Energetic", "Luxury", "Playful", "Trustworthy", "Modern"]
    channels = {
        "WhatsApp (Square)": "1024x1024",
        "Instagram Post (Square)": "1024x1024",
        "OTT Banner (Wide)": "1792x1024",
        "Instagram Story (Tall)": "1024x1792"
    }
    colors = ["Black", "White", "Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Pink", "Navy", "Grey"]
    audiences = ["General", "Young Adults", "Teenagers", "Families", "Parents", "Seniors", "Asian", "African", "European", "Middle Eastern"]

    # --- Session state for reset ---
    if "clear" not in st.session_state:
        st.session_state.clear = False

    # ---- Form State ----
    def reset_form():
        st.session_state.vertical = ""
        st.session_state.product = []
        st.session_state.theme = []
        st.session_state.style = []
        st.session_state.promo_text = ""
        st.session_state.channel = ""
        st.session_state.color_palette = []
        st.session_state.audience = []
        st.session_state.prompt_preview = ""
        st.session_state.clear = True

    with st.form("campaign_form"):
        col1, = st.columns(1)

        with col1:
            vertical = st.selectbox("Vertical", verticals, key="vertical")
            product_tag = st_tags(
                label='Product / Campaign Type',
                text='Type or select (comma to add new)',
                value=[],
                suggestions=products[vertical],
                key="product"
            )
            theme_tag = st_tags(
                label='Theme / Background',
                text='Type or select (comma to add new)',
                value=[],
                suggestions=themes,
                key="theme"
            )
            style_tag = st_tags(
                label='Visual Style / Tone',
                text='Type or select (comma to add new)',
                value=[],
                suggestions=styles,
                key="style"
            )
            promo_text = st.text_input("Promo Text / Overlay", value=st.session_state.get("promo_text", ""), key="promo_text")
            channel = st.selectbox("Target Channel / Format", list(channels.keys()), key="channel")
            color_palette_tag = st_tags(
                label='Color Palette (up to 3)',
                text='Type or select (comma to add new)',
                value=[],
                suggestions=colors,
                key="color_palette"
            )
            audience_tag = st_tags(
                label='Target Audience / Persona',
                text='Type or select (comma to add new)',
                value=[],
                suggestions=audiences,
                key="audience"
            )

        # ---- Prompt Preview (updates live) ----
        def build_prompt():
            prompt = (
                f"Create a {', '.join(style_tag) if style_tag else '[STYLE]'} promotional image for a {vertical.lower()} campaign featuring {', '.join(product_tag) if product_tag else '[PRODUCT]'}."
                f" The background should be {', '.join(theme_tag) if theme_tag else '[THEME]'}."
                f" Use a {', '.join(color_palette_tag) if color_palette_tag else '[COLORS]'} color palette."
                f" The target audience is {', '.join(audience_tag) if audience_tag else '[AUDIENCE]'}."
                f" Overlay large text: '{promo_text.strip() if promo_text else '[PROMO TEXT]'}'"
                f" Format: {channels[channel]}."
                f" Brand-safe, commercial use. Do not include logos or trademarked symbols."
            )
            return prompt

        prompt_preview = build_prompt()
        prompt_text = st.text_area("Prompt Preview (edit if needed before generating):", value=prompt_preview, height=130, key="prompt_preview")

        cols = st.columns([1,1])
        with cols[0]:
            generate = st.form_submit_button("Generate Visual")
        with cols[1]:
            reset = st.form_submit_button("Reset", on_click=reset_form)

    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Handle Generate ----
    if generate and prompt_text.strip():
        with st.spinner("Generating your visual..."):
            try:
                api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
                openai.api_key = api_key
                size = channels[channel]
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=prompt_text,
                    size=size,
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url

                # Download and display
                img_bytes = requests.get(image_url).content
                st.image(img_bytes, caption="AI-generated campaign visual", use_column_width=True)
                st.download_button("Download Image", data=img_bytes, file_name="campaign_visual.png", mime="image/png")
                st.success("Visual generated! You can download the image above.")
            except Exception as e:
                st.error(f"Image generation failed: {e}")
    elif reset:
        reset_form()
