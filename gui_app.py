import streamlit as st
import numpy as np
from PIL import Image
import io
import cv2
import stego_engine as stego  
import os

st.set_page_config(
    page_title="Embedding Encrypted Playload in Images via Steganography ",
    layout="wide"
)

st.markdown("""
    <style>
    /* Global App Container Framework Background */
    .stApp {
        background-color: #080511;
    }
    
    /* Enforce Consistent Pale Violet Text Across Headers and Widgets */
    h1, h2, h3, h4, p, span, label, div[data-testid="stMarkdownContainer"] p {
        color: #E6DFF2 !important;
    }

    /* ========================================================
        FIXED: TARGETING THE INNER FLEX CONTAINER FOR THE GAP
       ======================================================== */
    /* Target the actual inner container holding the segmented control buttons */
    div[data-testid="stSegmentedControl"] > div {
        display: flex !important;
        gap: 50px !important; /* FORCES A MASSIVE GAP BETWEEN THE TOGGLE BUTTONS */
        width: 100% !important;
    }
    
    /* Make each button an independent block with its own rounded corners */
    div[data-testid="stSegmentedControl"] button {
        flex: 1 !important;
        background-color: #130E26 !important;
        color: #C77DFF !important;
        border: 2px solid #3C096C !important;
        padding: 20px 24px !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        border-radius: 12px !important; /* Forces independent pill shapes instead of a glued bar */
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }

    /* Deep Purple Visual Highlights for Selected Option Segments */
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background-color: #5A189A !important;
        color: #FFFFFF !important;
        border-color: #9D4EDD !important;
        box-shadow: 0 0 18px rgba(131, 56, 236, 0.6) !important;
    }

    /* Hover States for Unselected Segment Blocks */
    div[data-testid="stSegmentedControl"] button:hover:not([aria-checked="true"]) {
        background-color: #1C1435 !important;
        border-color: #7B2CBF !important;
    }

    /* ========================================================
        DIAGLOG MODAL WINDOWS & FIELD SPACING CONFIGURATIONS
       ======================================================== */
    div[data-testid="stModal"] {
        background-color: #0E0A1F !important;
        border: 2px solid #5A189A !important;
        border-radius: 14px !important;
        box-shadow: 0 0 30px rgba(90, 24, 154, 0.5) !important;
        padding: 30px !important;
    }

    /* Explicit Generous Vertical Spacing Matrix Between Modal Content Form Fields */
    div[data-testid="stModal"] div.stSelectbox, 
    div[data-testid="stModal"] div.stTextInput {
        margin-top: 14px !important;
        margin-bottom: 38px !important;
    }
    
    /* Global Interactive Action Buttons Style */
    div.stButton > button {
        background-color: #1A1235 !important;
        color: #C77DFF !important;
        border: 2px solid #3C096C !important;
        border-radius: 8px !important;
        padding: 14px 28px !important;
        font-weight: bold !important;
        width: 100% !important;
        margin-top: 20px !important;    
        margin-bottom: 10px !important; 
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        background-color: #3C096C !important;
        color: #E0AAFF !important;
        border: 2px solid #6C22D6 !important;
    }
    
    /* Dialog Confirmation Primary Triggers */
    div[data-testid="stModal"] div.stButton > button {
        background-color: #5A189A !important;
        color: #FFFFFF !important;
        border: 2px solid #9D4EDD !important;
        margin-top: 30px !important; 
    }
    div[data-testid="stModal"] div.stButton > button:hover {
        background-color: #6C22D6 !important;
        box-shadow: 0 0 15px #8338EC !important;
    }

    /* Forms Focus Borders */
    div[data-baseweb="input"]:focus-within, 
    div[data-baseweb="select"]:focus-within, 
    div[data-baseweb="textarea"]:focus-within {
        border-color: #9D4EDD !important;
        box-shadow: 0 0 10px rgba(157, 78, 221, 0.5) !important;
    }

    /* Read-Only Terminal Console Viewport Box */
    .terminal-box {
        background-color: #05030A !important;
        border: 1px solid #241942 !important;
        border-left: 5px solid #6C22D6 !important;
        border-radius: 8px;
        padding: 16px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 13px;
        height: 160px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)


if "terminal_logs" not in st.session_state:
    st.session_state.terminal_logs = [
        ("<span style='color: #9D4EDD;'>[SYSTEM]</span> <span style='color: #E0AAFF;'>Initialization complete. Purple Core LSB Engine Active.</span>")
    ]
if "uploader_id" not in st.session_state:
    st.session_state.uploader_id = 0
if "decrypted_message" not in st.session_state:
    st.session_state.decrypted_message = ""
if "injection_ready" not in st.session_state:
    st.session_state.injection_ready = False
if "execution_status" not in st.session_state:
    st.session_state.execution_status = None

def log_terminal(sender, message, level="INFO"):
    color = "#E0AAFF" if level == "INFO" else "#FF5573"
    log_entry = f"<span style='color: #9D4EDD;'>[{sender}]</span> <span style='color: {color};'>{message}</span>"
    st.session_state.terminal_logs.append(log_entry)

def clear_all_buffers():
    st.session_state.uploader_id += 1
    st.session_state.decrypted_message = ""
    st.session_state.injection_ready = False
    st.session_state.execution_status = None
    if "secret_text_input" in st.session_state:
        st.session_state.secret_text_input = ""
        
    # Dynamically read the upcoming mode view state
    next_mode = st.session_state.get("global_mode_toggle_switch", "🔒 ENCRYPTION (ENCODE MODE)")
    
    if "ENCRYPTION" in next_mode:
        st.session_state.terminal_logs = [
            ("<span style='color: #9D4EDD;'>[SYSTEM]</span> <span style='color: #E0AAFF;'>Context switched. Purple Core LSB ENCODER Initialized.</span>")
        ]
    else:
        st.session_state.terminal_logs = [
            ("<span style='color: #9D4EDD;'>[SYSTEM]</span> <span style='color: #E0AAFF;'>Context switched. Purple Core LSB DECODER Initialized.</span>")
        ]


@st.dialog("🔮 Configure Key")
def show_encryption_modal(msg, cv2_img):
    
    password = st.text_input(
        "CRYPTOGRAPHIC SECRET PASSPHRASE KEY",
        type="password",
        placeholder="Enter master key for AES-256-GCM derivation..."
    )
    
    st.write("")
    if st.button("✨ Inject Encrypted Payload"):
        if not password:
            st.session_state.execution_status = {
                "type": "ERROR", 
                "msg": "Failed Encryption Request: Cryptographic master key phrase field cannot be empty."
            }
            log_terminal("CRYPT", "Operation aborted: Master key phrase authentication field is blank.", "ERROR")
            st.rerun()
        else:
            log_terminal("ENGINE", "Compressing & Encrypting Data via AES-256-GCM Protocol...")
            log_terminal("ENGINE", "Embedding bits seamlessly into target spatial layer matrix using LSB Rules.")
            
            try:
                # 1. Generate encrypted binary bitstream string from the engine
                payload = stego.encrypt_message(message=msg, password=password)
                
                # Convert the raw bit stream string to a readable clean HEX format for clear terminal viewing
                # We skip the tracking flags (first 40 bits) to display the pure encrypted cipher payload
                crypto_bits = payload[40:]
                hex_payload = "".join([format(int(crypto_bits[i:i+8], 2), '02X') for i in range(0, len(crypto_bits), 8)])
                
                out_img = stego.hide_data_lsb(cv2_img, payload, password)
                file_ext = ".png"
                mime_type = "image/png"
                    
                _, encoded_buffer = cv2.imencode(file_ext, out_img)
                stego_bytes = encoded_buffer.tobytes()
                
                st.session_state.injection_ready = True
                st.session_state.file_payload = stego_bytes  
                st.session_state.stego_filename = f"stego_output_lsb{file_ext}"
                st.session_state.stego_mime = mime_type
                
                st.session_state.execution_status = {
                    "type": "SUCCESS", 
                    "msg": "Success: Alphanumeric contents embedded within pixel arrays using LSB matrix techniques."
                }
                
                # --- REQUIREMENT INJECTION: LOG ENCRYPTED PAYLOAD ---
                log_terminal("SUCCESS", f"AFTER SUCCESSFUL ENCRYPTION IN ENCRYPT MODE [ENCRYPTED PAYLOAD] : {hex_payload}", "INFO")
                log_terminal("SUCCESS", "Payload bound to system container successfully via LSB.", "SUCCESS")
                st.toast("Injection Complete!", icon="🔮")
                st.rerun()
                
            except Exception as e:
                st.session_state.execution_status = {
                    "type": "ERROR", 
                    "msg": f"Injection Fault: {str(e)}"
                }
                log_terminal("ERROR", f"Core engine failed during processing: {str(e)}", "ERROR")
                st.rerun()

@st.dialog("🔓 Extraction & Decryption Authentication")
def show_decryption_modal(cv2_img):
    
    password = st.text_input(
        "INPUT CRYPTOGRAPHIC VERIFICATION KEY",
        type="password",
        placeholder="Enter authorization key code sequence..."
    )
    
    st.write("")
    if st.button("⚡ Execute Extraction & Decryption Protocol"):
        if not password:
            st.error("Failed Decryption Request: Passphrase authentication field is empty.")
            log_terminal("CRYPT", "Operation aborted: Verification key field is blank.", "ERROR")
        else:
            log_terminal("ENGINE", "Scanning image spatial layers and processing authentication tags...")
            
            try:
                extracted_raw = stego.extract_data_from_matrix(cv2_img, password)
                
                if isinstance(extracted_raw, str) and "CRITICAL_ERROR" in extracted_raw:
                    st.session_state.decrypted_message = extracted_raw
                    st.session_state.execution_status = {
                        "type": "ERROR", 
                        "msg": "Extraction System Failure: Bitstream validation failure or digital signature check rejected."
                    }
                    log_terminal("SECURITY", extracted_raw, "ERROR")
                else:
                    # Convert extracted bytes payload cleanly to UPPERCASE Hex string for terminal log visibility
                    hex_extracted = extracted_raw.hex().upper()
                    
                    cleartext = stego.decrypt_message(extracted_raw, password)
                    
                    if "❌" in cleartext:
                        st.session_state.decrypted_message = cleartext
                        st.session_state.execution_status = {
                            "type": "ERROR", 
                            "msg": "Extraction System Failure: Identity authentication signature rejected."
                        }
                        log_terminal("SECURITY", cleartext, "ERROR")
                    else:
                        st.session_state.decrypted_message = cleartext.replace("🔓 Success: ", "")
                        st.session_state.execution_status = {
                            "type": "SUCCESS",
                            "msg": "Decryption Completed: Data array verified, unpacked, and restored successfully."
                        }
                        # --- REQUIREMENT INJECTION: LOG EXTRACTED ENCRYPTED PAYLOAD ---
                        log_terminal("SUCCESS", f"AFTER SUCCESSFUL DECRYPTION IN DECRYPT MODE [EXTRACTED ENCRYPTED PAYLOAD] : {hex_extracted}", "INFO")
                        log_terminal("SUCCESS", "Integrity confirmed. Data extracted flawlessly.", "SUCCESS")
                    
                st.rerun()
                
            except Exception as e:
                st.error(f"System Exception: {str(e)}")
                log_terminal("ERROR", f"Core decryption layer execution break: {str(e)}", "ERROR")


st.markdown("<h1 style='text-align: center; color: #8338EC; margin-bottom: 0px;'>🔮 Embedding Encrypted Playload in Images via Steganography</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A294C2; font-size:14px;'>Premium cryptographically isolated frontend architecture wrapper</p>", unsafe_allow_html=True)
st.write("")

# 1. NATIVE BUTTON-TYPE SEGMENTED CONTROL COMPONENT
current_mode = st.segmented_control(
    "MODE SELECTOR",
    options=["🔒 ENCRYPTION (ENCODE MODE)", "🔓 DECRYPTION (DECODE MODE)"],
    default="🔒 ENCRYPTION (ENCODE MODE)",
    selection_mode="single",
    required=True,
    label_visibility="collapsed",
    on_change=clear_all_buffers,
    key="global_mode_toggle_switch"
)

st.write("---")

# 2. STATUS CONDITIONAL RESPONSE MARGINS
if st.session_state.execution_status is not None:
    status_card = st.session_state.execution_status
    if status_card["type"] == "SUCCESS":
        st.success(status_card["msg"])
    elif status_card["type"] == "ERROR":
        st.error(status_card["msg"])

# 3. CONTAINER IMAGE FILE UPLOADER ENGINE
uploaded_file = st.file_uploader(
    "Upload Cover Target Asset", 
    type=["png", "jpg", "jpeg", "bmp"],
    key=f"file_uploader_seed_{st.session_state.uploader_id}",
    label_visibility="visible"
)

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    raw_img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    
    if raw_img is None:
        st.error("Invalid image asset data buffer detected.")
        st.stop()
        
    if len(raw_img.shape) == 3 and raw_img.shape[2] == 4:
        log_terminal("SYSTEM", "Alpha transparency channel detected. Normalizing matrix to strict BGR-24...")
        cv2_img_bgr = cv2.cvtColor(raw_img, cv2.COLOR_BGRA2BGR)
    else:
        cv2_img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    uploaded_file.seek(0)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("<h3 style='color: #9D4EDD;'>🖼️ Source Image View</h3>", unsafe_allow_html=True)
        display_rgb = cv2.cvtColor(cv2_img_bgr, cv2.COLOR_BGR2RGB)
        st.image(display_rgb, caption=f"Active System Resource Buffer: {uploaded_file.name}", use_container_width=True)
        
    with col2:
        if "ENCRYPTION" in current_mode:
            st.markdown("<h3 style='color: #9D4EDD;'>📝 Input Secret Message </h3>", unsafe_allow_html=True)
            secret_message = st.text_area(
                "Secret Input Text Area",
                placeholder="Enter your confidential alphanumeric string payload data here...",
                height=260,
                label_visibility="collapsed",
                key="secret_text_input"
            )
            st.write("")
            if st.button("🔒 Confirm Payload & Encrypt"):
                if not secret_message:
                    st.session_state.execution_status = {
                        "type": "ERROR", 
                        "msg": "Failed Operation: Input secret message buffer cannot be blank during processing requests."
                    }
                    log_terminal("ERROR", "Operation aborted: Text payload workspace container is empty.", "ERROR")
                    st.rerun()
                else:
                    show_encryption_modal(secret_message, cv2_img_bgr)
        else:
            st.markdown("<h3 style='color: #9D4EDD;'>📝 Decrypted Plaintext Display</h3>", unsafe_allow_html=True)
            
            display_text = st.session_state.decrypted_message if st.session_state.decrypted_message else "[Locked] Ready for extraction processing execution rules..."
            st.text_area(
                "Decrypted Output Text Area",
                value=display_text,
                disabled=True,
                height=260,
                label_visibility="collapsed"
            )
            st.write("")
            if st.button("🔓 Open Decryption Control Panel Overlay"):
                show_decryption_modal(cv2_img_bgr)
else:
    st.info("📥 To unlock the operational workspace window and message payload containers, please load a valid file image container asset above.")

# 4. DOWNLOAD ACCELERATOR INTERFACE ELEMENT
if "ENCRYPTION" in current_mode and st.session_state.get("injection_ready", False):
    st.write("---")
    st.download_button(
        label="💾 Download Compiled Result(.PNG)",
        data=st.session_state.file_payload,
        file_name="stego_output_compiled.png",
        mime="image/png",
        use_container_width=True
    )

# 5. CORE CONSOLE TERMINAL MONITOR ENGINE LOG CHANNELS
st.write("---")
st.markdown("<h4 style='color: #7B2CBF; font-size: 14px;'>📟 Engine Real-Time Console Output Log Channel</h4>", unsafe_allow_html=True)
terminal_html = "<div class='terminal-box'>" + "<br>".join(st.session_state.terminal_logs) + "</div>"
st.markdown(terminal_html, unsafe_allow_html=True)