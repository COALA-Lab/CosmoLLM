import datetime
import secrets

import streamlit as st
from streamlit_authenticator import Authenticate
from streamlit_authenticator.utilities.hasher import Hasher

from . import consts
from .. import settings
from mongo_integration.client import Mongo


class Auth:
    def __init__(self):
        self._init_db()
        self.streamlit_auth: Authenticate = self._init_auth()

    def login(self) -> bool:
        _, authentication_status, username = self.streamlit_auth.login()
        if authentication_status:
            self.streamlit_auth.logout(location="sidebar")  # Insert Logout widget
            return True
        elif authentication_status == False:
            st.error('Username/password is incorrect!')
            return False
        elif authentication_status == None:
            st.warning('Please enter your username and password!')
            return False

        return False

    def _init_db(self) -> None:
        mongo = Mongo()

        if mongo.credentials.count_documents({}) == 0:
            credentials = {
                settings.ADMIN_USER: {
                    "password": Hasher([settings.ADMIN_PASSWORD]).generate()[0],
                    "name": settings.ADMIN_USER,
                }
            }
            mongo.credentials.insert_one(credentials)

        if mongo.cookies.count_documents({}) == 0:
            cookie = {
                "name": secrets.token_urlsafe(32),
                "key": secrets.token_urlsafe(32),
                "createdAt": datetime.datetime.now(),
            }
            mongo.cookies.insert_one(cookie)

    def _init_auth(self) -> Authenticate:
        if not st.session_state.get("cosmollm_credentials"):
            credentials = list(Mongo().credentials.find({}, {"_id": 0}))

            credentials_dict = {}
            for credential in credentials:
                credentials_dict.update(credential)
            credentials = {"usernames": credentials_dict}

            st.session_state.cosmollm_credentials = credentials

        if not st.session_state.get("cosmollm_cookie"):
            cookie = Mongo().cookies.find_one({})
            st.session_state.cosmollm_cookie = cookie

            if cookie["createdAt"] + datetime.timedelta(days=consts.COOKIES_EXPIRY_DAYS) < datetime.datetime.now():
                cookie = {
                    "name": secrets.token_urlsafe(32),
                    "key": secrets.token_urlsafe(32),
                    "createdAt": datetime.datetime.now(),
                }
            Mongo().cookies.update_one({}, {"$set": cookie})
            st.session_state.cosmollm_cookie = cookie

        credentials = st.session_state.cosmollm_credentials
        cookie = st.session_state.cosmollm_cookie

        auth = Authenticate(
            credentials,
            cookie["name"],
            cookie["key"],
            consts.COOKIES_EXPIRY_DAYS,
        )

        return auth
