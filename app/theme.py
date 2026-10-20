
import streamlit as st


def apply_theme():
    """Apply FightRAG's minimal dark visual theme."""

    st.markdown(
        """
        <style>
        /*1. BACKGROUND – Dual red ambient glow */

        .stApp {
            background:
                radial-gradient(
                    circle at top right,
                    rgba(255, 59, 48, 0.12),
                    transparent 20%
                ),
                radial-gradient(
                    circle at top left,
                    rgba(255, 90, 90, 0.10),
                    transparent 22%
                ),
                linear-gradient(
                    180deg,
                    #0B0B0F 0%,
                    #111216 100%
                );
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* 2. LAYOUT – Comfortable reading width */

        .stMainBlockContainer {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* 3. CARDS – Subtle graphite gradient */

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(
                155deg,
                #1C1D22 0%,
                #131418 100%
            );
            border: 1px solid #303039;
            border-radius: 22px;
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
        }

        /* 4. TABS – Subtle red active glow*/

        div[data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: #111216;
            border: 1px solid #26282E;
            border-radius: 18px;
            padding: 0.35rem;
        }

        button[role="tab"] {
            border-radius: 14px;
            padding: 0.6rem 1rem;
            color: #B9BBC3;
        }

        button[role="tab"][aria-selected="true"] {
            background: #242025;
            color: #FFFFFF;
            box-shadow: 0 0 18px rgba(255, 59, 48, 0.09);
        }

        /* 5. BUTTONS – Consistent dark controls*/

        .stButton > button {
            border-radius: 14px;
            border: 1px solid #303039;
            background: #191A1F;
            color: #F5F5F7;
            font-weight: 600;
        }

        .stButton > button:hover {
            border-color: #FF3B30;
            color: #FFFFFF;
        }

        .stButton > button[kind="primary"] {
            background: #D93636;
            border-color: #D93636;
            color: #FFFFFF;
        }

        /* 6. TYPOGRAPHY – Minimal and refined*/

        h1, h2, h3 {
            letter-spacing: -0.035em;
            font-weight: 650;
        }

        [data-testid="stMetricValue"] {
            letter-spacing: -0.045em;
            font-weight: 650;
        }

        [data-testid="stCaptionContainer"] {
            color: #A7AAB3;
        }

        /* 7. INPUTS AND EXPANDERS*/

        div[data-testid="stChatInput"] textarea,
        .stTextArea textarea,
        .stTextInput input {
            background: #15161A;
            color: #F5F5F7;
            border-radius: 16px;
        }

        details {
            border-radius: 16px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
