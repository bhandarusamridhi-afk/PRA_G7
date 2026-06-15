"""
AthleteOS - Athlete Performance Intelligence Platform
=====================================================
A Streamlit mock-up unifying physical + mental performance data for
athletes and coaches. Built from the APIP PRD v1.0.

Run locally:    streamlit run streamlit_app.py
Deploy:         GitHub -> Streamlit Community Cloud (main file: streamlit_app.py)
"""

from __future__ import annotations

import streamlit as st

from core import data, theme
from views import athlete as athlete_view
from views import coach as coach_view

st.set_page_config(
    page_title="AthleteOS",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.inject_css()


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------
def _get_account() -> data.Account | None:
    return st.session_state.get("account")


def _logout() -> None:
    st.session_state.pop("account", None)
    st.rerun()


# ---------------------------------------------------------------------------
# Login screen
# ---------------------------------------------------------------------------
def login_screen() -> None:
    left, mid, right = st.columns([1, 1.4, 1])
    with mid:
        st.markdown("<div style='height:6vh'></div>", unsafe_allow_html=True)
        theme.brand_header("Athlete Performance Intelligence Platform")
        st.markdown(
            f"<p style='color:{theme.TEXT_MUTED};font-size:1.02rem;margin-top:6px'>"
            "One intelligent platform unifying physical and mental performance data - "
            "so athletes and coaches see the <b style='color:#EAF2FF'>whole athlete</b>, "
            "not twelve scattered tabs.</p>",
            unsafe_allow_html=True,
        )
        st.markdown("####  ")

        with st.form("login"):
            st.markdown("##### Sign in")
            user_id = st.text_input("User ID", placeholder="e.g. alex or coach_maria")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Enter AthleteOS", use_container_width=True)

        if submitted:
            acct = data.authenticate(user_id, password)
            if acct:
                st.session_state["account"] = acct
                st.rerun()
            else:
                st.error("Invalid credentials. Try one of the demo accounts below.")

        with st.expander("Demo accounts (click to view)", expanded=True):
            st.markdown(
                f"""
                <div style="color:{theme.TEXT}">
                <b style="color:{theme.PRIMARY}">Coaches</b> (password: <code>coach123</code>) - each sees only their own sport's squad:
                <ul>
                  <li><code>coach_maria</code> - Track &amp; Field</li>
                  <li><code>coach_david</code> - Swimming</li>
                  <li><code>coach_tara</code> - Basketball</li>
                </ul>
                <b style="color:{theme.PRIMARY}">Athletes</b> (password = <code>id123</code>, e.g. <code>alex</code>):
                <ul>
                  <li>Track &amp; Field: <code>alex</code>, <code>jordan</code>, <code>maya</code>, <code>sam</code></li>
                  <li>Swimming: <code>lena</code>, <code>tom</code>, <code>nina</code></li>
                  <li>Basketball: <code>marcus</code>, <code>chris</code>, <code>andre</code></li>
                </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Sidebar (authenticated)
# ---------------------------------------------------------------------------
def sidebar(account: data.Account) -> None:
    with st.sidebar:
        theme.brand_header("")
        st.markdown("---")
        role_label = "Coach" if account.role == "coach" else "Athlete"
        st.markdown(
            f"**{account.name}**  \n"
            f"<span style='color:{theme.TEXT_MUTED}'>{role_label} &middot; {account.sport}"
            + (f" &middot; {account.event}" if account.event else "")
            + "</span>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.caption("AthleteOS demo - synthetic data, refreshed deterministically per athlete.")
        if st.button("Log out", use_container_width=True):
            _logout()


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
def main() -> None:
    account = _get_account()
    if account is None:
        login_screen()
        return

    sidebar(account)
    if account.role == "coach":
        coach_view.render(account)
    else:
        athlete_view.render(account)


if __name__ == "__main__":
    main()
