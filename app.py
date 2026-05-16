import streamlit as st
import google.generativeai as genai
import os
import io

# ─────────────────────────────────────────
# CONFIGURATION & MULTI-PROVIDER PRESETS
# ─────────────────────────────────────────
APP_TITLE = "🌊 HydroGeoAI Analyst Pro"
APP_ICON = "🛰️"

SYSTEM_PROMPTS = {
    "Hydro-GIS & Terrain Expert": (
        "You are an expert Hydro-GIS Assistant and Spatial Analyst specializing in terrain analysis. "
        "Provide production-ready Python snippets using ArcPy, GeoPandas, or WhiteboxTools. "
        "Focus on processing DEMs, sink filling, and prepping inputs for HEC-HMS/HEC-RAS. "
        "For regional Egyptian projects, use Egypt 1907 / Red Belt (EPSG:22991) or UTM Zone 36N (EPSG:32636)."
    ),
    "Remote Sensing Image Analyst": (
        "You are a remote sensing analyst. When an image is uploaded, examine its features, spectral properties, "
        "land cover layout, or drainage indices. Provide methodical, analytical descriptions."
    )
}

# Supported providers and models
PROVIDERS = {
    "Google Gemini": {
        "Gemini 2.5 Flash": "gemini-2.5-flash",
        "Gemini 2.5 Pro": "gemini-2.5-pro"
    },
    "Groq / OpenRouter Cloud": {
        "Llama 3.3 70B (Spatial)": "llama-3.3-70b-versatile",
    }
}

# Quick Action Prompt Presets
PRESET_PROMPTS = [
    {"label": "🕳️ Isolate Terrain Depressions", "text": "Write an ArcPy script to isolate depression areas by subtracting a raw DEM from a Filled DEM using Minus and Con tools."},
    {"label": "🌱 Calculate NDVI Formula", "text": "Explain how to calculate the Normalized Difference Vegetation Index (NDVI) using Sentinel-2 bands and provide a raster calculator expression."},
    {"label": "📌 Fix Messy Egyptian Address", "text": "Parse this messy Egyptian location string into Governorate, District, and Street: '١٢ ش التسعين الشمالي خلف المستشفى الجوي التجمع الخامس القاهرة'"}
]

# ─────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────
st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")
st.title(f"{APP_ICON} {APP_TITLE}")

