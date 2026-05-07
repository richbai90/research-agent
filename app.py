import streamlit as st
from pathlib import Path
import os

page_root = Path("./pages")
pages = os.listdir(page_root)

pg = st.navigation([st.Page(page_root / page) for page in pages])
pg.run()
