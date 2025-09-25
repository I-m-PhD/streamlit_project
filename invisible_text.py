import streamlit as st


def generate_invisible_text(input_characters, invisible_char):
    """
    Replaces each character in the input string with a chosen invisible character.
    The resulting string will have the same length but be completely invisible.
    """
    return invisible_char * len(input_characters)


st.set_page_config(page_title="Invisible Character Generator", layout="centered")

st.title("Invisible Character Generator")
st.markdown(
    """
    This app replaces each character you type with optional single, non-visible Unicode character.
    """
)

# A dictionary of invisible characters with their names and Unicode codes
invisible_chars = {
    "Hangul Filler (U+3164)": "\u3164",
    "Braille Pattern Blank (U+2800)": "\u2800",
    "Mongolian Vowel Separator (U+180E)": "\u180E",
    "Zero-Width Space (U+200B)": "\u200B",
    "Zero-Width Non-Joiner (U+200C)": "\u200C",
    "Zero-Width Joiner (U+200D)": "\u200D",
}

# A mapping for the visible representation of each invisible character
visible_representations = {
    "\u3164": "⟨HF⟩",
    "\u2800": "⟨BPB⟩",
    "\u180E": "⟨MVS⟩",
    "\u200B": "⟨ZWSP⟩",
    "\u200C": "⟨ZWNJ⟩",
    "\u200D": "⟨ZWJ⟩",
}

# Options for selecting the invisible character
selected_char_name = st.selectbox(
    "Select an invisible character:",
    options=list(invisible_chars.keys())
)

# Get the actual character based on the user's selection
invisible_char_to_use = invisible_chars[selected_char_name]

# Use st.chat_input to get user input
input_text = st.chat_input("Type something to make it invisible...")

# Check if the user has entered some text
if input_text:
    # Generate the invisible text using the selected character
    invisible_text = generate_invisible_text(input_text, invisible_char_to_use)

    # Calculate the number of characters and the byte size
    char_count = len(invisible_text)
    byte_size = len(invisible_text.encode('utf-8'))

    st.subheader("Copy your invisible text below:")

    # Display the generated text in a code block with a copy button
    st.code(invisible_text, language=None)

    # Display the character and byte count
    st.markdown(f"**Characters:** `{char_count}` **Bytes:** `{byte_size}`")

    st.subheader("Visual Representation:")
    # Generate and display the visible representation
    visible_representation = visible_representations[invisible_char_to_use] * len(input_text)


    st.code(visible_representation, language=None)

    st.success(f"Text generated! You can now copy and paste the invisible text created with {selected_char_name}.")
