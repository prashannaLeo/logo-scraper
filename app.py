import os
import re
import base64
import io
from PIL import Image
import streamlit as st

# Import the logo scraper logic
from scrape_logos import scrape_logo

# Set up page configurations (Modern dark, wide, expanded sidebar)
st.set_page_config(
    page_title="LogoGrabber Pro — Premium Brand Logo Scraper",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom Styling (Deep Carbon Theme, Neon Glow Accents, Total Branding Override)
PREMIUM_DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* ── Global Styles & Brand Overrides ───────────────────────────────────────── */

/* Completely hide Streamlit default brand headers, footers, decoration, and menus */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stHeader"] {display: none;}
[data-testid="stSidebarHeader"] {display: none;}

/* Define modern variables and typography */
:root {
    --bg-dark: #070913;
    --bg-card: #0f1324;
    --bg-sidebar: #05060c;
    --accent-indigo: #6366f1;
    --accent-purple: #8b5cf6;
    --accent-pink: #ec4899;
    --border-color: rgba(255, 255, 255, 0.08);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
}

html, body, [data-testid="stAppViewContainer"], .stWidgetForm {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-dark) !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
}

/* ── Hero Gradient Title ─────────────────────────────────────────────────── */
.premium-title-card {
    padding: 2rem;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.04) 0%, rgba(139, 92, 246, 0.04) 100%);
    border: 1px solid rgba(99, 102, 241, 0.15);
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.02);
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.premium-title-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--accent-indigo), var(--accent-purple), var(--accent-pink));
}

.glow-title {
    font-size: 2.8rem;
    font-weight: 850;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #a5b4fc 0%, #c084fc 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.6rem;
    text-shadow: 0 0 30px rgba(99, 102, 241, 0.2);
}

.premium-subtitle {
    font-size: 1.05rem;
    color: var(--text-secondary);
    font-weight: 450;
    max-width: 600px;
    margin: 0 auto;
    opacity: 0.85;
}

/* ── Form Inputs & Glowing Textfields ─────────────────────────────────────── */
div[data-testid="stTextInput"] input {
    background-color: rgba(255, 255, 255, 0.02) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease !important;
    font-size: 0.95rem !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent-purple) !important;
    box-shadow: 0 0 15px rgba(139, 92, 246, 0.15) !important;
    background-color: rgba(255, 255, 255, 0.04) !important;
}

/* Form block outline fix */
div[data-testid="stForm"] {
    border: 1px solid var(--border-color) !important;
    background-color: rgba(255, 255, 255, 0.01) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
}

/* ── Glassmorphic Active Display Canvas ───────────────────────────────────── */
.premium-canvas-card {
    border-radius: 20px;
    padding: 3rem;
    background: radial-gradient(circle at top left, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.005));
    border: 1px solid var(--border-color);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    transition: all 0.4s ease;
    min-height: 250px;
}

.premium-canvas-card::before {
    content: '';
    position: absolute;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.06) 0%, transparent 70%);
    top: -50px; left: -50px;
    pointer-events: none;
}

.premium-canvas-card:hover {
    border-color: rgba(139, 92, 246, 0.25);
    box-shadow: 0 20px 50px rgba(139, 92, 246, 0.08);
}

.premium-logo-display {
    max-width: 100%;
    max-height: 240px;
    object-fit: contain;
    border-radius: 12px;
    padding: 1rem;
    filter: drop-shadow(0 10px 20px rgba(0,0,0,0.3));
    transition: transform 0.3s ease;
}

.premium-logo-display:hover {
    transform: scale(1.02);
}

/* ── Sidebar & History Components ─────────────────────────────────────────── */
.sidebar-header-custom {
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #a5b4fc, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid var(--border-color);
}

/* Rendered history container row items */
div[data-testid="stSidebar"] div[data-testid="column"] {
    background: rgba(255, 255, 255, 0.01) !important;
    border-radius: 10px !important;
    padding: 4px 8px !important;
    margin-bottom: 6px !important;
    border: 1px solid rgba(255, 255, 255, 0.03) !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
}

div[data-testid="stSidebar"] div[data-testid="column"]:hover {
    background: rgba(255, 255, 255, 0.03) !important;
    border-color: rgba(99, 102, 241, 0.25) !important;
}

