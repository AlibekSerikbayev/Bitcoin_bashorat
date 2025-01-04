import streamlit as st
import joblib
import pandas as pd
import re
import datetime as dt

# DDoS modelni yuklash
ddos_model = joblib.load('models/ddos_rf_model.pkl')

# Bitcoin modelni yuklash
bitcoin_model = joblib.load('bitcoin_model5.pkl')

# DDoS uchun ustun nomlari
ddos_encoded_column_names = [
    'ip.src_192.168.1.1', 'ip.dst_192.168.1.2', 'frame.len', 'tcp.flags.push',
    'ip.flags.df', 'Packets', 'Bytes', 'Tx Packets', 'Tx Bytes', 'Rx Packets', 'Rx Bytes'
]

# Xabarlar tarixi
ddos_message_history = []

# Eski xabarlarni tozalash
def clean_ddos_message_history():
    global ddos_message_history
    now = dt.datetime.now()
    ddos_message_history = [msg for msg in ddos_message_history if (now - msg['timestamp']).seconds < 60]

# DDoS xabarini tahlil qilish
def process_ddos_message(text):
    ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text)
    if not ip_addresses:
        return "IP manzillar topilmadi", None

    frame_len = len(text)
    packets = len(ip_addresses)
    data = {
        'ip.src_192.168.1.1': 1 if ip_addresses[0] == '192.168.1.1' else 0,
        'ip.dst_192.168.1.2': 1 if len(ip_addresses) > 1 and ip_addresses[1] == '192.168.1.2' else 0,
        'frame.len': frame_len,
        'tcp.flags.push': 0,
        'ip.flags.df': 1,
        'Packets': packets,
        'Bytes': frame_len * packets,
        'Tx Packets': packets // 2,
        'Tx Bytes': frame_len * (packets // 2),
        'Rx Packets': packets // 2,
        'Rx Bytes': frame_len * (packets // 2)
    }

    user_data = pd.DataFrame([data], columns=ddos_encoded_column_names)
    prediction = ddos_model.predict(user_data)[0]
    return f"DDoS aniqlash: {'Hujum' if prediction == 1 else 'Xavfsiz'}", prediction

# Ilova interfeysi
st.title("DDoS Aniqlash va Bitcoin Narx Bashorati")

# Navigatsiya
app_mode = st.sidebar.selectbox("Tanlang:", ["DDoS Aniqlash", "Bitcoin Narxi Bashorati"])

if app_mode == "DDoS Aniqlash":
    st.header("DDoS Aniqlash Interfeysi")
    st.write("Xabar matnini kiriting va model orqali DDoS aniqlashni tekshiring.")

    ddos_text_input = st.text_area("Xabar matni", placeholder="Xabarni bu yerga kiriting...")
    ddos_user_id = st.text_input("Foydalanuvchi ID", value="12345")

    if st.button("DDoS Aniqlash"):
        if ddos_text_input.strip():
            result, prediction = process_ddos_message(ddos_text_input)
            st.write(result)

            if prediction is not None:
                ddos_message_history.append({
                    'timestamp': dt.datetime.now(),
                    'text': ddos_text_input,
                    'prediction': prediction,
                    'user_id': ddos_user_id
                })
                clean_ddos_message_history()

            st.subheader("Xabarlar tarixi")
            st.write(pd.DataFrame(ddos_message_history))
        else:
            st.warning("Iltimos, xabar matnini kiriting!")

elif app_mode == "Bitcoin Narxi Bashorati":
    st.header("Bitcoin Narxi Bashorati")
    st.write("Kelajakdagi Bitcoin narxini bashorat qiling.")

    # Foydalanuvchi kiritishi uchun form
    open_price = st.number_input("Open narxi:", min_value=0.0)
    high_price = st.number_input("High narxi:", min_value=0.0)
    low_price = st.number_input("Low narxi:", min_value=0.0)
    volume = st.number_input("Volume:", min_value=0.0)

    # Bashorat qilish
    if st.button("Bashorat qilish"):
        input_data = pd.DataFrame({
            'Open': [open_price],
            'High': [high_price],
            'Low': [low_price],
            'Volume': [volume]
        })
        prediction = bitcoin_model.predict(input_data)[0]
        st.write(f"Kelajakdagi narx: ${prediction:.2f}")



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
