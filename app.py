import streamlit as st
import pickle
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch – Movie Recommender",
    page_icon="🎬",
    layout="wide",
)

# ── Custom CSS / animations ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #0a0a0f;
    color: #e8e4dc;
}

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 1rem 2rem;
    animation: fadeDown 0.8s ease both;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 6vw, 4.5rem);
    font-weight: 900;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #f5c842 0%, #e8834a 50%, #c23b5e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.4rem;
    line-height: 1.1;
}
.hero-sub {
    font-size: 1rem;
    color: #8a8078;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 300;
    margin: 0;
}

/* ── Search bar container ── */
.search-wrapper {
    max-width: 680px;
    margin: 0 auto 2.5rem;
    animation: fadeUp 0.8s 0.15s ease both;
}

/* ── Streamlit selectbox override ── */
div[data-testid="stSelectbox"] > div > div {
    background: #16151e !important;
    border: 1.5px solid #2e2a3a !important;
    border-radius: 14px !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.2rem 0.5rem !important;
    transition: border-color 0.2s;
}
div[data-testid="stSelectbox"] > div > div:hover {
    border-color: #f5c842 !important;
}

/* ── Search label ── */
.search-label {
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6b6460;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

/* ── CTA Button ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #f5c842, #e8834a) !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.65rem 2.8rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    cursor: pointer !important;
    transition: transform 0.18s, box-shadow 0.18s !important;
    box-shadow: 0 4px 24px rgba(245,200,66,0.22) !important;
    display: block;
    margin: 0 auto !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(245,200,66,0.35) !important;
}
div[data-testid="stButton"] > button:active {
    transform: translateY(0px) !important;
}

/* ── Section label ── */
.section-label {
    font-size: 0.75rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6b6460;
    text-align: center;
    margin: 2.5rem 0 1.5rem;
    font-weight: 500;
    animation: fadeUp 0.5s ease both;
}

/* ── Movie card ── */
.movie-card {
    background: #16151e;
    border-radius: 16px;
    overflow: visible;
    border: 1px solid #1e1c28;
    transition: transform 0.28s cubic-bezier(.34,1.56,.64,1),
                border-color 0.22s, box-shadow 0.28s;
    cursor: pointer;
    animation: cardPop 0.5s ease both;
}
.movie-card:hover {
    transform: translateY(-8px) scale(1.025);
    border-color: #f5c842;
    box-shadow: 0 16px 48px rgba(245,200,66,0.18);
}
.movie-card img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    display: block;
    border-radius: 16px 16px 0 0;
}
.movie-card-body {
    padding: 0.75rem 0.85rem 1.1rem;
    overflow: visible;
}
.movie-card-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    color: #e8e4dc;
    line-height: 1.5;
    margin: 0;
    white-space: normal;
    word-break: break-word;
    overflow: visible;
    display: block;
}
.movie-rank {
    font-size: 0.68rem;
    color: #f5c842;
    letter-spacing: 0.1em;
    font-weight: 500;
    margin-bottom: 0.3rem;
}

/* ── No-poster placeholder ── */
.no-poster {
    width: 100%;
    aspect-ratio: 2/3;
    background: #1e1c28;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #3a3646;
    font-size: 2.5rem;
}

/* ── Divider ── */
.gold-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #f5c842 40%, #e8834a 60%, transparent);
    border: none;
    margin: 2rem auto;
    max-width: 320px;
}

/* ── Keyframes ── */
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes cardPop {
    from { opacity: 0; transform: translateY(30px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── Stagger delays for cards 1-5 ── */
.delay-1 { animation-delay: 0.05s; }
.delay-2 { animation-delay: 0.12s; }
.delay-3 { animation-delay: 0.19s; }
.delay-4 { animation-delay: 0.26s; }
.delay-5 { animation-delay: 0.33s; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    movies = pickle.load(open("movies_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

movies, similarity = load_data()
movies_list = movies["title"].values


# ── Poster fetch ───────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = (
        f"https://api.themoviedb.org/3/movie/{movie_id}"
        "?api_key=4568f770d0e2275e5006450022df93b0&language=en-US"
    )
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        path = data.get("poster_path")
        return f"https://image.tmdb.org/t/p/w500{path}" if path else None
    except requests.exceptions.RequestException:
        return None


# ── Recommendation engine ──────────────────────────────────────────────────────
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        enumerate(similarity[index]), key=lambda x: x[1], reverse=True
    )
    names, posters = [], []
    for i, _ in distances[1:6]:
        mid = movies.iloc[i].id
        names.append(movies.iloc[i].title)
        posters.append(fetch_poster(mid))
    return names, posters


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <p class="hero-title">CineMatch</p>
    <p class="hero-sub">Discover your next favourite film</p>
</div>
<hr class="gold-divider">
""", unsafe_allow_html=True)


# ── Search / select ────────────────────────────────────────────────────────────
_, mid_col, _ = st.columns([1, 2.4, 1])
with mid_col:
    st.markdown('<p class="search-label">Search or pick a movie</p>', unsafe_allow_html=True)
    selected_movie = st.selectbox(
        label="",
        options=movies_list,
        label_visibility="collapsed",
    )
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    recommend_btn = st.button("✦ Find Recommendations")


# ── Results ────────────────────────────────────────────────────────────────────
if recommend_btn:
    with st.spinner("Curating picks for you…"):
        names, posters = recommend(selected_movie)

    st.markdown(
        f'<p class="section-label">Because you like &nbsp;·&nbsp; {selected_movie}</p>',
        unsafe_allow_html=True,
    )

    cols = st.columns(5, gap="small")
    delay_classes = ["delay-1", "delay-2", "delay-3", "delay-4", "delay-5"]

    for idx, (col, name, poster, dc) in enumerate(zip(cols, names, posters, delay_classes), 1):
        with col:
            if poster:
                img_html = f'<img src="{poster}" alt="{name}" loading="lazy">'
            else:
                img_html = '<div class="no-poster">🎬</div>'

            st.markdown(f"""
            <div class="movie-card {dc}">
                {img_html}
                <div class="movie-card-body">
                    <p class="movie-rank">#{idx} Pick</p>
                    <p class="movie-card-title">{name}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)