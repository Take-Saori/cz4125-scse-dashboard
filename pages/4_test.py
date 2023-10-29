import streamlit as st
import pandas as pd
import os


df = pd.read_csv('/workspaces/cz4125-scse-dashboard/pages/updated_csv.csv')
st.dataframe(df)