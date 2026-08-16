import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# ============================================================
# DRISHTI HEALTH
# AI-Powered Personalized Food Label & Allergen Awareness
# ============================================================

st.set_page_config(
    page_title="Drishti Health",
    page_icon="👁️",
    layout="centered"
)

# ============================================================
# UI
# ============================================================

st.markdown(
    "<h1 style='text-align: center;'>👁️ DRISHTI HEALTH</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; color: #888888;'>"
    "AI-Powered Personalized Food Label & Allergen Awareness"
    "</p>",
    unsafe_allow_html=True
)

# ============================================================
# GEMINI CLIENT
# ============================================================

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception:
    client = None
    st.error(
        "Gemini API is not configured. "
        "Add GEMINI_API_KEY to Streamlit secrets."
    )

# ============================================================
# SESSION STATE
# ============================================================

if "profile_created" not in st.session_state:
    st.session_state.profile_created = False

if "user_diseases" not in st.session_state:
    st.session_state.user_diseases = ""

if "user_allergies" not in st.session_state:
    st.session_state.user_allergies = ""

if "selected_languages" not in st.session_state:
    st.session_state.selected_languages = [
        "English — English",
        "Hindi — हिन्दी"
    ]

if "scan_number" not in st.session_state:
    st.session_state.scan_number = 0


# ============================================================
# AVAILABLE LANGUAGES
# ============================================================

INDIAN_LANGUAGES = [
    "English — English",
    "Hindi — हिन्दी",
    "Bengali — বাংলা",
    "Marathi — मराठी",
    "Tamil — தமிழ்",
    "Telugu — తెలుగు",
    "Gujarati — ગુજરાતી",
    "Kannada — ಕನ್ನಡ",
    "Malayalam — മലയാളം",
    "Punjabi — ਪੰਜਾਬੀ",
    "Urdu — اردو",
    "Odia — ଓଡ଼ିଆ",
    "Nepali — Nepali"
]


# ============================================================
# STEP 1 — CREATE PROFILE
# ============================================================

if not st.session_state.profile_created:

    st.markdown("## 👤 Create Your Health Profile")

    st.write(
        "This profile helps Drishti identify information on food "
        "labels that may be relevant to you."
    )

    # --------------------------------------------------------
    # LANGUAGES (Checkboxes with max 2 limit)
    # --------------------------------------------------------

    st.markdown("### 🌐 Choose your report languages")
    st.caption("Select up to 2 languages using the checkboxes below:")

    with st.expander("Select Report Languages (Max 2)", expanded=True):
        chosen_langs = []
        for lang in INDIAN_LANGUAGES:
            default_checked = lang in st.session_state.selected_languages
            is_checked = st.checkbox(lang, value=default_checked, key=f"lang_chk_{lang}")
            if is_checked:
                chosen_langs.append(lang)

        if len(chosen_langs) > 2:
            st.error("⚠️ Maximum 2 languages allowed. Please uncheck one to proceed.")

    # --------------------------------------------------------
    # HEALTH CONDITIONS
    # --------------------------------------------------------

    st.markdown("### 🩺 Health Conditions / Dietary Restrictions")

    common_conditions = st.multiselect(
        "Select any that apply:",
        [
            "Diabetes",
            "Hypertension",
            "Heart-related dietary restrictions",
            "Kidney-related dietary restrictions",
            "Celiac disease",
            "Other"
        ]
    )

    other_condition = ""

    if "Other" in common_conditions:
        other_condition = st.text_input(
            "Enter another condition or restriction:"
        )

    # --------------------------------------------------------
    # ALLERGIES
    # --------------------------------------------------------

    st.markdown("### ⚠️ Allergies / Intolerances")

    common_allergies = st.multiselect(
        "Select any that apply:",
        [
            "Peanut",
            "Milk / Dairy",
            "Soy",
            "Wheat",
            "Egg",
            "Tree nuts",
            "Fish",
            "Shellfish",
            "Sesame",
            "Other"
        ]
    )

    other_allergy = ""

    if "Other" in common_allergies:
        other_allergy = st.text_input(
            "Enter another allergy or intolerance:"
        )

    # --------------------------------------------------------
    # CREATE PROFILE
    # --------------------------------------------------------

    if st.button("Create Profile", type="primary"):

        if not chosen_langs:
            st.warning("Please select at least one report language.")

        elif len(chosen_langs) > 2:
            st.error("Please limit your selection to a maximum of 2 languages.")

        elif not common_conditions and not common_allergies:
            st.warning(
                "Please enter at least one health condition, "
                "dietary restriction, allergy, or intolerance."
            )

        else:

            # Store profile in current Streamlit session

            conditions = [
                x for x in common_conditions
                if x != "Other"
            ]

            if other_condition.strip():
                conditions.append(other_condition.strip())

            allergies = [
                x for x in common_allergies
                if x != "Other"
            ]

            if other_allergy.strip():
                allergies.append(other_allergy.strip())

            st.session_state.user_diseases = ", ".join(conditions)
            st.session_state.user_allergies = ", ".join(allergies)

            st.session_state.selected_languages = chosen_langs

            st.session_state.profile_created = True

            st.rerun()


