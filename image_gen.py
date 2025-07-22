import streamlit as st
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
    .preview-card {{
        background: #f8f9fa;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        padding: 1.5em;
        margin: 1em 0;
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize session state with defaults
def initialize_session_state():
    defaults = {
        'vertical': 'E-commerce',
        'product': ['Joggers'],
        'theme': ['Urban'],
        'style': ['Bold'],
        'promo_text': 'Summer Sale - 25% Off!',
        'channel': 'WhatsApp (Square)',
        'color_palette': ['Black', 'White'],
        'audience': ['Young Adults'],
        'prompt_preview': '',
        'show_preview': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Logo & title
if os.path.exists("gms_logo.png"):
    st.image("gms_logo.png", width=150)
else:
    st.markdown(f'<h1 style="color: {GMS_GREEN}; text-align: center;">GMS</h1>', unsafe_allow_html=True)

st.markdown('<div class="gms-title">Content Builder MVP</div>', unsafe_allow_html=True)

# Configuration data
verticals = ["E-commerce", "Healthcare", "Retail", "Logistics", "Banking", "Other"]
products = {
    "Healthcare": ["Health checkup", "Dental care", "Vaccination drive", "Telemedicine", "Health insurance", "Wellness package"],
    "E-commerce": ["Joggers", "Shoes", "Smartphones", "Home appliances", "Flash sale", "Mega deals", "New arrivals", "Clearance"],
    "Retail": ["Groceries", "Apparel", "Furniture", "Grand opening", "Weekend sale", "Back to school", "Holiday special"],
    "Logistics": ["Courier service", "Delivery updates", "Package tracking", "Express shipping", "Same day delivery"],
    "Banking": ["Credit cards", "Loan offers", "Insurance", "Account opening", "Investment plans", "Digital banking"],
    "Other": ["Event invites", "Webinar", "Survey", "Service reminder", "App launch", "Brand awareness"]
}
themes = ["Urban", "Gym", "Outdoor", "Nature", "Office", "Studio", "Clinic", "Home", "Street", "Modern interior"]
styles = ["Bold", "Minimalist", "Energetic", "Luxury", "Playful", "Trustworthy", "Modern", "Vintage", "Professional"]
channels = {
    "WhatsApp (Square)": "1024x1024",
    "Instagram Post (Square)": "1024x1024", 
    "OTT Banner (Wide)": "1792x1024",
    "Instagram Story (Tall)": "1024x1792"
}
colors = ["Black", "White", "Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Pink", "Navy", "Grey", "Gold", "Silver"]
audiences = ["General", "Young Adults", "Teenagers", "Families", "Parents", "Seniors", "Professionals", "Students", "Urban millennials"]

# Helper function to build prompt
def build_prompt(vertical, product, theme, style, promo_text, channel, color_palette, audience):
    product_str = ', '.join(product) if product else '[PRODUCT]'
    theme_str = ', '.join(theme) if theme else '[THEME]' 
    style_str = ', '.join(style) if style else '[STYLE]'
    color_str = ', '.join(color_palette) if color_palette else '[COLORS]'
    audience_str = ', '.join(audience) if audience else '[AUDIENCE]'
    promo_str = promo_text.strip() if promo_text else '[PROMO TEXT]'
    
    prompt = (
        f"Create a {style_str} promotional image for a {vertical.lower()} campaign featuring {product_str}. "
        f"The background should be {theme_str}. "
        f"Use a {color_str} color palette. "
        f"The target audience is {audience_str}. "
        f"Overlay large, readable text: '{promo_str}' "
        f"Format: {channels[channel]}. "
        f"Brand-safe, commercial use, high quality, professional photography style. "
        f"Do not include logos or trademarked symbols."
    )
    return prompt

# Main form
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Campaign Details")
    
    # Form inputs
    col1, col2 = st.columns([1, 1])
    
    with col1:
        vertical = st.selectbox(
            "Vertical", 
            verticals, 
            index=verticals.index(st.session_state.vertical),
            key="vertical_input"
        )
        
        product = st.multiselect(
            "Product / Campaign Type",
            products[vertical],
            default=st.session_state.product if vertical == st.session_state.vertical else products[vertical][:1],
            key="product_input"
        )
        
        theme = st.multiselect(
            "Theme / Background",
            themes,
            default=st.session_state.theme,
            key="theme_input"
        )
        
        style = st.multiselect(
            "Visual Style / Tone",
            styles,
            default=st.session_state.style,
            key="style_input"
        )
    
    with col2:
        promo_text = st.text_input(
            "Promo Text / Overlay", 
            value=st.session_state.promo_text,
            key="promo_input"
        )
        
        channel = st.selectbox(
            "Target Channel / Format", 
            list(channels.keys()),
            index=list(channels.keys()).index(st.session_state.channel),
            key="channel_input"
        )
        
        color_palette = st.multiselect(
            "Color Palette (up to 3)",
            colors,
            default=st.session_state.color_palette,
            max_selections=3,
            key="color_input"
        )
        
        audience = st.multiselect(
            "Target Audience / Persona",
            audiences,
            default=st.session_state.audience,
            key="audience_input"
        )
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Preview Prompt", type="secondary"):
            st.session_state.show_preview = True
            st.session_state.prompt_preview = build_prompt(
                vertical, product, theme, style, promo_text, 
                channel, color_palette, audience
            )
    
    with col2:
        generate_clicked = st.button("Generate Visual", type="primary")
    
    with col3:
        if st.button("Reset Form"):
            # Reset to defaults
            st.session_state.vertical = 'E-commerce'
            st.session_state.product = ['Joggers']
            st.session_state.theme = ['Urban']
            st.session_state.style = ['Bold']
            st.session_state.promo_text = 'Summer Sale - 25% Off!'
            st.session_state.channel = 'WhatsApp (Square)'
            st.session_state.color_palette = ['Black', 'White']
            st.session_state.audience = ['Young Adults']
            st.session_state.show_preview = False
            st.session_state.prompt_preview = ''
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Prompt Preview Section
if st.session_state.show_preview and st.session_state.prompt_preview:
    st.markdown('<div class="preview-card">', unsafe_allow_html=True)
    st.markdown("#### Prompt Preview")
    st.text_area(
        "Generated prompt (you can edit before generating):",
        value=st.session_state.prompt_preview,
        height=120,
        key="editable_prompt"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Handle Generate
if generate_clicked:
    # Use edited prompt if available, otherwise build fresh
    if st.session_state.show_preview and 'editable_prompt' in st.session_state:
        final_prompt = st.session_state.editable_prompt
    else:
        final_prompt = build_prompt(
            vertical, product, theme, style, promo_text,
            channel, color_palette, audience
        )
    
    if final_prompt.strip():
        with st.spinner("Generating your visual..."):
            try:
                # Get API key from secrets
                api_key = st.secrets["OPENAI_API_KEY"]
                openai.api_key = api_key
                
                size = channels[channel]
                
                # Make API call
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=final_prompt,
                    size=size,
                    quality="standard",
                    n=1,
                )
                
                image_url = response.data[0].url
                
                # Download and display image
                img_response = requests.get(image_url)
                img_bytes = img_response.content
                
                st.success("✅ Visual generated successfully!")
                st.image(img_bytes, caption=f"Generated for: {channel}", use_column_width=True)
                
                # Download button
                st.download_button(
                    label="📥 Download Image",
                    data=img_bytes,
                    file_name=f"campaign_visual_{channel.lower().replace(' ', '_').replace('(', '').replace(')', '')}.png",
                    mime="image/png",
                    type="primary"
                )
                
                # Show used prompt
                with st.expander("View used prompt"):
                    st.code(final_prompt, language="text")
                    
            except Exception as e:
                st.error(f"❌ Image generation failed: {str(e)}")
                if "API key" in str(e):
                    st.info("💡 Make sure your OpenAI API key is properly set in Streamlit secrets.")
    else:
        st.warning("⚠️ Please fill in the campaign details or preview the prompt first.")

# Footer
st.markdown("---")
st.markdown("*Powered by OpenAI DALL-E 3 | Built with Streamlit*", unsafe_allow_html=True)