import streamlit as st
from func.inference import analyze_image
from func.calorie_map import get_calorie
from PIL import Image
import tempfile
import pandas as pd

# PAGE
st.set_page_config(
    page_title="Food Detector",
    layout="centered"
)

st.title("Food Calorie Detector")
st.markdown(
    "Upload a meal photo and let us estimate the **total calories** based on detected food items."
)

# Sidebar
st.sidebar.header("Detection Settings")
confidence = st.sidebar.slider(
    "Confidence Threshold",
    0.1, 1.0, 0.25,
    help="Lower values detect more objects but may include false positives."
)

# IMAGE UPLOAD
uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)

    # Save to temporary file for model
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        image_path = tmp.name

    # Show uploaded image
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Analyzing food items..."):
        counts, avg_conf, total_calories, _ = analyze_image(image_path, conf=confidence)

    total_items = sum(counts.values())

    # DASHBOARD METRICS
    st.markdown("### Summary")
    col1, col2 = st.columns(2)
    col1.metric("Total Items Detected", total_items)
    col2.metric("Estimated Calories", f"{total_calories} kcal")

    st.caption("Calories are estimated according to the portion sizes detected in the photo, so might not be 100% accurate.")

    # TABLE
    df = pd.DataFrame({
        "Food Item": list(counts.keys()),
        "Quantity": list(counts.values()),
        "Calories per Item": [get_calorie(f) for f in counts.keys()],
        "Avg Confidence": [round(avg_conf[f], 2) for f in counts.keys()]
    })

    df["Total Calories"] = df["Quantity"] * df["Calories per Item"]

    st.markdown("### Nutrition Breakdown")
    st.dataframe(df, use_container_width=True)

    # WARNINGS
    if any(c < 0.6 for c in avg_conf.values()):
        st.warning("Some detections have low confidence. The calorie estimate may be less accurate.")

else:
    st.info("Upload an image to begin calorie estimation.")





