import base64
import os

import joblib
import pandas as pd
import streamlit as st

# ------------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Heart Disease Prediction",
    page_icon="❤️",
    layout="wide",
)


# ------------------------------------------------------------------
# Background heart image (heart_bg.png app.py ke saath same folder me rakho)
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def clean(html):
    """Indentation hatata hai taaki Markdown HTML ko code block na samjhe."""
    return " ".join(line.strip() for line in html.splitlines() if line.strip())


def img_to_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


heart_b64 = img_to_base64(os.path.join(BASE_DIR, "heart_bg.png"))
heart_layer = (
    f'url("data:image/png;base64,{heart_b64}") right top / auto 100% no-repeat fixed,'
    if heart_b64
    else ""
)

# ------------------------------------------------------------------
# Custom CSS - dark dashboard look
# ------------------------------------------------------------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Inter', sans-serif;
    color: #E8EEF9;
}}

/* ---------- Background ---------- */
.stApp {{
    background:
        {heart_layer}
        radial-gradient(circle at 8% 90%, rgba(255, 46, 99, 0.10), transparent 35%),
        radial-gradient(circle at 60% 0%, rgba(30, 80, 160, 0.18), transparent 45%),
        #050B18;
    background-attachment: fixed;
}}

header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer {{ visibility: hidden; }}

/* Content ko left ~76% me rakho taaki heart image right side me dikhe */
.block-container {{
    max-width: 76% !important;
    margin-left: 3.5% !important;
    margin-right: auto !important;
    padding-top: 2.2rem !important;
}}