/* Beautiful Action Buttons inside Sidebar */
div[data-testid="stSidebar"] button {
    background-color: rgba(255, 255, 255, 0.02) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 2px 6px !important;
    min-height: 28px !important;
    height: 28px !important;
    line-height: 1 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stSidebar"] button:hover {
    background-color: var(--accent-indigo) !important;
    border-color: var(--accent-indigo) !important;
    color: #ffffff !important;
    box-shadow: 0 0 10px rgba(99, 102, 241, 0.35) !important;
    transform: scale(1.05);
}

/* All Primary Action Buttons (Download, Form Submit) */
div[data-testid="stFormSubmitButton"] button,
button[data-testid="stBaseButton-primary"],
button[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, var(--accent-indigo), var(--accent-purple)) !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stFormSubmitButton"] button:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(90deg, var(--accent-purple), var(--accent-pink)) !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.3) !important;
    transform: translateY(-1px) !important;
}

/* Force bright crisp white text on ALL primary button elements (paragraphs, spans, text) */
div[data-testid="stFormSubmitButton"] button p,
div[data-testid="stFormSubmitButton"] button span,
button[data-testid="stBaseButton-primary"] p,
button[data-testid="stBaseButton-primary"] span,
button[data-testid="baseButton-primary"] p,
button[data-testid="baseButton-primary"] span {
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}

/* Premium Destructive Secondary Action Buttons (e.g. Delete Brand from Canvas) */
button[data-testid="stBaseButton-secondary"],
button[data-testid="baseButton-secondary"] {
    background-color: rgba(255, 255, 255, 0.02) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    font-weight: 650 !important;
    font-size: 0.92rem !important;
    transition: all 0.3s ease !important;
}

button[data-testid="stBaseButton-secondary"] p,
button[data-testid="stBaseButton-secondary"] span,
button[data-testid="baseButton-secondary"] p,
button[data-testid="baseButton-secondary"] span {
    color: var(--text-secondary) !important;
    transition: color 0.3s ease !important;
}

button[data-testid="stBaseButton-secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover {
    background-color: rgba(239, 68, 68, 0.08) !important;
    border-color: rgba(239, 68, 68, 0.35) !important;
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.12) !important;
}

button[data-testid="stBaseButton-secondary"]:hover p,
button[data-testid="stBaseButton-secondary"]:hover span,
button[data-testid="baseButton-secondary"]:hover p,
button[data-testid="baseButton-secondary"]:hover span {
    color: #fca5a5 !important;
}


/* Specs Badge Elements */
.badge-custom {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 5px 12px;
    border-radius: 12px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Styled info tables inside details card */
.premium-info-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 0.5rem;
}

.premium-info-table td {
    padding: 12px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 0.9rem;
}

.premium-info-table td.label {
    font-weight: 600;
    color: var(--text-secondary);
    width: 32%;
}

.premium-info-table td.val {
    font-weight: 500;
    color: var(--text-primary);
}

.premium-info-table td.val a {
    color: #818cf8 !important;
    text-decoration: none !important;
    transition: color 0.2s ease;
}

.premium-info-table td.val a:hover {
    color: #a5b4fc !important;
    text-decoration: underline !important;
}

