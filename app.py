import streamlit as st
import qrcode
from qrcode.image.styles.moduledrawers.pil import (
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
)
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Stylish QR Code Generator", page_icon="🎨", layout="wide")

st.title("🎨 Stylish QR Code Generator")
st.caption("Generate custom QR codes with **gradients**, **logos**, and **background images** — live preview enabled!")

# Sidebar controls
st.sidebar.header("⚙️ QR Code Settings")
data = st.sidebar.text_input("🔗 Enter text or URL", "https://example.com")

qr_size = st.sidebar.slider("📏 QR Size (pixels)", 200, 1000, 400, 50)
error_correction = st.sidebar.selectbox("🛡️ Error Correction", {
    "Low (L)": qrcode.constants.ERROR_CORRECT_L,
    "Medium (M)": qrcode.constants.ERROR_CORRECT_M,
    "Quartile (Q)": qrcode.constants.ERROR_CORRECT_Q,
    "High (H)": qrcode.constants.ERROR_CORRECT_H
}.keys())
error_map = {
    "Low (L)": qrcode.constants.ERROR_CORRECT_L,
    "Medium (M)": qrcode.constants.ERROR_CORRECT_M,
    "Quartile (Q)": qrcode.constants.ERROR_CORRECT_Q,
    "High (H)": qrcode.constants.ERROR_CORRECT_H
}
ec_level = error_map[error_correction]

# Color / background
fill_mode = st.sidebar.radio("🎨 QR Fill Mode", ["Solid Color", "Gradient"])
fg_color = st.sidebar.color_picker("Primary QR Color", "#000000")
if fill_mode == "Gradient":
    gradient_color = st.sidebar.color_picker("Secondary QR Color", "#0078D7")

bg_mode = st.sidebar.radio("🖼️ Background Mode", ["Color", "Image"])
bg_color = "#ffffff"
bg_image_file = None
if bg_mode == "Color":
    bg_color = st.sidebar.color_picker("Background Color", "#ffffff")
else:
    bg_image_file = st.sidebar.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])

# Shape options
shape_choice = st.sidebar.selectbox("🔳 QR Shape Style", [
    "Square", "Gapped Square", "Circle", "Rounded"
])
shape_map = {
    "Square": SquareModuleDrawer(),
    "Gapped Square": GappedSquareModuleDrawer(),
    "Circle": CircleModuleDrawer(),
    "Rounded": RoundedModuleDrawer()
}
module_shape = shape_map[shape_choice]

# Logo options
logo_file = st.sidebar.file_uploader("📌 Upload Logo (optional)", type=["png", "jpg", "jpeg"])
logo_size_pct = st.sidebar.slider("Logo Size (% of QR width)", 10, 30, 20)

# --- Generate QR automatically ---
if data:
    # Step 1: make base QR in black/white
    qr = qrcode.QRCode(
        version=1,
        error_correction=ec_level,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")
    qr_img = qr_img.resize((qr_size, qr_size))

    # Step 2: make background (solid or image)
    if bg_mode == "Color":
        base = Image.new("RGBA", (qr_size, qr_size), bg_color)
    else:
        if bg_image_file:
            base = Image.open(bg_image_file).convert("RGBA").resize((qr_size, qr_size))
        else:
            base = Image.new("RGBA", (qr_size, qr_size), "#ffffff")

    # Step 3: make fill (solid or gradient)
    if fill_mode == "Solid Color":
        fill = Image.new("RGBA", (qr_size, qr_size), fg_color)
    else:  # Gradient
        fill = Image.new("RGBA", (qr_size, qr_size))
        draw = ImageDraw.Draw(fill)
        for y in range(qr_size):
            r = int(int(fg_color[1:3], 16) + (int(gradient_color[1:3], 16) - int(fg_color[1:3], 16)) * y / qr_size)
            g = int(int(fg_color[3:5], 16) + (int(gradient_color[3:5], 16) - int(fg_color[3:5], 16)) * y / qr_size)
            b = int(int(fg_color[5:7], 16) + (int(gradient_color[5:7], 16) - int(fg_color[5:7], 16)) * y / qr_size)
            draw.line([(0, y), (qr_size, y)], fill=(r, g, b, 255))

    # Step 4: apply mask (QR black = visible)
    qr_mask = qr_img.point(lambda p: 255 - p)  # invert: black->white mask
    colored_qr = Image.composite(fill, base, qr_mask)

    # Step 5: add logo if present
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA")
        logo_size = int(qr_size * (logo_size_pct / 100))
        logo = logo.resize((logo_size, logo_size))
        pos = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)
        colored_qr.paste(logo, pos, logo)

    # Show result
    st.image(colored_qr, caption="✨ Live Preview of Your QR Code", use_container_width=False)

    # Download button
    buf = io.BytesIO()
    colored_qr.save(buf, format="PNG")
    st.sidebar.download_button(
        label="⬇️ Download QR Code",
        data=buf.getvalue(),
        file_name="stylish_qrcode.png",
        mime="image/png"
    )

else:
    st.warning("⚠️ Enter some text or URL in the sidebar to generate your QR code.")
