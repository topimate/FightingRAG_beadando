import base64
from pathlib import Path

import streamlit as st


ASSET_PATH = Path(__file__).resolve().parent / "assets" / "mma_cage_hero.jpg"


def apply_theme() -> None:
    """Apply the existing minimal dark theme and a photo-backed hero card."""
    image_b64 = base64.b64encode(ASSET_PATH.read_bytes()).decode("ascii")

    st.markdown(
        f"""
        <style>
        /* App background: keep the two subtle red corner lights. */
        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(255, 59, 48, 0.12), transparent 20%),
                radial-gradient(circle at top left, rgba(255, 90, 90, 0.10), transparent 22%),
                linear-gradient(180deg, #0B0B0F 0%, #111216 100%);
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        .stMainBlockContainer {{
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        /* Regular cards preserve the minimal graphite design. */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: linear-gradient(155deg, #1C1D22 0%, #131418 100%);
            border: 1px solid #303039;
            border-radius: 22px;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
        }}

        /* One named native Streamlit container gets the photo background. */
        .st-key-fight_hero {{
            background:
                linear-gradient(90deg, rgba(9, 10, 14, 0.80) 0%,
                                      rgba(9, 10, 14, 0.58) 50%,
                                      rgba(9, 10, 14, 0.72) 100%),
                url("data:image/jpeg;base64,{image_b64}") center / cover no-repeat !important;
            border: 1px solid #423036 !important;
            border-radius: 24px !important;
            box-shadow: 0 12px 38px rgba(0, 0, 0, 0.28);
        }}

        /* Native tabs. */
        div[data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background: #111216;
            border: 1px solid #26282E;
            border-radius: 18px;
            padding: 0.35rem;
        }}

        button[role="tab"] {{
            border-radius: 14px;
            padding: 0.6rem 1rem;
            color: #B9BBC3;
        }}

        button[role="tab"][aria-selected="true"] {{
            background: #242025;
            color: #FFFFFF;
            box-shadow: 0 0 18px rgba(255, 59, 48, 0.09);
        }}

        /* Controls. */
        .stButton > button {{
            border-radius: 14px;
            border: 1px solid #303039;
            background: #191A1F;
            color: #F5F5F7;
            font-weight: 600;
        }}

        .stButton > button:hover {{
            border-color: #FF3B30;
            color: #FFFFFF;
        }}

        .stButton > button[kind="primary"] {{
            background: #D93636;
            border-color: #D93636;
            color: #FFFFFF;
        }}

        h1, h2, h3 {{
            letter-spacing: -0.035em;
            font-weight: 650;
        }}

        [data-testid="stMetricValue"] {{
            letter-spacing: -0.045em;
            font-weight: 650;
        }}

        [data-testid="stCaptionContainer"] {{
            color: #A7AAB3;
        }}

        div[data-testid="stChatInput"] textarea,
        .stTextArea textarea,
        .stTextInput input {{
            background: #15161A;
            color: #F5F5F7;
            border-radius: 16px;
        }}

        details {{
            border-radius: 16px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
