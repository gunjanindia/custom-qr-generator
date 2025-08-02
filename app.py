import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
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
st.caption("Generate custom QR codes with gradients, logos, and background images — all live previewed!")

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

# Color options
color_mode = st.sidebar.radio("🎨 QR Fill Mode", ["Solid Color", "Gradient"])
fg_color = st.sidebar.color_picker("Primary QR Color", "#000000")
bg_mode = st.sidebar.radio("🖼️ Background Mode", ["Color", "Image"])
bg_color = "#ffffff"
bg_image_file = None
if bg_mode == "Color":
    bg_color = st.sidebar.color_picker("Background Color", "#ffffff")
else:
    bg_image_file = st.sidebar.file_uploader("Upload Background Image", type=["png", "jpg", "jpeg"])

if color_mode == "Gradient":
    gradient_color = st.sidebar.color_picker("Secondary QR Color", "#0078D7")

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
    qr = qrcode.QRCode(
        version=1,
        error_correction=ec_level,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=module_shape,
        fill_color=fg_color if color_mode == "Solid Color" else "black",
        back_color=bg_color if bg_mode == "Color" else "white"
    ).convert("RGBA")
    img = img.resize((qr_size, qr_size))

    # Apply gradient if chosen
    if color_mode == "Gradient":
        gradient = Image.new("RGBA", img.size, color=0)
        draw = ImageDraw.Draw(gradient)
        for y in range(img.size[1]):
            r = int(int(fg_color[1:3], 16) + (int(gradient_color[1:3], 16) - int(fg_color[1:3], 16)) * y / img.size[1])
            g = int(int(fg_color[3:5], 16) + (int(gradient_color[3:5], 16) - int(fg_color[3:5], 16)) * y / img.size[1])
            b = int(int(fg_color[5:7], 16) + (int(gradient_color[5:7], 16) - int(fg_color[5:7], 16)) * y / img.size[1])
            draw.line([(0, y), (img.size[0], y)], fill=(r, g, b, 255))
        img = Image.alpha_composite(gradient, img)

    # Merge with background image if uploaded
    if bg_mode == "Image" and bg_image_file:
        bg_img = Image.open(bg_image_file).convert("RGBA")
        bg_img = bg_img.resize((qr_size, qr_size))
        combined = Image.alpha_composite(bg_img, img)
        img = combined

    # Add logo if uploaded
    if logo_file:
        logo = Image.open(logo_file).convert("RGBA")
        logo_size = int(qr_size * (logo_size_pct / 100))
        logo = logo.resize((logo_size, logo_size))
        pos = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)
        img.paste(logo, pos, logo)

    # Show QR
    st.image(img, caption="✨ Live Preview of Your QR Code", use_container_width=False)

    # Sidebar download button
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.sidebar.download_button(
        label="⬇️ Download QR Code",
        data=buf.getvalue(),
        file_name="stylish_qrcode.png",
        mime="image/png"
    )
else:
    st.warning("⚠️ Enter some text or URL in the sidebar to generate your QR code.")
