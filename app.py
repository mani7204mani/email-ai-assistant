import os
import re
import streamlit as st
from gmail_helper import get_auth_url, get_service_from_code, get_unread_emails, send_email_html
from ai_engine import summarize_email, generate_replies

st.set_page_config(page_title="AI Email Assistant", page_icon="📧", layout="wide")
st.title("📧 AI Email Summarizer & Reply Generator")

REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://localhost:8501")

# ── Step 1: Gmail Auth ──────────────────────────────────────────
if 'service' not in st.session_state:
    params = st.query_params

    if 'code' in params:
        with st.spinner("Authenticating..."):
            try:
                service = get_service_from_code(params['code'], REDIRECT_URI)
                st.session_state.service = service
                st.query_params.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")
                st.info("👇 Please try logging in again")
                st.query_params.clear()
                if st.button("🔄 Try Again"):
                    st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px;">
            <h2>👋 Welcome to AI Email Assistant</h2>
            <p style="color:#888; font-size:16px;">
                Summarize emails and generate smart replies in one click.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("🔗 Login with Gmail", type="primary", use_container_width=True):
                try:
                    auth_url = get_auth_url(REDIRECT_URI)
                    st.markdown(f'''
                    <meta http-equiv="refresh" content="0; url={auth_url}">
                    <p>Redirecting... <a href="{auth_url}">Click here</a> if not redirected.</p>
                    ''', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error generating login URL: {e}")

    st.stop()

# ── Step 2: Ask for Signature once ─────────────────────────────
if 'signature' not in st.session_state:
    st.markdown("### ✍️ Set Your Email Signature")
    st.markdown("This will be added to the bottom of every reply you send.")

    with st.form("signature_form"):
        name     = st.text_input("Your Full Name",          placeholder="Mani Reddy")
        title    = st.text_input("Your Job Title",          placeholder="Software Engineer")
        company  = st.text_input("Company (optional)",      placeholder="ABC Tech")
        phone    = st.text_input("Phone (optional)",        placeholder="+91 9999999999")
        linkedin = st.text_input("LinkedIn URL (optional)", placeholder="https://linkedin.com/in/yourname")
        submitted = st.form_submit_button("💾 Save & Continue", type="primary")

        if submitted:
            if not name:
                st.error("Please enter at least your name.")
            else:
                st.session_state.signature = {
                    "name": name, "title": title,
                    "company": company, "phone": phone, "linkedin": linkedin
                }
                st.rerun()
    st.stop()

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    max_emails = st.slider("Emails to fetch", 1, 20, 5)
    if st.button("🔄 Refresh Emails", type="primary"):
        st.session_state.emails    = None
        st.session_state.summaries = {}
        st.session_state.replies   = {}
    st.divider()
    sig = st.session_state.signature
    st.markdown("**✍️ Your Signature**")
    st.markdown(f"**{sig['name']}**")
    if sig['title']:   st.caption(sig['title'])
    if sig['company']: st.caption(sig['company'])
    if sig['phone']:   st.caption(sig['phone'])
    if st.button("✏️ Edit Signature"):
        del st.session_state.signature
        st.rerun()
    st.divider()
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Step 3: Fetch Emails ─────────────────────────────────────────
if 'emails' not in st.session_state or st.session_state.emails is None:
    with st.spinner("Fetching unread emails..."):
        try:
            st.session_state.emails    = get_unread_emails(st.session_state.service, max_emails)
            st.session_state.summaries = {}
            st.session_state.replies   = {}
        except Exception as e:
            st.error(f"Error fetching emails: {e}")
            st.stop()

emails = st.session_state.get('emails', [])

if not emails:
    st.info("📭 No unread emails found!")
else:
    st.success(f"✅ {len(emails)} unread emails found!")

    for i, email in enumerate(emails):
        with st.expander(f"📩  {email['subject']}   —   {email['sender']}"):

            # ── Full clean email body ─────────────────────
            st.markdown("**📜 Original Email**")
            clean_body = re.sub(r'<[^>]+>', '', email['body'])
            clean_body = re.sub(r'\n{3,}', '\n\n', clean_body).strip()
            st.markdown(
                f"""<div style="background-color:#1e1e1e; border:1px solid #444;
                border-radius:8px; padding:16px 20px; font-family:Arial,sans-serif;
                font-size:14px; line-height:1.8; color:#e0e0e0; white-space:pre-wrap;
                max-height:400px; overflow-y:auto;">{clean_body}</div>""",
                unsafe_allow_html=True
            )

            st.divider()
            col1, col2 = st.columns(2)

            # ── Summary ──────────────────────────────────
            with col1:
                st.markdown("**📋 AI Summary**")
                if st.button("Generate Summary", key=f"sum_btn_{i}"):
                    with st.spinner("Analyzing..."):
                        st.session_state.summaries[i] = summarize_email(email)
                if i in st.session_state.get('summaries', {}):
                    st.info(st.session_state.summaries[i])

            # ── Replies ──────────────────────────────────
            with col2:
                st.markdown("**✍️ Reply Suggestions**")
                if st.button("Generate Replies", key=f"rep_btn_{i}"):
                    with st.spinner("Crafting replies..."):
                        raw   = generate_replies(email)
                        parts = raw.split("Option 2:")
                        opt1  = parts[0].replace("Option 1:", "").strip()
                        opt2  = parts[1].strip() if len(parts) > 1 else ""
                        st.session_state.replies[i] = {"opt1": opt1, "opt2": opt2}

                if i in st.session_state.get('replies', {}):
                    replies      = st.session_state.replies[i]
                    sender_raw   = email['sender']
                    sender_email = sender_raw.split('<')[1].replace('>', '').strip() if '<' in sender_raw else sender_raw.strip()
                    sender_name  = sender_raw.split('<')[0].strip()                  if '<' in sender_raw else sender_raw
                    sig          = st.session_state.signature

                    # Signature parts
                    phone_part    = f"{sig['phone']}"                                       if sig.get('phone')    else ""
                    linkedin_part = f'<a href="{sig["linkedin"]}">LinkedIn</a>'             if sig.get('linkedin') else ""
                    company_part  = f"{sig['title']} | {sig['company']}"                    if sig.get('company')  else sig.get('title','')

                    # ══ Option 1 ══════════════════════════
                    st.markdown("""
                        <div style="background:#1a3a2a; border-left:4px solid #2ecc71;
                        padding:10px 14px; border-radius:6px; margin-top:12px;">
                        <b style="color:#2ecc71;">Option 1 — Brief Reply</b></div>
                    """, unsafe_allow_html=True)

                    edited_opt1 = st.text_area(
                        "Option 1 reply",
                        value=replies['opt1'],
                        height=180,
                        key=f"edit_opt1_{i}",
                        label_visibility="collapsed"
                    )

                    with st.expander("👁️ Preview full email"):
                        st.markdown(f"""
<div style="font-family:Arial,sans-serif; font-size:14px;
    padding:16px; border:1px solid #444; border-radius:8px; line-height:1.8;">
    <p style="color:#aaa; margin:0 0 8px;">
        <b>To:</b> {sender_email}<br>
        <b>Subject:</b> Re: {email['subject']}
    </p>
    <hr style="border-color:#444; margin:10px 0;">
    <p>Dear {sender_name},</p>
    <p>{edited_opt1.replace(chr(10), '<br>')}</p>
    <hr style="border-color:#4A90E2; margin:16px 0 10px;">
    <p style="margin:0;"><b>{sig['name']}</b></p>
    <p style="margin:4px 0; color:#888; font-size:13px;">{company_part}</p>
    <p style="margin:4px 0; color:#888; font-size:13px;">{phone_part} {linkedin_part}</p>
</div>
                        """, unsafe_allow_html=True)

                    if st.button("📤 Send Option 1", key=f"send_opt1_{i}", type="primary"):
                        with st.spinner("Sending..."):
                            try:
                                send_email_html(
                                    st.session_state.service, sender_email,
                                    email['subject'], edited_opt1, sig, sender_name
                                )
                                st.success("✅ Option 1 sent successfully!")
                            except Exception as e:
                                st.error(f"Failed: {e}")

                    st.markdown("<br>", unsafe_allow_html=True)

                    # ══ Option 2 ══════════════════════════
                    st.markdown("""
                        <div style="background:#1a2a3a; border-left:4px solid #4A90E2;
                        padding:10px 14px; border-radius:6px; margin-top:4px;">
                        <b style="color:#4A90E2;">Option 2 — Detailed Reply</b></div>
                    """, unsafe_allow_html=True)

                    edited_opt2 = st.text_area(
                        "Option 2 reply",
                        value=replies['opt2'],
                        height=200,
                        key=f"edit_opt2_{i}",
                        label_visibility="collapsed"
                    )

                    with st.expander("👁️ Preview full email"):
                        st.markdown(f"""
<div style="font-family:Arial,sans-serif; font-size:14px;
    padding:16px; border:1px solid #444; border-radius:8px; line-height:1.8;">
    <p style="color:#aaa; margin:0 0 8px;">
        <b>To:</b> {sender_email}<br>
        <b>Subject:</b> Re: {email['subject']}
    </p>
    <hr style="border-color:#444; margin:10px 0;">
    <p>Dear {sender_name},</p>
    <p>{edited_opt2.replace(chr(10), '<br>')}</p>
    <hr style="border-color:#4A90E2; margin:16px 0 10px;">
    <p style="margin:0;"><b>{sig['name']}</b></p>
    <p style="margin:4px 0; color:#888; font-size:13px;">{company_part}</p>
    <p style="margin:4px 0; color:#888; font-size:13px;">{phone_part} {linkedin_part}</p>
</div>
                        """, unsafe_allow_html=True)

                    if st.button("📤 Send Option 2", key=f"send_opt2_{i}", type="primary"):
                        with st.spinner("Sending..."):
                            try:
                                send_email_html(
                                    st.session_state.service, sender_email,
                                    email['subject'], edited_opt2, sig, sender_name
                                )
                                st.success("✅ Option 2 sent successfully!")
                            except Exception as e:
                                st.error(f"Failed: {e}")