# ============================================================
# PROFILE CREATED
# ============================================================

else:

    st.markdown("## 👤 Your Active Profile")

    st.success("✅ Profile active")

    st.markdown(
        f"""
        **Health conditions / restrictions:**  
        {st.session_state.user_diseases or "None specified"}

        **Allergies / intolerances:**  
        {st.session_state.user_allergies or "None specified"}

        **Report languages:**  
        {", ".join(st.session_state.selected_languages)}

        **Products scanned:**  
        {st.session_state.scan_number}
        """
    )

    if st.button("Edit / Reset Profile"):

        st.session_state.profile_created = False
        st.session_state.user_diseases = ""
        st.session_state.user_allergies = ""
        st.session_state.selected_languages = [
            "English — English",
            "Hindi — हिन्दी"
        ]
        st.session_state.scan_number = 0

        st.rerun()


# ============================================================
# CONTINUOUS PRODUCT SCANNING
# ============================================================

if st.session_state.profile_created:

    st.markdown("---")

    st.markdown("## 📸 Scan a Food Label")

    st.caption(
        "Your profile remains active. Scan Product A, Product B, "
        "Product C, and more without entering your information again."
    )

    # --------------------------------------------------------
    # DUAL INPUT MODES (Webcam stream vs Native Camera / Gallery / Drive)
    # --------------------------------------------------------

    tab1, tab2 = st.tabs(["📁 Upload / Drive / Native Cam", "📷 Live Stream Camera"])

    uploaded_file = None

    with tab1:
        uploaded_file = st.file_uploader(
            f"Select image for Product {st.session_state.scan_number + 1}",
            type=["jpg", "jpeg", "png", "webp"],
            help="Tap 'Browse files' on mobile to launch your Native Camera App or upload from Gallery/Google Drive."
        )

    with tab2:
        cam_file = st.camera_input(
            f"Scan Product {st.session_state.scan_number + 1}"
        )
        if cam_file is not None:
            uploaded_file = cam_file

    if uploaded_file is not None:

        if client is None:
            st.error("Gemini is not configured.")
            st.stop()

        image = Image.open(uploaded_file)

        st.image(
            image,
            caption="Captured food label",
            use_container_width=True
        )

        with st.spinner(
            "Reading ingredients, additives and nutrition information..."
        ):

            # ====================================================
            # ADVANCED AI PROMPT
            # ====================================================

            prompt = f"""
You are Drishti Health, an AI-powered food-label
analysis and consumer-awareness assistant.

Your task is to analyze the visible food packaging
and identify information that MAY be relevant to
the user's stated profile.

========================================================
USER PROFILE
========================================================

Health conditions / dietary restrictions:
{st.session_state.user_diseases or "None specified"}

Allergies / intolerances:
{st.session_state.user_allergies or "None specified"}

The user selected these report languages:
{", ".join(st.session_state.selected_languages)}

========================================================
IMPORTANT SAFETY RULES
========================================================

You are NOT a doctor.

You are NOT a diagnostic system.

Do NOT provide a medical diagnosis.

Do NOT declare that a product is medically
"safe", "unsafe", "approved", or "cleared".

Do NOT tell the user that they definitely can
or cannot consume the product.

Do NOT assume that an ingredient is universally
"bad".

Instead, identify information that MAY be relevant
to the user's stated profile.

If information cannot be reliably read from the
photograph, explicitly say so.

Never invent an ingredient, chemical, nutrition
value, additive number, or health effect.

========================================================
ADVANCED INGREDIENT & ADDITIVE IDENTIFICATION
========================================================

Food labels may contain ordinary ingredient names,
chemical names, additive codes, INS numbers,
E-numbers, preservative codes, colour codes,
emulsifiers, stabilizers, acidity regulators,
antioxidants, flavour enhancers, sweeteners,
thickeners and other technical terms.

For example, a label might contain something such as:

INS 163
INS 330
INS 621
INS 211
INS 322
INS 415

If an additive code such as an INS number or
E-number is visible:

1. Identify the code exactly as written.

2. Determine the commonly recognized name of the
   additive if you can do so reliably.

3. Identify its general technological function,
   such as:
   - colour
   - preservative
   - acidity regulator
   - antioxidant
   - emulsifier
   - stabilizer
   - thickener
   - flavour enhancer
   - sweetener

4. Explain what the additive is generally used for
   in food.

5. If relevant information is known, explain whether
   it may be relevant to the user's stated allergies,
   intolerances, dietary restrictions, or conditions.

6. Clearly distinguish established information
   from uncertainty.

7. NEVER invent a chemical structure or chemical
   composition merely because the code looks familiar.

8. Do not assign an arbitrary numerical "risk score"
   such as 7/10 unless a verified scientific or
   regulatory basis is actually available.

9. Risk should NOT be treated as universal.
   Explain that relevance may depend on the individual,
   amount consumed, sensitivity, dietary context,
   and other factors.

10. If you cannot confidently identify an INS/E-number,
    report:

    "Additive code detected, but reliable identification
    could not be established from the available
    information."

========================================================
CHEMICAL / COMPOUND UNDERSTANDING
========================================================

When a recognizable additive or compound is detected,
attempt to provide:

- Label name
- INS/E-number, if present
- Common name
- General chemical/additive category
- Technological function
- Why it is used in food
- Whether it appears relevant to the user's profile
- Confidence level

Do NOT turn this into a medical diagnosis.

If the label contains an ingredient with a complex
technical name, explain it in simple consumer language.

For example:

Technical term
→ What it generally is
→ Why it is used
→ Whether it appears relevant to this particular
  user's profile

========================================================
LABEL EXTRACTION
========================================================

Read the following where visible:

- Product name
- Ingredient list
- INS/E-numbers
- Additives
- Declared allergens
- Nutrition facts
- Calories / energy
- Sugar
- Sodium / salt
- Total fat
- Saturated fat
- Protein
- Fibre
- Serving size
- Any relevant warnings

Do NOT invent information that is not visible.

========================================================
PROFILE COMPARISON
========================================================

Compare detected information ONLY with the user's
self-entered profile.

For every possible match, explain:

1. What was detected?
2. Why might it be relevant?
3. How confident are you?

Use:

High
Medium
Low

confidence.

If there is no clear match, state:

"No clear profile-relevant match was detected from
the visible label."

========================================================
OUTPUT FORMAT
========================================================

Produce the report in EVERY language selected by
the user:

{", ".join(st.session_state.selected_languages)}

LANGUAGE SCRIPT REQUIREMENT:

When generating a report in a selected language,
use that language's native writing system/script.

Use the following scripts:

English → English / Latin script
Hindi → Devanagari script (हिन्दी)
Bengali → Bengali script (বাংলা)
Marathi → Devanagari script (मराठी)
Tamil → Tamil script (தமிழ்)
Telugu → Telugu script (తెలుగు)
Gujarati → Gujarati script (Gujarati)
Kannada → Kannada script (ಕನ್ನಡ)
Malayalam → Malayalam script (മലയാളം)
Punjabi → Gurmukhi script (ਪੰਜਾਬੀ)
Urdu → Urdu script (اردو)
Odia → Odia script (ଓଡ଼ିଆ)
Nepali → Devanagari script (नेपाली)

Do NOT transliterate the selected language into
English/Roman characters unless the user explicitly
requests Romanized text.

Do NOT produce Hinglish, Tanglish, or other
Romanized forms when the native-script language
has been selected.

Every language must contain the SAME underlying
information.

Do not add medical claims in one language that are
absent from another.

For each language use this structure:

### 🔍 DETECTED LABEL INFORMATION

### 🧪 ADDITIVES / COMPLEX INGREDIENTS

For each identified additive:

- Label code/name
- Common name
- Function
- Relevance
- Confidence

### ⚠️ PROFILE-RELEVANT FLAGS

### 🧾 NUTRITION SUMMARY

### 💡 SIMPLE EXPLANATION

### ❗ IMPORTANT LIMITATION

Explain that the analysis is based only on the
visible label and the user's self-entered profile.

It is an educational consumer-awareness screening
tool and does not replace professional medical advice.

========================================================
FINAL REQUIREMENT
========================================================

Be precise.

Do not manufacture missing information.

Do not confuse an additive's technological function
with its medical effect.

Do not provide a universal "healthy/unhealthy"
judgment.

Focus on personalized label understanding and
consumer awareness.
"""

            try:
                # Dynamic MIME Type Detection
                mime_type = getattr(uploaded_file, "type", "image/jpeg")
                if not mime_type or mime_type == "application/octet-stream":
                    mime_type = "image/jpeg"

                image_bytes = uploaded_file.getvalue()

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=image_bytes,
                            mime_type=mime_type
                        ),
                        prompt
                    ]
                )

                st.session_state.scan_number += 1

                st.markdown("---")

                st.markdown(
                    "## 📊 Drishti Personal Food Report"
                )

                st.write(response.text)

                st.info(
                    "Drishti provides educational food-label "
                    "analysis based on the visible label and "
                    "the user's self-entered profile. It does "
                    "not replace professional medical advice."
                )

            except Exception as e:

                st.error(
                    "The label could not be analyzed successfully."
                )

                st.caption(
                    "Please try capturing the label again with better lighting "
                    "and a clearer view of the ingredients."
                )

    # ========================================================
    # CONTINUOUS SCANNING
    # ========================================================

    if st.session_state.scan_number > 0:

        st.markdown("---")

        st.markdown(
            f"### 🔄 Ready for Product "
            f"{st.session_state.scan_number + 1}"
        )

        st.write(
            "Your profile is still active. "
            "You do not need to enter it again."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Drishti Health — AI-powered food-label accessibility "
    "and consumer awareness prototype."
)
