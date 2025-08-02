import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from PIL import Image
import io

st.set_page_config(page_title="Custom QR Code Generator", page_icon="🎨")

st.title("🎨 Custom QR Code Generator")
st.write("Generate QR codes with **custom colors** and an optional **logo**.")

# Input fields
data = st.text_input("Enter text or URL")
qr_color = st.color_picker("Pick QR Color", "#000000")
bg_color = st.color_picker("Pick Background Color", "#ffffff")
logo_file = st.file_uploader("Upload a logo (optional, PNG recommended)", type=["png", "jpg", "jpeg"])

if st.button("Generate QR Code"):
    if data:
        # Create QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            fill_color=qr_color,
            back_color=bg_color
        ).convert("RGBA")

        # Add logo if uploaded
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            qr_width, qr_height = img.size

            logo_size = qr_width // 4
            logo = logo.resize((logo_size, logo_size))

            pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            img.paste(logo, pos, logo)

        # Show QR Code
        st.image(img, caption="Your Custom QR Code", use_container_width=False)

        # Download button
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button(
            label="⬇️ Download QR Code",
            data=buf.getvalue(),
            file_name="custom_qrcode.png",
            mime="image/png"
        )
    else:
        st.warning("⚠️ Please enter some text or a URL to generate a QR code.")
