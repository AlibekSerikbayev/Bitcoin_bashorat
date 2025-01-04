import streamlit as st
import cv2
import face_recognition
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import pandas as pd
import joblib
from captcha.image import ImageCaptcha
import random
import string

# === Yuzni Tanish (Face ID) Qismi === #

# Yuzni tanish uchun bazaviy rasm yuklash
KNOWN_IMAGE_PATH = "known_face.jpg"  # Bu sizning tanib olinadigan yuzingiz
known_image = face_recognition.load_image_file(KNOWN_IMAGE_PATH)
known_face_encoding = face_recognition.face_encodings(known_image)[0]

# Yuzni solishtirish funksiyasi
def compare_faces(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        match = face_recognition.compare_faces([known_face_encoding], face_encoding, tolerance=0.6)
        if match[0]:
            return True
    return False

class FaceDetectionTransformer(VideoTransformerBase):
    def __init__(self):
        self.verified = False

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        if not self.verified:
            if compare_faces(img):
                self.verified = True
                cv2.putText(img, "Verified", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(img, "Unverified", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return img

# === Bitcoin Narxi Bashorati Qismi === #

# Modelni yuklash
model = joblib.load('bitcoin_model5.pkl')

# CAPTCHA yaratish funksiyasi
def generate_captcha():
    image_captcha = ImageCaptcha(width=280, height=90)
    captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    image = image_captcha.generate_image(captcha_text)
    return captcha_text, image

# CAPTCHA tekshirish funksiyasi
def verify_captcha(user_input, actual_captcha):
    return user_input.strip().upper() == actual_captcha

# === Interfeys === #
st.title("Bitcoin Narxi Bashorati va Yuzni Tanish Tizimi")
st.sidebar.title("Bo'limni tanlang:")
section = st.sidebar.radio("Navigatsiya:", ("Face ID Tizimi", "Bitcoin Bashorati"))

if section == "Face ID Tizimi":
    st.header("Yuzni Tanish (Face ID)")
    st.image(KNOWN_IMAGE_PATH, caption="Tanish yuz (bazaviy rasm)")

    webrtc_streamer(
        key="face-id",
        video_transformer_factory=FaceDetectionTransformer,
        media_stream_constraints={"video": True, "audio": False},
    )

    if st.button("Tekshiruv natijasi"):
        face_detected = FaceDetectionTransformer().verified
        if face_detected:
            st.success("Yuz tanildi! Kirish muvaffaqiyatli.")
        else:
            st.error("Yuz topilmadi yoki mos kelmadi.")

elif section == "Bitcoin Bashorati":
    st.header("Bitcoin Narxi Bashorati")

    if "captcha_text" not in st.session_state:
        st.session_state.captcha_text, st.session_state.captcha_image = generate_captcha()

    st.image(st.session_state.captcha_image, caption="Quyidagi matnni kiriting:")
    captcha_input = st.text_input("CAPTCHA-ni kiriting:")

    open_price = st.number_input("Open narxi:", min_value=0.0)
    high_price = st.number_input("High narxi:", min_value=0.0)
    low_price = st.number_input("Low narxi:", min_value=0.0)
    volume = st.number_input("Volume:", min_value=0.0)

    captcha_valid = verify_captcha(captcha_input, st.session_state.captcha_text)

    if st.button("Bashorat qilish"):
        if not captcha_valid:
            st.error("CAPTCHA noto‘g‘ri! Iltimos, qaytadan urinib ko‘ring.")
        else:
            input_data = pd.DataFrame({
                'Open': [open_price],
                'High': [high_price],
                'Low': [low_price],
                'Volume': [volume]
            })
            prediction = model.predict(input_data)[0]
            st.success(f"CAPTCHA to'g'ri! Kelajakdagi narx: ${prediction:.2f}")


# import streamlit as st
# import pandas as pd
# import joblib
# from captcha.image import ImageCaptcha
# import random
# import string

# # Modelni yuklash
# model = joblib.load('bitcoin_model5.pkl')

# # CAPTCHA yaratish funksiyasi
# def generate_captcha():
#     image_captcha = ImageCaptcha(width=280, height=90)
#     captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
#     image = image_captcha.generate_image(captcha_text)
#     return captcha_text, image

# # CAPTCHA tekshirish funksiyasi
# def verify_captcha(user_input, actual_captcha):
#     return user_input.strip().upper() == actual_captcha

# # Streamlit interfeysi
# st.title("Bitcoin Narxi Bashorati")
# st.write("Kelajakdagi Bitcoin narxini bashorat qiling")

# # CAPTCHA sessiya holatida saqlanadi
# if "captcha_text" not in st.session_state:
#     st.session_state.captcha_text, st.session_state.captcha_image = generate_captcha()

# # CAPTCHA-ni interfeysda ko'rsatish
# st.image(st.session_state.captcha_image, caption="Quyidagi matnni kiriting:")
# captcha_input = st.text_input("CAPTCHA-ni kiriting:")

# # Foydalanuvchi kiritishi uchun form
# open_price = st.number_input("Open narxi:", min_value=0.0)
# high_price = st.number_input("High narxi:", min_value=0.0)
# low_price = st.number_input("Low narxi:", min_value=0.0)
# volume = st.number_input("Volume:", min_value=0.0)

# # CAPTCHA tekshirish natijasi
# captcha_valid = verify_captcha(captcha_input, st.session_state.captcha_text)

# # Bashorat qilish
# if st.button("Bashorat qilish"):
#     if not captcha_valid:
#         st.error("CAPTCHA noto‘g‘ri! Iltimos, qaytadan urinib ko‘ring.")
#     else:
#         input_data = pd.DataFrame({
#             'Open': [open_price],
#             'High': [high_price],
#             'Low': [low_price],
#             'Volume': [volume]
#         })
#         prediction = model.predict(input_data)[0]
#         st.success(f"CAPTCHA to'g'ri! Kelajakdagi narx: ${prediction:.2f}")



# import streamlit as st
# import pandas as pd
# import joblib
# from captcha.image import ImageCaptcha
# import random
# import string
# from io import BytesIO
# from PIL import Image

# # Modelni yuklash
# model = joblib.load('bitcoin_model5.pkl')

# # CAPTCHA yaratish funksiyasi
# def generate_captcha():
#     image_captcha = ImageCaptcha(width=280, height=90)
#     captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
#     image = image_captcha.generate_image(captcha_text)
#     return captcha_text, image

# # CAPTCHA tekshirish funksiyasi
# def verify_captcha(user_input, actual_captcha):
#     return user_input.strip().upper() == actual_captcha

# # Interfeys
# st.title("Bitcoin Narxi Bashorati")
# st.write("Kelajakdagi Bitcoin narxini bashorat qiling")

# # Foydalanuvchi kiritishi uchun form
# open_price = st.number_input("Open narxi:", min_value=0.0)
# high_price = st.number_input("High narxi:", min_value=0.0)
# low_price = st.number_input("Low narxi:", min_value=0.0)
# volume = st.number_input("Volume:", min_value=0.0)

# # CAPTCHA yaratish
# captcha_text, captcha_image = generate_captcha()
# st.image(captcha_image, caption="Quyidagi matnni kiriting:")
# captcha_input = st.text_input("CAPTCHA-ni kiriting:")

# # Bashorat qilish
# if st.button("Bashorat qilish"):
#     if not captcha_input:
#         st.warning("Iltimos, CAPTCHA-ni kiriting!")
#     elif not verify_captcha(captcha_input, captcha_text):
#         st.error("CAPTCHA noto‘g‘ri! Iltimos, qaytadan urinib ko‘ring.")
#     else:
#         input_data = pd.DataFrame({
#             'Open': [open_price],
#             'High': [high_price],
#             'Low': [low_price],
#             'Volume': [volume]
#         })
#         prediction = model.predict(input_data)[0]
#         st.write(f"Kelajakdagi narx: ${prediction:.2f}")



# import streamlit as st
# import requests

# # Streamlit interfeysi
# st.title("Sayt himoyasi: DDoS aniqlash va bloklash")
# st.write("Quyidagi funksiyalarni sinab ko'rishingiz mumkin.")

# # So'rov yuborish
# ip_address = st.text_input("IP manzilni kiriting (bloklash uchun):")

# if st.button("So'rov yuborish"):
#     try:
#         response = requests.get("http://127.0.0.1:5000")
#         st.write(response.json())
#     except Exception as e:
#         st.error(f"So'rovda xatolik: {e}")

# if st.button("IP-ni blokdan chiqarish"):
#     if ip_address.strip():
#         response = requests.post("http://127.0.0.1:5000/unblock", json={"ip_address": ip_address})
#         st.write(response.json())
#     else:
#         st.warning("Iltimos, IP manzilni kiriting!")


# import streamlit as st
# import joblib
# import pandas as pd
# import re
# import datetime as dt

# # DDoS modelni yuklash
# ddos_model = joblib.load('models/ddos_rf_model.pkl')

# # Bitcoin modelni yuklash
# bitcoin_model = joblib.load('bitcoin_model5.pkl')

# # DDoS uchun ustun nomlari
# ddos_encoded_column_names = [
#     'ip.src_192.168.1.1', 'ip.dst_192.168.1.2', 'frame.len', 'tcp.flags.push',
#     'ip.flags.df', 'Packets', 'Bytes', 'Tx Packets', 'Tx Bytes', 'Rx Packets', 'Rx Bytes'
# ]

# # Xabarlar tarixi
# ddos_message_history = []

# # Eski xabarlarni tozalash
# def clean_ddos_message_history():
#     global ddos_message_history
#     now = dt.datetime.now()
#     ddos_message_history = [msg for msg in ddos_message_history if (now - msg['timestamp']).seconds < 60]

# # DDoS xabarini tahlil qilish
# def process_ddos_message(text):
#     ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)
#     if not ip_addresses:
#         return "IP manzillar topilmadi", None

#     frame_len = len(text)
#     packets = len(ip_addresses)
#     data = {
#         'ip.src_192.168.1.1': 1 if ip_addresses[0] == '192.168.1.1' else 0,
#         'ip.dst_192.168.1.2': 1 if len(ip_addresses) > 1 and ip_addresses[1] == '192.168.1.2' else 0,
#         'frame.len': frame_len,
#         'tcp.flags.push': 0,
#         'ip.flags.df': 1,
#         'Packets': packets,
#         'Bytes': frame_len * packets,
#         'Tx Packets': packets // 2,
#         'Tx Bytes': frame_len * (packets // 2),
#         'Rx Packets': packets // 2,
#         'Rx Bytes': frame_len * (packets // 2)
#     }

#     user_data = pd.DataFrame([data], columns=ddos_encoded_column_names)
#     prediction = ddos_model.predict(user_data)[0]
#     return f"DDoS aniqlash: {'Hujum' if prediction == 1 else 'Xavfsiz'}", prediction

# # Ilova interfeysi
# st.title("DDoS Aniqlash va Bitcoin Narx Bashorati")

# # Navigatsiya
# app_mode = st.sidebar.selectbox("Tanlang:", ["DDoS Aniqlash", "Bitcoin Narxi Bashorati"])

# if app_mode == "DDoS Aniqlash":
#     st.header("DDoS Aniqlash Interfeysi")
#     st.write("Xabar matnini kiriting va model orqali DDoS aniqlashni tekshiring.")

#     ddos_text_input = st.text_area("Xabar matni", placeholder="Xabarni bu yerga kiriting...")
#     ddos_user_id = st.text_input("Foydalanuvchi ID", value="12345")

#     if st.button("DDoS Aniqlash"):
#         if ddos_text_input.strip():
#             result, prediction = process_ddos_message(ddos_text_input)
#             st.write(result)

#             if prediction is not None:
#                 ddos_message_history.append({
#                     'timestamp': dt.datetime.now(),
#                     'text': ddos_text_input,
#                     'prediction': prediction,
#                     'user_id': ddos_user_id
#                 })
#                 clean_ddos_message_history()

#             st.subheader("Xabarlar tarixi")
#             st.write(pd.DataFrame(ddos_message_history))
#         else:
#             st.warning("Iltimos, xabar matnini kiriting!")

# elif app_mode == "Bitcoin Narxi Bashorati":
#     st.header("Bitcoin Narxi Bashorati")
#     st.write("Kelajakdagi Bitcoin narxini bashorat qiling.")

#     # Foydalanuvchi kiritishi uchun form
#     open_price = st.number_input("Open narxi:", min_value=0.0)
#     high_price = st.number_input("High narxi:", min_value=0.0)
#     low_price = st.number_input("Low narxi:", min_value=0.0)
#     volume = st.number_input("Volume:", min_value=0.0)

#     # Bashorat qilish
#     if st.button("Bashorat qilish"):
#         input_data = pd.DataFrame({
#             'Open': [open_price],
#             'High': [high_price],
#             'Low': [low_price],
#             'Volume': [volume]
#         })
#         prediction = bitcoin_model.predict(input_data)[0]
#         st.write(f"Kelajakdagi narx: ${prediction:.2f}")



# import streamlit as st
# import joblib
# import numpy as np

# def load_model():
#     # Load the pre-trained model
#     model = joblib.load("bitcoin_model.pkl")
#     return model

# def main():
#     st.title("Bitcoin Narxini Bashorat Qilish")
#     st.write("Iltimos, quyidagi parametrlarni kiriting:")

#     # Input fields for Bitcoin parameters
#     open_price = st.number_input("Open narxi", min_value=0.0, value=1000.0)
#     high_price = st.number_input("High narxi", min_value=0.0, value=1050.0)
#     low_price = st.number_input("Low narxi", min_value=0.0, value=950.0)
#     volume = st.number_input("Volume", min_value=0, value=10000)

#     if st.button("Bashorat qilish"):
#         model = load_model()
#         input_features = np.array([[open_price, high_price, low_price, volume]])
#         prediction = model.predict(input_features)

#         st.success(f"Bitcoinning bashorat qilingan narxi: ${prediction[0]:.2f}")

# if __name__ == "__main__":
#     main()

#uzgarish

# import streamlit as st
# import pandas as pd
# import joblib

# # Modelni yuklash
# model = joblib.load('bitcoin_model5.pkl')

# # Interfeys
# st.title("Bitcoin Narxi Bashorati")
# st.write("Kelajakdagi Bitcoin narxini bashorat qiling")

# # Foydalanuvchi kiritishi uchun form
# open_price = st.number_input("Open narxi:", min_value=0.0)
# high_price = st.number_input("High narxi:", min_value=0.0)
# low_price = st.number_input("Low narxi:", min_value=0.0)
# volume = st.number_input("Volume:", min_value=0.0)

# # Bashorat qilish
# if st.button("Bashorat qilish"):
#     input_data = pd.DataFrame({
#         'Open': [open_price],
#         'High': [high_price],
#         'Low': [low_price],
#         'Volume': [volume]
#     })
#     prediction = model.predict(input_data)[0]
#     st.write(f"Kelajakdagi narx: ${prediction:.2f}")
