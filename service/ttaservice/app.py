from io import StringIO

import streamlit as st

from tta_generator.narration import get_narration_from_text


st.title("Audiobook Generator")

uploaded_file = st.file_uploader("Choose a text file", type="txt")

if uploaded_file is not None:
    text: str = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    with st.spinner("Generating narration..."):
        narration: bytes = get_narration_from_text(text=text)
        st.audio(narration, format="audio/mp3")
