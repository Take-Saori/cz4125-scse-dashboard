import streamlit as st
import pandas as pd
import os


df = pd.read_csv(r'updated_csv.csv')
st.dataframe(df)