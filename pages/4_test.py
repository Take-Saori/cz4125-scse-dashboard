import streamlit as st
import pandas as pd
import os


df = pd.read_csv('data/updated_csv.csv')
df.head()