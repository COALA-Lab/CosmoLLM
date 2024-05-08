import streamlit as st

from frontend.admin.consts import INTRO_SCREEN_MARKDOWN
from frontend.admin.utils.page_templates import login


def main():
    if not login():
        return
    st.markdown(INTRO_SCREEN_MARKDOWN)


if __name__ == "__main__":
    main()
