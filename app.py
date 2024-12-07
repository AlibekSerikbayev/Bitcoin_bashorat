import streamlit as st
import joblib
import numpy as np

def load_model():
    # Load the pre-trained model
    model = joblib.load("bitcoin_model.pkl")
    return model

def main():
    st.title("Bitcoin Narxini Bashorat Qilish")
    st.write("Iltimos, quyidagi parametrlarni kiriting:")

    # Input fields for Bitcoin parameters
    open_price = st.number_input("Open narxi", min_value=0.0, value=1000.0)
    high_price = st.number_input("High narxi", min_value=0.0, value=1050.0)
    low_price = st.number_input("Low narxi", min_value=0.0, value=950.0)
    volume = st.number_input("Volume", min_value=0, value=10000)

    if st.button("Bashorat qilish"):
        model = load_model()
        input_features = np.array([[open_price, high_price, low_price, volume]])
        prediction = model.predict(input_features)

        st.success(f"Bitcoinning bashorat qilingan narxi: ${prediction[0]:.2f}")

if __name__ == "__main__":
    main()

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
# close_price = st.number_input("Close narxi:", min_value=0.0)
# volume = st.number_input("Volume:", min_value=0.0)

# # Bashorat qilish
# if st.button("Bashorat qilish"):
#     input_data = pd.DataFrame({
#         'Open': [open_price],
#         'High': [high_price],
#         'Low': [low_price],
#         'Close': [close_price],
#         'Volume': [volume]
#     })
#     prediction = model.predict(input_data)[0]
#     st.write(f"Kelajakdagi narx: ${prediction:.2f}")