# ─────────────────────────────────────────
# SIDEBAR CONFIGURATION
# ─────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Engine Settings")
    
    # 1. Multi-Provider Selection
    provider_choice = st.selectbox("API Provider", list(PROVIDERS.keys()))
    model_choice = st.selectbox("Model Architecture", list(PROVIDERS[provider_choice].keys()))
    model_id = PROVIDERS[provider_choice][model_choice]
    
    # 2. Dynamic API Key Management
    env_var_name = "GOOGLE_API_KEY" if provider_choice == "Google Gemini" else "GROQ_API_KEY"
    api_key = st.text_input(
        f"{provider_choice} Key", 
        type="password", 
        value=os.environ.get(env_var_name, ""),
        help=f"Loaded from environment if left blank."
    )
    
    # 3. Domain Specialty Selection
    preset_specialty = st.selectbox("Domain Specialty", list(SYSTEM_PROMPTS.keys()))
    system_instruction = SYSTEM_PROMPTS[preset_specialty]
    
    st.markdown("---")
    
    # 4. Chat Management & Export Utilities
    st.subheader("🛠️ Utilities")
    if st.button("🗑️ Reset Chat Log", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─────────────────────────────────────────
# CORE APPLICATION LOGIC
# ─────────────────────────────────────────

# Initialize persistent memory structures
if "messages" not in st.session_state:
    st.session_state.messages = []

# Dynamic Real-time Token Counter Metric
# Simple heuristic estimation (~4 characters per token) for tracking UI overhead
total_chars = sum(len(m["content"]) for m in st.session_state.messages)
estimated_tokens = int(total_chars / 4)
st.metric(label="Estimated Conversational Token Counter", value=f"{estimated_tokens} tokens")

# 📥 IMAGE MULTI-MODAL UPLOAD SECTION
uploaded_file = st.file_uploader(
    "🛰️ Optional: Drop Satellite/Map Imagery for Multi-Modal Processing", 
    type=["png", "jpg", "jpeg"]
)
uploaded_image_bytes = None

if uploaded_file is not None:
    st.image(uploaded_file, caption="Staged Input Raster Matrix", width=350)
    uploaded_image_bytes = uploaded_file.read()

# 🎛️ PRESET PROMPT INTERFACE QUICK-BUTTONS
st.markdown("##### ⚡ Quick Structural Pipelines")
cols = st.columns(len(PRESET_PROMPTS))
clicked_preset_text = None

for idx, preset_btn in enumerate(PRESET_PROMPTS):
    if cols[idx].button(preset_btn["label"], use_container_width=True):
        clicked_preset_text = preset_btn["text"]

# Render Existing History Context
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Capture Input from Either Text Box or Quick Preset Button
user_input = st.chat_input("Input spatial syntax parameters or prompt requirements...")
if clicked_preset_text:
    user_input = clicked_preset_text

# ─────────────────────────────────────────
# ─────────────────────────────────────────
# STREAMING RESPONSES VIA LLM ENGINE
# ─────────────────────────────────────────
if user_input:
    # Render user prompt input block
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Provider routing block
    if provider_choice == "Google Gemini":
        if not api_key:
            st.error("🔑 Verification Exception: Please plug your API Key into the configuration panel.")
        else:
            genai.configure(api_key=api_key)
            try:
                model = genai.GenerativeModel(
                    model_name=model_id,
                    system_instruction=system_instruction
                )
                payload = [user_input]
                if uploaded_image_bytes:
                    payload.append({
                        "mime_type": uploaded_file.type,
                        "data": uploaded_image_bytes
                    })
                
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    accumulated_response = ""
                    response_stream = model.generate_content(payload, stream=True)
                    for chunk in response_stream:
                        accumulated_response += chunk.text
                        response_placeholder.markdown(accumulated_response + "▌")
                    response_placeholder.markdown(accumulated_response)
                
                st.session_state.messages.append({"role": "assistant", "content": accumulated_response})
                st.rerun()
                
            except Exception as e:
                st.error(f"Execution Halt across Gemini Hub: {str(e)}")
                
    else:
        # ─── THIS IS THE EXACT BLOCK YOU NEED TO OVERWRITE ───
        if not api_key:
            st.error("🔑 Verification Exception: Please plug your Groq API Key into the configuration panel.")
        else:
            try:
                from groq import Groq
                client = Groq(api_key=api_key)
                
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    accumulated_response = ""
                    
                    response_stream = client.chat.completions.create(
                        model=model_id,
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": user_input}
                        ],
                        stream=True,
                    )
                    
                    for chunk in response_stream:
                        if chunk.choices[0].delta.content:
                            accumulated_response += chunk.choices[0].delta.content
                            response_placeholder.markdown(accumulated_response + "▌")
                    response_placeholder.markdown(accumulated_response)
                
                st.session_state.messages.append({"role": "assistant", "content": accumulated_response})
                st.rerun()
                
            except Exception as e:
                st.error(f"Execution Halt across Groq Hub: {str(e)}")

# ─────────────────────────────────────────
# EXPORT MODULE (MARKDOWN DOWNLOADER)
# ─────────────────────────────────────────
if st.session_state.messages:
    st.markdown("---")  # <-- Your lines live right here!
    
    markdown_buffer = io.StringIO()
    markdown_buffer.write(f"# {APP_TITLE} Export Logs\n\n")
    for msg in st.session_state.messages:
        role_tag = "### 🧑 User Input" if msg["role"] == "user" else "### 🤖 Assistant Solution"
        markdown_buffer.write(f"{role_tag}\n\n{msg['content']}\n\n---\n\n")
        
    st.download_button(
        label="📥 Export Complete Chat Logs (.MD)",
        data=markdown_buffer.getvalue(),
        file_name="hydrogeo_session_export.md",
        mime="text/markdown",
        use_container_width=True
    )