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
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }}
    .stButton>button {{
        background-color: #D7DBFB !important;
        color: #222 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.09em !important;
        width: 100% !important;
        margin-top: 0.5em !important;
    }}
    .gms-title {{
        color: {GMS_GREEN};
        font-size: 2.1rem;
        font-weight: 800;
        text-align: center;
        margin: 1rem 0 2rem 0;
    }}
    .form-card {{
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 3px 18px rgba(188, 195, 212, 0.3);
        padding: 2rem;
        margin-bottom: 2rem;
    }}
    .preview-card {{
        background: #f8f9fa;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }}
    .section-header {{
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: #2c3e50;
    }}
    /* Remove default streamlit spacing */
    .element-container {{
        margin-bottom: 1rem !important;
    }}
    /* Logo container */
    .logo-container {{
        text-align: center;
        margin-bottom: 1rem;
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize session state with defaults
def initialize_session_state():
    defaults = {
        'vertical': 'E-commerce',
        'product': 'Running shoes',
        'theme': 'Urban',
        'style': 'Modern',
        'promo_text': 'Summer Sale - 25% Off!',
        'color_palette': ['White', 'Green'],
        'audience': 'Young Adults',
        'background': 'Opaque',
        'prompt_preview': '',
        'show_preview': False,
        'include_text': True
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Configuration data
verticals = ["E-commerce", "Healthcare", "Retail", "Logistics", "Banking", "Other"]
products = {
    "Healthcare": ["Health checkup", "Dental consultation", "Vaccination campaign", "Telemedicine service", "Health insurance", "Wellness program", "Medical equipment", "Pharmacy products"],
    "E-commerce": ["Running shoes", "Wireless headphones", "Laptop computer", "Kitchen blender", "Smartphone", "Coffee maker", "Fitness tracker", "Gaming chair", "Fashion accessories", "Home decor"],
    "Retail": ["Fresh groceries", "Designer clothing", "Modern furniture", "Electronics", "Fashion items", "Home appliances", "Sports equipment", "Beauty products"],
    "Logistics": ["Courier service", "Package delivery", "Express shipping", "Freight transport", "Logistics solution", "Supply chain"],
    "Banking": ["Credit card", "Personal loan", "Insurance policy", "Savings account", "Investment plan", "Mobile banking", "Financial planning"],
    "Other": ["Conference event", "Online webinar", "Product launch", "Brand campaign", "Service announcement", "Educational course"]
}
themes = ["Urban", "Modern interior", "Outdoor", "Nature", "Office", "Studio", "Home", "Street", "Gym", "Minimalist background"]

# Updated styles based on ChatGPT image generation options (keeping common ones from original)
styles = [
    "Modern", "Bold", "Minimalist", "Luxury", "Professional", "Energetic", "Clean", "Elegant", "Dynamic",
    "Photo Shoot", "Cyberpunk", "Anime", "Dramatic Headshot", "Coloring Book", 
    "Retro Cartoon", "80s Glam", "Art Nouveau", "Synthwave"
]

# Style modifiers based on ChatGPT styles
style_modifiers = {
    "Modern": "modern design aesthetic, contemporary styling, clean lines",
    "Bold": "bold visual impact, strong contrast, striking composition",
    "Minimalist": "minimalist design, clean composition, subtle elements",
    "Luxury": "luxury aesthetic, premium materials, elegant presentation",
    "Professional": "professional appearance, business-ready, polished design",
    "Energetic": "dynamic energy, vibrant atmosphere, active composition",
    "Clean": "clean design, organized layout, crisp presentation",
    "Elegant": "elegant styling, sophisticated appearance, refined aesthetic",
    "Dynamic": "dynamic composition, movement, engaging visual flow",
    "Photo Shoot": "professional photography style, studio lighting, high-resolution commercial quality",
    "Cyberpunk": "futuristic cyberpunk aesthetic, neon lights, dark atmosphere, tech noir style",
    "Anime": "anime art style, vibrant colors, Japanese animation inspired, stylized character design",
    "Dramatic Headshot": "dramatic portrait style, professional headshot lighting, intense focus",
    "Coloring Book": "black and white line art, coloring book style, clean outlines, simple design",
    "Retro Cartoon": "vintage cartoon style, retro animation aesthetic, nostalgic character design",
    "80s Glam": "1980s glamour style, retro fashion, bold colors, vintage aesthetic",
    "Art Nouveau": "Art Nouveau style, decorative arts, flowing organic forms, elegant curves",
    "Synthwave": "synthwave aesthetic, retro-futuristic, neon colors, 80s sci-fi inspired"
}

# Text styling options based on context
text_styles = {
    "E-commerce": "bold, attention-grabbing text with high contrast",
    "Healthcare": "clean, professional typography, trustworthy appearance", 
    "Banking": "sophisticated, secure-looking text, professional font",
    "Retail": "eye-catching, promotional text, vibrant and clear",
    "Logistics": "clear, efficient-looking text, modern typography",
    "Other": "prominent, well-positioned text with good readability"
}

# Helper function to get text styling based on vertical and style
def get_text_styling(vertical, style, audience):
    base_style = text_styles.get(vertical, "prominent, well-positioned text with good readability")
    
    # Adjust based on visual style
    if style in ["Luxury", "Elegant", "Art Nouveau"]:
        return f"elegant, sophisticated typography, {base_style}"
    elif style in ["Bold", "Energetic", "Cyberpunk", "Synthwave"]:
        return f"bold, high-impact text with strong contrast, {base_style}"
    elif style in ["Minimalist", "Clean", "Professional"]:
        return f"clean, minimal typography, {base_style}"
    elif style in ["Retro Cartoon", "80s Glam"]:
        return f"stylized, retro-inspired text, {base_style}"
    else:
        return base_style

colors = ["White", "Black", "Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Navy", "Grey", "Gold", "Silver"]
audiences = ["General", "Young Adults", "Teenagers", "Families", "Parents", "Professionals", "Students", "Seniors", "Asian", "African", "European", "Middle Eastern", "Latino", "Urban millennials"]

# Background options
background_options = ["Opaque", "Transparent"]

# Helper function to build prompt
def build_prompt(vertical, product, theme, style, promo_text, color_palette, audience, include_text):
    # Audience context for visual representation
    if audience in ["Asian", "African", "European", "Middle Eastern", "Latino"]:
        people_context = f"lifestyle photography with {audience.lower()} cultural context"
    elif audience == "Families":
        people_context = "family-friendly setting, warm atmosphere"
    elif audience == "Young Adults":
        people_context = "trendy, contemporary lifestyle setting"
    elif audience == "Professionals":
        people_context = "professional, business environment"
    else:
        people_context = f"{audience.lower()} target demographic, appropriate lifestyle setting"
    
    # Color handling
    if len(color_palette) == 1:
        color_desc = f"{color_palette[0].lower()} dominant color scheme"
    else:
        color_desc = f"{' and '.join(color_palette).lower()} color palette"
    
    # Product focus
    product_desc = f"{product} as the hero product, prominently featured"
    
    # Environment
    setting_desc = f"{theme.lower()} environment, {people_context}"
    
    # Style description with specific modifiers
    style_desc = style_modifiers.get(style, f"{style.lower()} design aesthetic")
    
    # Text overlay (if included) - context-aware styling
    if include_text and promo_text.strip():
        text_styling = get_text_styling(vertical, style, audience)
        text_desc = f'Text overlay reading "{promo_text.strip()}" with {text_styling}, clearly readable, well-positioned'
    else:
        text_desc = "clean composition without text overlays"
    
    # Construct final prompt (removed copyright clause)
    prompt = (
        f"{product_desc} in {setting_desc}. "
        f"{style_desc} with {color_desc}. "
        f"{text_desc}. "
        f"High quality, marketing-ready image, square format 1024x1024."
    )
    
    return prompt

# Logo and title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    if os.path.exists("gms_logo.png"):
        st.image("gms_logo.png", width=120)
    else:
        st.markdown(f'<h2 style="color: {GMS_GREEN}; text-align: center; margin: 0;">GMS</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="gms-title">Content Builder MVP</div>', unsafe_allow_html=True)

# Main form
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Campaign Details</div>', unsafe_allow_html=True)

# Form layout
col1, col2 = st.columns([1, 1])

with col1:
    vertical = st.selectbox(
        "Industry Vertical", 
        verticals, 
        index=verticals.index(st.session_state.vertical) if st.session_state.vertical in verticals else 0,
        key="vertical_input"
    )
    
    # Custom input option
    product_options = ["Custom..."] + products[vertical]
    product_selection = st.selectbox(
        "Product / Service",
        product_options,
        index=1 if st.session_state.product in products[vertical] else 0,
        key="product_select"
    )
    
    if product_selection == "Custom...":
        product = st.text_input("Enter custom product/service:", key="custom_product", placeholder="e.g., Organic skincare cream")
    else:
        product = product_selection
    
    theme = st.selectbox(
        "Setting / Background",
        themes,
        index=themes.index(st.session_state.theme) if st.session_state.theme in themes else 0,
        key="theme_input"
    )
    
    style = st.selectbox(
        "Visual Style",
        styles,
        index=styles.index(st.session_state.style) if st.session_state.style in styles else 0,
        key="style_input",
        help="Choose from ChatGPT-style visual aesthetics"
    )

with col2:
    # Text overlay toggle
    include_text = st.checkbox("Include promotional text overlay", value=st.session_state.include_text, key="text_toggle")
    
    if include_text:
        promo_text = st.text_input(
            "Promotional Text", 
            value=st.session_state.promo_text,
            key="promo_input",
            placeholder="e.g., Summer Sale - 25% Off!"
        )
    else:
        promo_text = ""
    
    # Background transparency option
    background = st.selectbox(
        "Background Type",
        background_options,
        index=background_options.index(st.session_state.background) if st.session_state.background in background_options else 0,
        key="background_input",
        help="Choose opaque for solid background or transparent for PNG with transparency"
    )
    
    color_palette = st.multiselect(
        "Color Palette (1-3 colors)",
        colors,
        default=st.session_state.color_palette[:3],
        max_selections=3,
        key="color_input"
    )
    
    audience = st.selectbox(
        "Target Audience",
        audiences,
        index=audiences.index(st.session_state.audience) if st.session_state.audience in audiences else 0,
        key="audience_input",
        help="This helps AI understand the cultural/demographic context for appropriate representation"
    )

# Image specifications display
st.info("📐 Image Size: 1024×1024 pixels (Square format, optimized for social media)")

# Action buttons
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🔍 Preview Prompt", type="secondary"):
        if product.strip():
            st.session_state.show_preview = True
            st.session_state.prompt_preview = build_prompt(
                vertical, product, theme, style, promo_text, 
                color_palette, audience, include_text
            )
        else:
            st.warning("Please select or enter a product first.")

with col2:
    generate_clicked = st.button("🎨 Generate Visual", type="primary")

with col3:
    if st.button("🔄 Reset Form"):
        for key in ['vertical', 'product', 'theme', 'style', 'promo_text', 'color_palette', 'audience', 'background', 'show_preview', 'prompt_preview', 'include_text']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Prompt Preview Section
if st.session_state.show_preview and st.session_state.prompt_preview:
    st.markdown('<div class="preview-card">', unsafe_allow_html=True)
    st.markdown("#### 📝 Prompt Preview")
    st.text_area(
        "Generated prompt (you can edit before generating):",
        value=st.session_state.prompt_preview,
        height=120,
        key="editable_prompt"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Handle Generate
if generate_clicked:
    # Validate inputs
    if not product or product.strip() == "":
        st.error("❌ Please select or enter a product/service.")
    elif not color_palette:
        st.error("❌ Please select at least one color.")
    else:
        # Use edited prompt if available, otherwise build fresh
        if st.session_state.show_preview and 'editable_prompt' in st.session_state:
            final_prompt = st.session_state.editable_prompt
        else:
            final_prompt = build_prompt(
                vertical, product, theme, style, promo_text,
                color_palette, audience, include_text
            )
        
        with st.spinner("🎨 Generating your visual..."):
            try:
                # Get API key from secrets
                api_key = st.secrets["OPENAI_API_KEY"]
                openai.api_key = api_key
                
                # Prepare API parameters based on OpenAI gpt-image-1 specification
                api_params = {
                    "model": "gpt-image-1",
                    "prompt": final_prompt,
                    "size": "1024x1024",
                    "quality": "low",
                    "background": background.lower()  # "opaque" or "transparent"
                }
                
                # Make API call
                response = openai.images.generate(**api_params)
                
                # Handle response - gpt-image-1 returns URL for both transparent and opaque
                image_url = response.data[0].url
                img_response = requests.get(image_url)
                img_bytes = img_response.content
                
                st.success("✅ Visual generated successfully!")
                st.image(img_bytes, caption=f"Generated Image (1024×1024) - {background} Background", use_column_width=True)
                
                # Download button
                file_extension = "png"
                st.download_button(
                    label="📥 Download Image",
                    data=img_bytes,
                    file_name=f"campaign_{product.lower().replace(' ', '_')}_{style.lower().replace(' ', '_')}.{file_extension}",
                    mime=f"image/{file_extension}",
                    type="primary"
                )
                
                # Show used prompt
                with st.expander("📋 View generated prompt"):
                    st.code(final_prompt, language="text")
                    
            except Exception as e:
                st.error(f"❌ Image generation failed: {str(e)}")
                if "API key" in str(e):
                    st.info("💡 Make sure your OpenAI API key is properly set in Streamlit secrets.")
                elif "model" in str(e).lower():
                    st.info("💡 Please verify that 'gpt-image-1' is the correct model name for your API access.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; font-size: 0.9rem;'>Powered by GPT Image Generation | Built with Streamlit</div>", unsafe_allow_html=True)