/* ---------- Header ---------- */
.hero {{
    display: flex;
    align-items: center;
    gap: 22px;
    margin-bottom: 6px;
}}
.hero h1 {{
    font-size: 3.1rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0;
    padding: 0;
    line-height: 1.1;
    letter-spacing: -0.5px;
}}
.hero h1 span {{ color: #FF5C8A; }}
.hero-sub {{
    color: #9FB3D1;
    font-size: 1.08rem;
    margin: 4px 0 26px 106px;
}}

/* ---------- Form card ---------- */
div[data-testid="stForm"] {{
    background: rgba(9, 20, 42, 0.78);
    border: 1px solid #1B3358;
    border-radius: 16px;
    padding: 26px 28px 22px 28px;
    box-shadow: 0 0 0 1px rgba(40, 90, 170, 0.12), 0 12px 40px rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(6px);
}}
div[data-testid="stForm"] h3 {{
    color: #FFFFFF;
    font-weight: 700;
    font-size: 1.25rem;
}}

/* Labels */
label, label p, div[data-testid="stWidgetLabel"] p {{
    color: #B9C8E3 !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
}}

/* Select / number inputs */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] {{
    background-color: #0B1A35 !important;
    border: 1px solid #1F3A66 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    overflow: hidden;
}}
div[data-baseweb="base-input"] {{
    background-color: transparent !important;
    border: none !important;
}}
div[data-baseweb="select"] span,
div[data-baseweb="input"] input {{
    background-color: transparent !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}
div[data-baseweb="select"] svg {{ fill: #CFE0FF !important; }}
div[data-testid="stNumberInput"] button {{
    background-color: #0B1A35 !important;
    color: #CFE0FF !important;
    border: none !important;
}}
div[data-testid="stNumberInput"] button svg {{ fill: #CFE0FF !important; }}

/* Dropdown menu */
ul[role="listbox"], div[data-baseweb="popover"] > div {{
    background-color: #0B1A35 !important;
    color: #FFFFFF !important;
}}

/* Sliders */
div[data-testid="stSlider"] div[role="slider"] {{
    background-color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 0 8px rgba(255, 46, 99, 0.7);
}}
div[data-testid="stSliderThumbValue"] {{ color: #FFFFFF !important; }}
div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"] {{
    color: #9FB3D1 !important;
    background: transparent !important;
    font-family: 'Inter', sans-serif !important;
}}

/* Run Prediction button */
div[data-testid="stFormSubmitButton"] > button {{
    background: linear-gradient(90deg, #FF2E63 0%, #E8164D 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    height: 3.1rem;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    box-shadow: 0 6px 22px rgba(255, 46, 99, 0.35);
    transition: all 0.2s ease;
}}
div[data-testid="stFormSubmitButton"] > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 8px 28px rgba(255, 46, 99, 0.55);
}}
div[data-testid="stFormSubmitButton"] > button p {{ color: #FFFFFF !important; font-weight: 700; }}

/* ---------- Results card ---------- */
.results-card {{
    margin-top: 22px;
    background: rgba(9, 20, 42, 0.78);
    border: 1px solid #1B3358;
    border-radius: 16px;
    padding: 22px 28px 18px 28px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(6px);
}}
.results-title {{
    color: #FFFFFF;
    font-weight: 700;
    font-size: 1.2rem;
    margin-bottom: 16px;
}}
.results-grid {{
    display: grid;
    grid-template-columns: 1.1fr 1fr;
    gap: 20px;
}}
.res-box {{
    border-radius: 12px;
    padding: 18px 22px;
    display: flex;
    align-items: center;
    gap: 18px;
}}
.res-low  {{ background: linear-gradient(90deg, rgba(14,70,60,.55), rgba(8,30,35,.6)); border: 1px solid #14604F; }}
.res-high {{ background: linear-gradient(90deg, rgba(110,18,40,.55), rgba(40,10,20,.6)); border: 1px solid #8A1F3C; }}
.res-icon {{
    width: 58px; height: 58px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.9rem; color: #fff; font-weight: 800; flex-shrink: 0;
}}
.icon-low  {{ background: #1FD286; }}
.icon-high {{ background: #FF3B63; }}
.res-text-low  {{ color: #2EE6A0; font-size: 1.45rem; font-weight: 700; }}
.res-text-high {{ color: #FF6B8A; font-size: 1.45rem; font-weight: 700; }}

.prob-box {{
    background: rgba(10, 25, 50, 0.7);
    border: 1px solid #1F3A66;
    border-radius: 12px;
    padding: 16px 22px;
}}
.prob-label {{ color: #B9C8E3; font-size: 0.95rem; }}
.prob-value {{ color: #FFFFFF; font-size: 2rem; font-weight: 700; margin: 2px 0 10px 0; }}
.prob-track {{ background: #14284A; border-radius: 20px; height: 10px; overflow: hidden; }}
.prob-fill-low  {{ height: 100%; border-radius: 20px; background: linear-gradient(90deg, #1FD286, #2EE6A0); }}
.prob-fill-high {{ height: 100%; border-radius: 20px; background: linear-gradient(90deg, #FF2E63, #FF6B8A); }}

.disclaimer {{
    color: #8FA3C4;
    font-size: 0.82rem;
    margin-top: 16px;
}}

/* Error box */
div[data-testid="stAlert"] {{ border-radius: 12px; }}
</style>
""",
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Load model artifacts
# ------------------------------------------------------------------
@st.cache_resource
def load_artifacts():
    try:
        model = joblib.load("ht.pkl")
        scaler = joblib.load("scaler.pkl")
        expected_columns = list(joblib.load("heart_columns.pkl"))
        return model, scaler, expected_columns, None
    except Exception as e:
        return None, None, None, str(e)


model, scaler, expected_columns, error_message = load_artifacts()

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
HEART_ICON = """
<svg width="84" height="84" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="hg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#FF5C8A"/>
      <stop offset="1" stop-color="#E8164D"/>
    </linearGradient>
  </defs>
  <path d="M50 90 C10 58 4 32 24 20 C36 13 46 19 50 28 C54 19 64 13 76 20 C96 32 90 58 50 90Z"
        fill="url(#hg)"/>
  <polyline points="8,50 30,50 38,36 48,66 58,44 64,50 92,50"
            fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

st.markdown(
    clean(f"""
    <div class="hero">
        {HEART_ICON}
        <h1>Heart <span>Disease</span> Risk Prediction</h1>
    </div>
    <div class="hero-sub">Enter the patient's clinical details below to evaluate the likelihood of heart disease.</div>
    """),
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Main app
# ------------------------------------------------------------------
if error_message:
    st.error(
        f"⚠️ Error loading model files: `{error_message}`. "
        "Please ensure `ht.pkl`, `scaler.pkl`, and `heart_columns.pkl` are in your app directory."
    )
else:
    with st.form("prediction_form"):
        st.subheader("🩺 Patient Clinical Parameters")

        col1, col2, col3 = st.columns(3)

        with col1:
            age = st.slider("👤 Age", 18, 100, 50)
            sex = st.selectbox("⚧ Sex", ["male", "female"])
            chest_pain = st.selectbox("🫀 Chest Pain Type", ["ATA", "NAP", "TA", "ASY"])
            resting_bp = st.number_input(
                "🌡️ Resting Blood Pressure (mm Hg)", min_value=50, max_value=250, value=120
            )

        with col2:
            cholesterol = st.number_input(
                "💧 Cholesterol (mg/dL)", min_value=0, max_value=1000, value=200
            )
            fasting_bs = st.selectbox(
                "🩸 Fasting Blood Sugar > 120 mg/dL",
                [0, 1],
                format_func=lambda x: "Yes (> 120 mg/dL)" if x == 1 else "No (≤ 120 mg/dL)",
            )
            resting_ecg = st.selectbox("📈 Resting ECG", ["Normal", "ST", "LVH"])
            max_hr = st.slider("❤️ Maximum Heart Rate", 60, 220, 150)

        with col3:
            exercise_angina = st.selectbox(
                "⚡ Exercise-Induced Angina",
                ["N", "Y"],
                format_func=lambda x: "Yes" if x == "Y" else "No",
            )
            oldpeak = st.number_input(
                "📉 Oldpeak (ST Depression)", min_value=-3.0, max_value=10.0, value=1.0, step=0.1
            )
            st_slope = st.selectbox("📈 ST Slope", ["up", "flat", "down"])

        st.markdown("")
        submit_button = st.form_submit_button(
            "▶  Run Prediction", type="primary", use_container_width=True
        )

    if submit_button:
        input_data = pd.DataFrame(
            [
                {
                    "Age": age,
                    "Sex": sex,
                    "ChestPainType": chest_pain,
                    "RestingBP": resting_bp,
                    "Cholesterol": cholesterol,
                    "FastingBS": fasting_bs,
                    "RestingECG": resting_ecg,
                    "MaxHR": max_hr,
                    "ExerciseAngina": exercise_angina,
                    "Oldpeak": oldpeak,
                    "ST_Slope": st_slope,
                }
            ]
        )

        input_encoded = pd.get_dummies(input_data, drop_first=True)
        input_encoded = input_encoded.reindex(columns=expected_columns, fill_value=0)
        input_scaled = scaler.transform(input_encoded)

        prediction = model.predict(input_scaled)[0]

        has_proba = hasattr(model, "predict_proba")
        risk_probability = None
        if has_proba:
            proba = model.predict_proba(input_scaled)[0]
            risk_probability = proba[1] * 100 if len(proba) > 1 else proba[0] * 100

        is_high = prediction == 1
        box_cls = "res-high" if is_high else "res-low"
        icon_cls = "icon-high" if is_high else "icon-low"
        icon_sym = "!" if is_high else "✓"
        text_cls = "res-text-high" if is_high else "res-text-low"
        text = "High Risk of Heart Disease" if is_high else "Low Risk of Heart Disease"
        fill_cls = "prob-fill-high" if is_high else "prob-fill-low"

        prob_html = ""
        if risk_probability is not None:
            prob_html = f"""
            <div class="prob-box">
                <div class="prob-label">🛡️ Estimated Risk Probability</div>
                <div class="prob-value">{risk_probability:.1f}%</div>
                <div class="prob-track">
                    <div class="{fill_cls}" style="width:{min(max(risk_probability, 0), 100):.1f}%"></div>
                </div>
            </div>
            """

        st.markdown(
            clean(f"""
            <div class="results-card">
                <div class="results-title">📊 Prediction Results</div>
                <div class="results-grid">
                    <div class="res-box {box_cls}">
                        <div class="res-icon {icon_cls}">{icon_sym}</div>
                        <div class="{text_cls}">{text}</div>
                    </div>
                    {prob_html}
                </div>
                <div class="disclaimer">
                    ⓘ Disclaimer: This is an educational machine-learning prediction tool
                    and should not be used as a substitute for professional medical diagnosis or advice.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
