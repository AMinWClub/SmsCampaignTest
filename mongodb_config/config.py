from dotenv import load_dotenv
import os
import streamlit as st
from pymongo import MongoClient

load_dotenv()

@st.cache_resource
def get_db():
    client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
    db = client["sms_task"]
    return db