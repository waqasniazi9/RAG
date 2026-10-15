import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from rag import answer_question, build_index, data_files


BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")

st.set_page_config(
    page_title="Northstar | Company Knowledge",
    page_icon="✳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #18231f;
        --muted: #77817b;
        --green: #187c5c;
        --green-dark: #116447;
        --mint: #eaf4ee;
        --line: #e9ece9;
        --paper: #ffffff;
    }
    .stApp {
        background: #fbfcfa;
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }
    [data-testid="stHeader"] { background: rgba(251, 252, 250, .88); }
    [data-testid="stSidebar"] {
        background: #f5f7f3;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.4rem; }
    .block-container { max-width: 1120px; padding: 2rem 3.5rem 7rem; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; color: var(--ink); letter-spacing: -.035em; }
    .brand { display: flex; align-items: center; gap: 11px; margin-bottom: 2.1rem; }
    .brand-mark {
        width: 39px; height: 39px; display: grid; place-items: center;
        border-radius: 13px; color: white; background: var(--green);
        font: 800 20px 'Manrope', sans-serif; box-shadow: 0 5px 14px #187c5c2b;
    }
    .brand-name { font: 800 15px 'Manrope', sans-serif; letter-spacing: -.03em; }
    .brand-sub { color: var(--muted); font-size: 11px; margin-top: 1px; }
    .eyebrow {
        display: inline-flex; align-items: center; gap: 7px;
        color: var(--green-dark); background: var(--mint);
        border: 1px solid #d9eade; border-radius: 99px;
        padding: 6px 11px; font-size: 11px; font-weight: 700;
        letter-spacing: .075em; text-transform: uppercase;
    }
    .hero { padding: 1.4rem 0 1.7rem; }
    .hero h1 { font-size: clamp(2.1rem, 4.4vw, 3.6rem); line-height: 1.08; margin: 1rem 0 .8rem; }
    .hero p { max-width: 640px; color: #66716a; font-size: 16px; line-height: 1.7; margin: 0; }
    .hero-accent { color: var(--green); }
    .trust-row { display:flex; flex-wrap:wrap; gap:9px; margin-top:1.35rem; }
    .trust-pill { color:#59655e; background:#fff; border:1px solid var(--line); border-radius:99px; padding:7px 11px; font-size:11px; }
    .section-label { font: 700 12px 'Manrope', sans-serif; color:#66716a; margin:1.35rem 0 .8rem; }
    .welcome-card {
        border:1px solid var(--line); border-radius:20px; padding:24px 26px;
        background:linear-gradient(120deg,#f1f7f1 0%,#f9fbf8 72%,#fff 100%);
        margin: 1rem 0 1.5rem;
    }
    .welcome-title { font:700 18px 'Manrope',sans-serif; margin-bottom:5px; }
    .welcome-copy { color:#758078; font-size:13px; line-height:1.6; }
    div[data-testid="stButton"] button {
        border:1px solid var(--line); border-radius:12px; background:#fff;
        color:#27342d; min-height:48px; text-align:left; font-size:13px;
        transition:all .16s ease;
    }
    div[data-testid="stButton"] button:hover {
        border-color:#a9cbb5; color:var(--green-dark); background:#f7fbf7;
        transform:translateY(-1px);
    }
    [data-testid="stChatMessage"] {
        border:1px solid var(--line); border-radius:17px;
        padding:1rem 1.1rem; background:#fff; margin-bottom:.85rem;
    }
    [data-testid="stChatInput"] {
        border:1px solid #dfe5df; border-radius:17px;
        box-shadow:0 8px 30px #1b33230b; background:white;
    }
    [data-testid="stChatInput"]:focus-within { border-color:#8cb89b; box-shadow:0 0 0 3px #187c5c12; }
    [data-testid="stChatInput"] textarea { font-family:'DM Sans',sans-serif; }
    .sidebar-heading { font:700 12px 'Manrope',sans-serif; color:#536057; margin:1.2rem 0 .7rem; }
    .sidebar-note { color:#818b83; font-size:11px; line-height:1.6; }
    .sidebar-file {
        overflow-wrap:anywhere; color:#59655e; font-size:11px;
        padding:8px 10px; background:#fff; border:1px solid var(--line);
        border-radius:9px; margin:5px 0;
    }
    .status-dot { color:#18845c; font-size:14px; margin-right:5px; }
    div[data-testid="stMetric"] {
        background:#fff; border:1px solid var(--line); border-radius:12px;
        padding:12px 14px;
    }
    div[data-testid="stMetricLabel"] { color:#7b857e; font-size:11px; }
    div[data-testid="stMetricValue"] { color:#26332b; font:700 22px 'Manrope',sans-serif; }
    [data-testid="stExpander"] { border-color:var(--line); border-radius:12px; background:#fff; }
    .footer { color:#a0a8a1; font-size:11px; text-align:center; padding:1.4rem 0 0; }
    @media(max-width: 700px) {
        .block-container { padding:1.4rem 1rem 6rem; }
        .hero { padding-top:.6rem; }
        .hero p { font-size:14px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def setting(key, default=""):
    value = os.getenv(key)
    if value:
        return value
    try:
        return str(st.secrets.get(key, default))
    except FileNotFoundError:
        return default


@st.cache_resource(show_spinner=False)
def cached_index(data_dir, fingerprint, embedding_model, _api_key):
    return build_index(Path(data_dir), _api_key, embedding_model)


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
          <div class="brand-mark">N</div>
          <div><div class="brand-name">Northstar</div><div class="brand-sub">Company knowledge assistant</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sidebar-heading">YOUR KNOWLEDGE BASE</div>', unsafe_allow_html=True)

api_key = setting("OPENAI_API_KEY")
chat_model = setting("OPENAI_MODEL", "gpt-4o-mini")
embedding_model = setting("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

if not api_key or api_key == "your_openai_api_key_here":
    st.markdown(
        """
        <div class="hero">
          <span class="eyebrow">✳ &nbsp; COMPANY KNOWLEDGE, MADE SIMPLE</span>
          <h1>Your company answers,<br><span class="hero-accent">all in one place.</span></h1>
          <p>A clear, focused workspace for finding answers across your company's policies and product knowledge.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning("Add OPENAI_API_KEY to your .env file or Streamlit app secrets to connect your knowledge assistant.")
    st.stop()

paths = data_files(BASE / "data")
fingerprint = tuple(
    (str(path.relative_to(BASE)), path.stat().st_mtime_ns, path.stat().st_size)
    for path in paths
)
try:
    with st.spinner("Preparing your company knowledge..."):
        store, stats = cached_index(str(BASE / "data"), fingerprint, embedding_model, api_key)
except Exception:
    st.error(
        "The knowledge base could not be prepared. Check your local files, package installation, "
        "API key, model access and API billing. No chat response was generated."
    )
    st.stop()

with st.sidebar:
    st.markdown('<div class="sidebar-heading"><span class="status-dot">●</span>INDEX READY</div>', unsafe_allow_html=True)
    metric_left, metric_right = st.columns(2)
    metric_left.metric("Files", stats["files"])
    metric_right.metric("Passages", stats["chunks"])
    for path in paths:
        st.markdown(
            f'<div class="sidebar-file">▤ &nbsp; {path.relative_to(BASE / "data")}</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="sidebar-heading">HOW IT WORKS</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-note">Ask a question in plain language. The assistant searches your company files and shows the passages behind each supported answer.</div>',
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("＋  Start a new conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown(
        '<div class="sidebar-note">Your files and questions are processed by OpenAI. Use only authorized data and configure Streamlit Secrets before deploying.</div>',
        unsafe_allow_html=True,
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    """
    <div class="hero">
      <span class="eyebrow">✳ &nbsp; YOUR COMPANY, WITHIN REACH</span>
      <h1>Good questions lead to<br><span class="hero-accent">clear answers.</span></h1>
      <p>Find what you need in your company's knowledge base. Ask naturally, get a concise answer, and see exactly where it came from.</p>
      <div class="trust-row">
        <span class="trust-pill">⌕ &nbsp; Search company files</span>
        <span class="trust-pill">◉ &nbsp; Sources included</span>
        <span class="trust-pill">↗ &nbsp; Ask in plain language</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


def render_sources(sources):
    if sources:
        with st.expander(f"View {len(sources)} supporting passage{'s' if len(sources) != 1 else ''}"):
            for source in sources:
                suffix = f" · Sheet: {source['sheet']}" if source.get("sheet") else ""
                st.caption(f"Passage {source['passage']} · {source['file']}{suffix}")
                st.text(source["text"])


if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-card">
          <div class="welcome-title">What would you like to know?</div>
          <div class="welcome-copy">Start with a suggestion or type your own question below.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    suggestions = [
        "What are the office hours?",
        "How many annual leave days are provided?",
        "What is the return policy?",
        "Tell me about the products.",
    ]
    prompt_columns = st.columns(2)
    selected_prompt = None
    for index, prompt in enumerate(suggestions):
        if prompt_columns[index % 2].button(prompt, key=f"suggestion_{index}", use_container_width=True):
            selected_prompt = prompt
else:
    selected_prompt = None
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            render_sources(message.get("sources", []))

question = st.chat_input("Ask a question about your company...", max_chars=2000)
question = question or selected_prompt

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching your company knowledge..."):
                result = answer_question(question, store, api_key, chat_model)
            st.markdown(result["answer"])
            render_sources(result["sources"])
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                }
            )
        except Exception:
            error = (
                "The request failed. Please check API access/billing or try again. "
                "This is a service error, not evidence that the answer is missing from the data."
            )
            st.error(error)
            st.session_state.messages.append(
                {"role": "assistant", "content": error, "sources": []}
            )
