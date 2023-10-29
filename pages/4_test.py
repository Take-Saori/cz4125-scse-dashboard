import streamlit as st
import pandas as pd
import os


df = pd.read_csv('updated_csv.csv')

st.dataframe(df, use_container_width=True)