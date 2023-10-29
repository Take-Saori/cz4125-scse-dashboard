import streamlit as st
import pandas as pd


try:
    st.write('Trying with back slashes')
    st.dataframe(pd.read_csv(r'.\\data\\updated_csv.csv'))
except:
    st.write('It didn\'t work with back slashes.')


try:
    st.write('Trying with forward slashes')
    st.dataframe(pd.read_csv(r'data/updated_csv.csv'))
except:
    st.write('It didn\'t work with forward slashes.')