/* Toast styling override to dark standard */
div[data-testid="stNotification"] {
    background-color: #0f172a !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}

</style>
"""
st.markdown(PREMIUM_DARK_CSS, unsafe_allow_html=True)

STORAGE_JS = """
<script>
(function() {
    const LS_KEY = 'logo_map_base64';
    function encode(h) {
        try { return JSON.stringify(h); } catch(e) { return ''; }
    }
    function saveList() {
        try {
            const rows = [];
            const items = window.streamlitSessionStorage || [];
            (window.__streamlitSessionState || {}).history
            let history = [];
            try { history = window.streamlit?.['last_history_v1'] || []; } catch(e) {}
            if (!history.length) {
                const stored = localStorage.getItem(LS_KEY);
                if (stored) {
                    try { history = JSON.parse(stored); } catch(e) {}
                }
            }
            if (!history.length) {
                try {
                    const raw = sessionStorage.getItem(LS_KEY);
                    if (raw) history = JSON.parse(raw);
                } catch(e) {}
            }
            if (history.length) {
                localStorage.setItem(LS_KEY, JSON.stringify(history));
            }
        } catch(e) {}
    }
    function patchSubmit() {
        window.persistLogoMap = function(data) {
            const rows = data || [];
            localStorage.setItem(LS_KEY, JSON.stringify(rows));
            try {
                window.streamlit.setComponentValue && window.streamlit.setComponentValue({type:'storage',storage:'localStorage',key:LS_KEY,value:JSON.stringify(rows)});
            } catch(e) {}
        };
    }
    if (document.readyState === 'loading') {
        window.addEventListener('DOMContentLoaded', patchSubmit);
    } else {
        patchSubmit();
    }
})();
</script>
"""
st.markdown(STORAGE_JS, unsafe_allow_html=True)

# ── Helper Functions ──────────────────────────────────────────────────────────

def resolve_input(user_input: str) -> str:
    """Resolves website URLs or company names into valid scraping URLs."""
    user_input = user_input.strip()
    if not user_input:
        return ""

    if user_input.startswith(("http://", "https://")):
        return user_input

    if "." in user_input and " " not in user_input:
        return f"https://{user_input}"

    cleaned_name = re.sub(r"[^\w\-]", "", user_input).lower()
    if cleaned_name:
        return f"https://{cleaned_name}.com"

    return ""

def get_image_base64(filepath: str) -> str:
    """Reads a local file and returns its Base64 string."""
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

def get_download_data(saved_file_path: str):
    """
    Converts local image to PNG using PIL in memory. Falls back to raw bytes
    for unsupported types like SVG to maintain maximum details.
    """
    ext = os.path.splitext(saved_file_path)[-1].lower()
    if ext == ".png":
        with open(saved_file_path, "rb") as f:
            return f.read(), "image/png", ".png"
    elif ext == ".svg":
        with open(saved_file_path, "rb") as f:
            return f.read(), "image/svg+xml", ".svg"
    else:
        try:
            img = Image.open(saved_file_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue(), "image/png", ".png"
        except Exception:
            with open(saved_file_path, "rb") as f:
                mime = f"image/{ext.lstrip('.')}" if ext else "image/png"
                return f.read(), mime, ext or ".png"

# ── High-Performance Session State Initialization (Base64 Memory Caching) ──────

if "history" not in st.session_state:
    st.session_state.history = []
    
    # Pre-seed and cache history items once on startup
    csv_path = os.path.join("logos", "_logo_map.csv")
    if os.path.exists(csv_path):
        import csv
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("status", "").startswith("ok"):
                        strategy = row["status"].split(":")[-1]
                        saved_file = row["saved_file"].replace("\\", "/")
                        if os.path.exists(saved_file):
                            # CACHE BASE64 IN STATE ONCE: Eliminates disk access in page loops!
                            b64_str = get_image_base64(saved_file)
                            if b64_str:
                                st.session_state.history.append({
                                    "site": row["site"],
                                    "domain": row["domain"],
                                    "logo_url": row["logo_url"],
                                    "saved_file": saved_file,
                                    "strategy": strategy,
                                    "base64_data": b64_str  # Caching base64 data directly in memory!
                                })
        except Exception:
            pass

if "active_logo" not in st.session_state:
    if st.session_state.history:
        st.session_state.active_logo = st.session_state.history[0]
    else:
        st.session_state.active_logo = None

# Sidebar History Operations
def add_to_history(result: dict):
    # Eliminate duplicate domains, place at index 0
    st.session_state.history = [h for h in st.session_state.history if h["domain"] != result["domain"]]
    st.session_state.history.insert(0, result)

def delete_history_item(domain: str):
    st.session_state.history = [h for h in st.session_state.history if h["domain"] != domain]
    if st.session_state.active_logo and st.session_state.active_logo["domain"] == domain:
        if st.session_state.history:
            st.session_state.active_logo = st.session_state.history[0]
        else:
            st.session_state.active_logo = None

def clear_all_history():
    st.session_state.history = []
    st.session_state.active_logo = None

# ── Main Application Interface ────────────────────────────────────────────────

# Premium SaaS Hero Card
st.markdown("""
<div class="premium-title-card">
    <div class="glow-title">🎨 LogoGrabber Pro</div>
    <div class="premium-subtitle">Instantly extract, view, and download crystal-clear brand logos from any website or company name using high-performance scraping engines.</div>
</div>
""", unsafe_allow_html=True)

col_main, col_spacer = st.columns([7, 3])

with col_main:
    # ── Input Section ─────────────────────────────────────────────────────────
    st.markdown("### 🔍 Fetch Brand Logo")
    
    with st.form("logo_fetch_form", clear_on_submit=False):
        user_input = st.text_input(
            "Enter Company Name or website URL:",
            placeholder="e.g. Stripe, OpenAI, github.com",
            help="Provide a website address or simple brand name. Our parsing engine resolves it automatically."
        )
        submitted = st.form_submit_button("🚀 Fetch Brand Logo", use_container_width=True)

    if submitted:
        if not user_input.strip():
            st.warning("⚠️ Please provide a company name or website domain.")
        else:
            resolved_url = resolve_input(user_input)
            domain = resolved_url.split("//")[-1].split("/")[0].replace("www.", "")
            
            st.toast(f"🌐 Resolving brand input: {domain}", icon="🌐")
            
            # Fetch with elegant UI spinner
            with st.spinner(f"🚀 Scraping high-resolution logo for {domain}..."):
                try:
                    out_directory = "logos"
                    os.makedirs(out_directory, exist_ok=True)
                    
                    # Core scraping call
                    res = scrape_logo(resolved_url, out_directory)
                    
                    if res and res.get("status", "").startswith("ok"):
                        strategy = res["status"].split(":")[-1]
                        saved_file = res["saved_file"]
                        
                        # Load and cache base64 for the newly scraped logo
                        b64_str = get_image_base64(saved_file)
                        
                        history_entry = {
                            "site": res["site"],
                            "domain": res["domain"],
                            "logo_url": res["logo_url"],
                            "saved_file": saved_file,
                            "strategy": strategy,
                            "base64_data": b64_str  # Cached instantly in memory!
                        }
                        
                        # Append and set active
                        add_to_history(history_entry)
                        st.session_state.active_logo = history_entry
                        
                        st.toast(f"🎉 Successfully scraped logo via {strategy}!", icon="🎉")
                        st.rerun()
                    else:
                        st.error(f"❌ Could not retrieve a brand logo for **{domain}**. We tested favicon links, apple headers, clearbit, and fallback services, but none succeeded.")
                except Exception as e:
                    st.error(f"⚠️ Scraping engine exception occurred: {e}")

    # ── Display Active Logo Canvas ────────────────────────────────────────────
    if st.session_state.active_logo:
        active = st.session_state.active_logo
        st.markdown("---")
        st.markdown(f"### 🖼️ Active Logo Preview: **{active['domain']}**")
        
        disp_cols = st.columns([5, 5])
        
        with disp_cols[0]:
            # HIGH PERFORMANCE: Read Base64 directly from memory cache (0ms disk reads!)
            b64_str = active.get("base64_data", "")
            if not b64_str:
                # Fallback if cache is missing
                b64_str = get_image_base64(active["saved_file"])
                active["base64_data"] = b64_str
                
            file_ext = os.path.splitext(active["saved_file"])[-1].lower().replace(".", "")
            
            if b64_str:
                st.markdown(f"""
                <div class="premium-canvas-card">
                    <img class="premium-logo-display" src="data:image/{file_ext};base64,{b64_str}" alt="{active['domain']} logo">
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Error displaying active logo.")

        with disp_cols[1]:
            # Specs and Info details
            strategy_name = active["strategy"]
            
            # Map strategies to modern colors
            color_map = {
                "link-icon": "linear-gradient(135deg, #3b82f6, #1d4ed8)",
                "apple-touch-icon": "linear-gradient(135deg, #10b981, #047857)",
                "clearbit": "linear-gradient(135deg, #8b5cf6, #6d28d9)",
                "favicon.ico": "linear-gradient(135deg, #f59e0b, #b45309)",
                "google-favicon": "linear-gradient(135deg, #ec4899, #be185d)"
            }
            
            # Find closest strategy color
            matching_gradient = color_map.get("favicon.ico")  # Default
            for k, v in color_map.items():
                if k in strategy_name.lower():
                    matching_gradient = v
                    break
            
            badge_html = f'<span class="badge-custom" style="background: {matching_gradient};">{strategy_name}</span>'
            
            st.markdown(f"""
            <table class="premium-info-table">
                <tr>
                    <td class="label">Target Domain</td>
                    <td class="val"><code>{active['domain']}</code></td>
                </tr>
                <tr>
                    <td class="label">Resolved Source URL</td>
                    <td class="val"><a href="{active['site']}" target="_blank">{active['site']}</a></td>
                </tr>
                <tr>
                    <td class="label">Detection Engine</td>
                    <td class="val">{badge_html}</td>
                </tr>
                <tr>
                    <td class="label">Direct Image Link</td>
                    <td class="val"><a href="{active['logo_url']}" target="_blank">View Original Source</a></td>
                </tr>
                <tr>
                    <td class="label">Local Cache Filename</td>
                    <td class="val"><code>{os.path.basename(active['saved_file'])}</code></td>
                </tr>
            </table>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Handle download conversions
            download_bytes, mime_type, file_suffix = get_download_data(active["saved_file"])
            clean_domain = active["domain"].replace(".", "_")
            download_filename = f"{clean_domain}_logo{file_suffix}"
            
            btn_label = f"📥 Download as PNG" if file_suffix == ".png" else f"📥 Download Original ({file_suffix.upper().replace('.', '')})"
            
            st.download_button(
                label=btn_label,
                data=download_bytes,
                file_name=download_filename,
                mime=mime_type,
                type="primary",
                use_container_width=True
            )
            
            # Sidebar Mutating Quick Delete
            if st.button("🗑️ Delete from Search History", type="secondary", use_container_width=True):
                delete_history_item(active["domain"])
                st.toast(f"Pruned logo '{active['domain']}' from search history.", icon="🗑️")
                st.rerun()

    else:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.info("💡 Enter a company name or website domain above to fetch a brand logo. Successfully scraped logos will display here with download links and full technical metadata.")

# ── Sidebar Navigation / Fast History Panel ──────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-header-custom">📜 Search History</div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.markdown("<div style='opacity: 0.6; font-style: italic; padding: 10px;'>No history found. Try fetching a brand logo first.</div>", unsafe_allow_html=True)
    else:
        # Display history panel list items
        for h in list(st.session_state.history):
            h_cols = st.columns([1.5, 4.5, 2, 2])
            
            with h_cols[0]:
                # HIGH PERFORMANCE: Read Base64 directly from cache (0ms disk lag!)
                thumb_b64 = h.get("base64_data", "")
                if not thumb_b64:
                    thumb_b64 = get_image_base64(h["saved_file"])
                    h["base64_data"] = thumb_b64
                    
                thumb_ext = os.path.splitext(h["saved_file"])[-1].lower().replace(".", "")
                
                if thumb_b64:
                    st.markdown(f'<img src="data:image/{thumb_ext};base64,{thumb_b64}" style="width: 26px; height: 26px; object-fit: contain; border-radius: 4px; background: transparent; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));" />', unsafe_allow_html=True)
                else:
                    st.markdown("🖼️")
                    
            with h_cols[1]:
                domain_display = h["domain"]
                if len(domain_display) > 13:
                    domain_display = domain_display[:11] + "..."
                st.markdown(f"<div style='font-weight: 600; font-size: 0.88rem; line-height: 1.8; color: var(--text-primary);'>{domain_display}</div>", unsafe_allow_html=True)
                
            with h_cols[2]:
                # Instant View (Under 1ms due to memory caching!)
                if st.button("👁️", key=f"view_{h['domain']}", help=f"View {h['domain']}", use_container_width=True):
                    st.session_state.active_logo = h
                    
            with h_cols[3]:
                # Instant Delete
                if st.button("🗑️", key=f"del_{h['domain']}", help=f"Remove {h['domain']}", use_container_width=True):
                    delete_history_item(h["domain"])
                    
        st.markdown("<br><hr style='opacity: 0.08;'><br>", unsafe_allow_html=True)
        
        # Clear All control
        if st.button("🔴 Clear All History", type="secondary", use_container_width=True):
            clear_all_history()
            st.toast("Cleared history successfully!", icon="🔴")
            st.rerun()
