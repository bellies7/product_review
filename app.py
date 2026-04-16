import streamlit as st
import os, json, time, re, collections
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from openai import OpenAI
from tavily import TavilyClient

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ProductReview",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS — beige background, blue accents, serif font ──────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lora:wght@400;500;600&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Lora', Georgia, serif;
    background-color: #F5F0E8;
    color: #2C2C2C;
}

/* Main container */
.main .block-container {
    background-color: #F5F0E8;
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 860px;
}

/* Hide Streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Title */
.pr-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #1A3A5C;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem;
}

.pr-subtitle {
    font-family: 'Lora', Georgia, serif;
    font-size: 1.05rem;
    color: #6B6B6B;
    margin-bottom: 2.5rem;
}

/* Input area */
.stTextInput > div > div > input {
    font-family: 'Lora', Georgia, serif;
    font-size: 1rem;
    background-color: #FDFAF4;
    border: 1.5px solid #C8B99A;
    border-radius: 6px;
    color: #2C2C2C;
    padding: 0.6rem 0.9rem;
}
.stTextInput > div > div > input:focus {
    border-color: #1A3A5C;
    box-shadow: 0 0 0 2px rgba(26,58,92,0.12);
}
.stTextInput label {
    font-family: 'Lora', Georgia, serif;
    font-size: 0.92rem;
    color: #4A4A4A;
    font-weight: 600;
}

/* Button */
.stButton > button {
    font-family: 'Lora', Georgia, serif;
    font-size: 1rem;
    font-weight: 600;
    background-color: #1A3A5C;
    color: #FDFAF4;
    border: none;
    border-radius: 6px;
    padding: 0.6rem 2rem;
    transition: background-color 0.2s ease;
    cursor: pointer;
}
.stButton > button:hover {
    background-color: #254D7A;
}

/* Section headers */
.pr-section-header {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.45rem;
    font-weight: 600;
    color: #1A3A5C;
    border-bottom: 2px solid #C8B99A;
    padding-bottom: 0.4rem;
    margin-top: 2.2rem;
    margin-bottom: 1rem;
}

/* Cards */
.pr-card {
    background-color: #FDFAF4;
    border: 1px solid #DDD4C0;
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
}

/* Pro / Con badges */
.badge-pro {
    display: inline-block;
    background-color: #D4E8D4;
    color: #1A4D1A;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 0.4rem;
    font-family: 'Lora', Georgia, serif;
}
.badge-con {
    display: inline-block;
    background-color: #F0D4D4;
    color: #4D1A1A;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 0.4rem;
    font-family: 'Lora', Georgia, serif;
}
.badge-overlap {
    display: inline-block;
    background-color: #E8E0D0;
    color: #4A3A1A;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 0.4rem;
    font-family: 'Lora', Georgia, serif;
}
.badge-opp {
    display: inline-block;
    background-color: #D4DCF0;
    color: #1A254D;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    margin-bottom: 0.4rem;
    font-family: 'Lora', Georgia, serif;
}

/* Stats row */
.stat-box {
    background-color: #FDFAF4;
    border: 1px solid #DDD4C0;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}
.stat-number {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2rem;
    font-weight: 700;
    color: #1A3A5C;
}
.stat-label {
    font-size: 0.82rem;
    color: #6B6B6B;
    margin-top: 0.2rem;
}

/* Competitor tag */
.comp-tag {
    display: inline-block;
    background-color: #E8EEF5;
    color: #1A3A5C;
    font-size: 0.88rem;
    padding: 4px 12px;
    border-radius: 20px;
    margin: 3px 4px;
    border: 1px solid #B8C8D8;
    font-family: 'Lora', Georgia, serif;
}

/* Progress / status messages */
.status-msg {
    font-family: 'Lora', Georgia, serif;
    font-size: 0.9rem;
    color: #5A5A5A;
    font-style: italic;
    padding: 0.3rem 0;
}

/* Report text */
.report-body {
    font-family: 'Lora', Georgia, serif;
    font-size: 1rem;
    line-height: 1.8;
    color: #2C2C2C;
    white-space: pre-wrap;
}

/* Divider */
.pr-divider {
    border: none;
    border-top: 1px solid #DDD4C0;
    margin: 2rem 0;
}

/* Keyword pill */
.kw-pill {
    display: inline-block;
    background-color: #EDE8DE;
    color: #3A3028;
    font-size: 0.82rem;
    padding: 3px 10px;
    border-radius: 12px;
    margin: 2px 3px;
    font-family: 'Lora', Georgia, serif;
}

/* Chat history bubble */
.chat-user {
    background-color: #1A3A5C;
    color: #FDFAF4;
    border-radius: 16px 16px 4px 16px;
    padding: 0.7rem 1.1rem;
    margin: 0.5rem 0;
    display: inline-block;
    max-width: 80%;
    float: right;
    clear: both;
    font-family: 'Lora', Georgia, serif;
    font-size: 0.95rem;
}
.chat-system {
    background-color: #FDFAF4;
    border: 1px solid #DDD4C0;
    color: #2C2C2C;
    border-radius: 16px 16px 16px 4px;
    padding: 0.7rem 1.1rem;
    margin: 0.5rem 0;
    display: inline-block;
    max-width: 90%;
    float: left;
    clear: both;
    font-family: 'Lora', Georgia, serif;
    font-size: 0.95rem;
}
.chat-clear { clear: both; }
</style>
""", unsafe_allow_html=True)


# ── Pipeline functions (adapted from notebook) ───────────────────────────────

def get_clients(google_key, openai_key, tavily_key):
    youtube       = build('youtube', 'v3', developerKey=google_key)
    openai_client = OpenAI(api_key=openai_key)
    tavily_client = TavilyClient(api_key=tavily_key)
    return youtube, openai_client, tavily_client


def search_youtube_videos(youtube, query, max_results=10):
    response = youtube.search().list(
        q=query, part='snippet', maxResults=max_results,
        type='video', order='relevance'
    ).execute()
    return [{'id': i['id']['videoId'], 'title': i['snippet']['title']}
            for i in response.get('items', [])]


def get_youtube_comments(youtube, video_id, max_comments=100):
    comments, page_token = [], None
    while len(comments) < max_comments:
        params = dict(part='snippet', videoId=video_id,
                      maxResults=min(100, max_comments - len(comments)),
                      order='relevance', textFormat='plainText')
        if page_token:
            params['pageToken'] = page_token
        try:
            resp = youtube.commentThreads().list(**params).execute()
        except Exception:
            break
        for item in resp.get('items', []):
            s = item['snippet']['topLevelComment']['snippet']
            comments.append({'text': s['textDisplay'],
                             'likes': s.get('likeCount', 0),
                             'date':  s.get('publishedAt', '')})
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return comments


def filter_yt_comments(openai_client, comments, product_model, product_category, batch_size=40):
    relevant = []
    for i in range(0, len(comments), batch_size):
        batch = comments[i:i+batch_size]
        numbered = "\n".join([f"{j+1}. {c['text'][:300]}" for j, c in enumerate(batch)])
        prompt = f"""You are filtering YouTube comments for a product analysis of the {product_model} ({product_category}).

Keep a comment ONLY if it:
- Discusses this specific product model or its direct performance as a {product_category}
- Contains genuine user experience (praise, complaint, comparison, suggestion)
- Is in English and is not spam, bot-generated, or irrelevant

Return a JSON array of the 1-based indices of comments to KEEP.
Example: [1, 3, 5]
Return JSON only.

Comments:
{numbered}"""
        try:
            resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            raw = re.sub(r'^```json|^```|```$', '', resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
            indices = json.loads(raw)
            for idx in indices:
                if 1 <= idx <= len(batch):
                    relevant.append(batch[idx-1]['text'])
        except Exception:
            pass
    return relevant


def scrape_web_reviews(tavily_client, openai_client, product_model, product_category, status_fn=None):
    queries = [
        f"{product_model} {product_category} review",
        f"{product_model} {product_category} problems complaints users",
        f"site:reddit.com {product_model} {product_category}",
    ]
    all_pages, all_passages = [], []
    for q in queries:
        if status_fn:
            status_fn(f"Searching: {q[:60]}...")
        try:
            results = tavily_client.search(
                query=q, search_depth="advanced",
                include_raw_content=True, max_results=4
            )
            for r in results.get('results', []):
                content = r.get('raw_content') or r.get('content', '')
                if len(content) > 200:
                    all_pages.append({'url': r.get('url',''), 'source': r.get('url','').split('/')[2] if '//' in r.get('url','') else '', 'content': content[:6000]})
        except Exception as e:
            if status_fn:
                status_fn(f"  Search error: {e}")
        time.sleep(0.5)

    # Filter for relevant passages using OpenAI
    for page in all_pages:
        chunks = [page['content'][i:i+600] for i in range(0, len(page['content']), 600)]
        chunks = [c for c in chunks if len(c) > 150]
        if not chunks:
            continue
        numbered = "\n".join([f"{j+1}. {c}" for j, c in enumerate(chunks[:15])])
        prompt = f"""Filter these text passages from a web page about the {product_model}.
Keep passages that contain genuine user opinion, product feedback, complaints, praise, or comparisons.
Discard navigation text, ads, boilerplate, or irrelevant content.
Return JSON array of 1-based indices to keep. Return JSON only.

Passages:
{numbered}"""
        try:
            resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            raw = re.sub(r'^```json|^```|```$', '', resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
            indices = json.loads(raw)
            for idx in indices:
                if 1 <= idx <= len(chunks[:15]):
                    all_passages.append({'source': page['source'], 'url': page['url'], 'text': chunks[:15][idx-1]})
        except Exception:
            pass

    return all_pages, all_passages


def find_competitors(tavily_client, openai_client, product_model, product_category, num_competitors=3, status_fn=None):
    if status_fn:
        status_fn("Finding competitors by online mention frequency...")
    queries = [
        f"best alternatives to {product_model} {product_category}",
        f"{product_model} vs competitors {product_category}",
        f"top {product_category} competitors to {product_model}",
    ]
    mention_counter = collections.Counter()
    for q in queries:
        try:
            results = tavily_client.search(query=q, search_depth="basic", max_results=5)
            combined_text = " ".join([r.get('content','') for r in results.get('results',[])])
            prompt = f"""From this text, extract the names of specific {product_category} products/models
that are mentioned as alternatives or competitors to the {product_model}.
Return a JSON array of product name strings. Return JSON only.

Text: {combined_text[:3000]}"""
            resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            raw = re.sub(r'^```json|^```|```$', '', resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
            names = json.loads(raw)
            for n in names:
                if isinstance(n, str) and len(n) > 2:
                    mention_counter[n.strip()] += 1
        except Exception:
            pass
        time.sleep(0.3)

    top = [(name, {'frequency': count}) for name, count in mention_counter.most_common(num_competitors)]
    return top


def get_competitor_gaps(openai_client, product_model, top_competitors, all_passages, yt_relevant):
    all_text = " ".join([p['text'] for p in all_passages] + yt_relevant[:50])[:4000]
    comp_names = [n for n, _ in top_competitors]
    prompt = f"""You are analysing what competing {' / '.join(comp_names)} products offer that the {product_model} lacks,
based on user review data below.

For each competitor, identify:
1. Features users praise in the competitor but criticise or miss in the {product_model}
2. Design advantages the competitor has

Return a JSON object where keys are competitor names and values have keys:
'features_we_lack' (list of strings), 'design_advantages' (list of strings)

Return JSON only.

Review data:
{all_text}"""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        raw = re.sub(r'^```json|^```|```$', '', resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception:
        return {}


def run_sentiment(openai_client, texts, batch_size=25):
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        numbered = "\n".join([f"{j+1}. {t[:300]}" for j, t in enumerate(batch)])
        prompt = f"""Classify sentiment of each comment as Positive, Negative, or Neutral.
Return ONLY a JSON array of strings matching the input order.
Example: ["Positive","Negative","Neutral"]

Comments:
{numbered}"""
        try:
            resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            raw = re.sub(r'^```json|^```|```$', '', resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
            batch_s = json.loads(raw)
            if len(batch_s) != len(batch):
                batch_s = (batch_s + ['Neutral']*len(batch))[:len(batch)]
            results.extend(batch_s)
        except Exception:
            results.extend(['Neutral']*len(batch))
        time.sleep(0.3)
    return results


def extract_keywords(openai_client, texts, product_model):
    sample = "\n".join(texts[:80])[:5000]
    prompt = f"""From these user reviews of the {product_model}, extract the 15 most frequently discussed
design-relevant keywords or short phrases (e.g. 'basket coating', 'noise level', 'preheat time').
Focus on physical product attributes, not brand mentions.
Return a JSON array of strings. Return JSON only.

Reviews:
{sample}"""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        raw = re.sub(r'^```json|^```|```$', '', resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception:
        return []


def get_pros_cons(openai_client, texts, product_model, top_n=5):
    sample = "\n".join(texts[:120])[:6000]
    prompt = f"""Analyse these user reviews of the {product_model} and identify the top {top_n} pros and top {top_n} cons.

For each pro and con:
- 'title': short label (3-5 words)
- 'description': one sentence explaining the issue with specific detail
- 'frequency_estimate': estimated number of reviewers who mention this
- 'evidence': one direct quote or paraphrase from the reviews

Rank by frequency (most mentioned first).

Return a JSON object with keys 'pros' and 'cons', each a list of {top_n} objects.
Return JSON only.

Reviews:
{sample}"""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        raw = re.sub(r'^```json|^```|```$', '', resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception:
        return {'pros': [], 'cons': []}


def get_overlaps(openai_client, pros, cons, product_model):
    prompt = f"""Given these pros and cons for the {product_model}, identify features that appear in BOTH lists
(i.e. some users love it, others hate it — a polarising aspect).

Pros: {json.dumps(pros)}
Cons: {json.dumps(cons)}

Return a JSON array of objects with key 'overlap_description' (one sentence).
Return JSON only, empty array if none."""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        raw = re.sub(r'^```json|^```|```$', '', resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception:
        return []


def get_spec_sheet(tavily_client, product_model, product_category):
    try:
        results = tavily_client.search(
            query=f"{product_model} {product_category} specifications official",
            search_depth="advanced", include_raw_content=True, max_results=2
        )
        for r in results.get('results', []):
            content = r.get('raw_content') or r.get('content', '')
            if len(content) > 300:
                return content[:5000]
    except Exception:
        pass
    return ""


def generate_design_opportunities(openai_client, product_model, product_category,
                                   pros, cons, competitor_gaps, top_competitors,
                                   spec_text, keywords):
    comp_names = [n for n, _ in top_competitors]
    comp_block = json.dumps(competitor_gaps, indent=2)[:1500]
    cons_block = json.dumps(cons, indent=2)[:1500]
    spec_block = spec_text[:1500] if spec_text else "Not available."

    prompt = f"""You are a senior product designer preparing a report for a CEO to justify investment in redesigning the {product_model} ({product_category}).

Based on the data below, generate exactly 5 design opportunities. Each must be:
1. Grounded in specific user complaint frequency data
2. SPECIFIC — name exact components, materials, and dimensions where possible
   (e.g. "increase basket depth from 4.2 inches to 5.5 inches" not just "larger basket")
3. Compared against a competitor benchmark (reference one of: {', '.join(comp_names)})
4. Include a sustainability angle (materials reduction, energy efficiency, repairability)
5. Have an INTEREST SCORE (1-10) based on how many users mentioned this issue
6. Have an EFFORT SCORE (1-10) — based on engineering complexity:
   - Material change = 3, Dimension change = 4, New component = 6, Electronics = 8, Full redesign = 9
   State which rule was applied.

TOP CONS (frequency-ranked):
{cons_block}

COMPETITOR GAPS:
{comp_block}

PRODUCT SPEC SHEET:
{spec_block}

DESIGN KEYWORDS FROM REVIEWS:
{', '.join(keywords[:12])}

Return a JSON array of 5 objects with keys:
'title', 'specific_change', 'evidence', 'competitor_benchmark',
'sustainability_note', 'interest_score', 'effort_score', 'effort_justification'

Return JSON only."""

    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        raw = re.sub(r'^```json|^```|```$', '', resp.choices[0].message.content.strip(), flags=re.MULTILINE).strip()
        return json.loads(raw)
    except Exception:
        return []


def plot_priority_matrix(design_opportunities, product_model):
    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor('#F5F0E8')
    ax.set_facecolor('#F5F0E8')

    ax.axhspan(5, 10, xmin=0,   xmax=0.5, alpha=0.07, color='#2A7A2A')
    ax.axhspan(5, 10, xmin=0.5, xmax=1.0, alpha=0.07, color='#1A3A5C')
    ax.axhspan(0, 5,  xmin=0,   xmax=0.5, alpha=0.07, color='#8A7A3A')
    ax.axhspan(0, 5,  xmin=0.5, xmax=1.0, alpha=0.07, color='#8A2A2A')

    ax.axhline(y=5, color='#C8B99A', linestyle='--', linewidth=1, alpha=0.8)
    ax.axvline(x=5, color='#C8B99A', linestyle='--', linewidth=1, alpha=0.8)

    ax.text(2.5, 9.5, 'Quick Wins',        ha='center', fontsize=9, color='#2A7A2A', style='italic')
    ax.text(7.5, 9.5, 'Major Projects',    ha='center', fontsize=9, color='#1A3A5C', style='italic')
    ax.text(2.5, 0.5, 'Low Priority',      ha='center', fontsize=9, color='#8A7A3A', style='italic')
    ax.text(7.5, 0.5, 'Avoid for Now',     ha='center', fontsize=9, color='#8A2A2A', style='italic')

    colours = ['#1A3A5C', '#2A6A4A', '#8A5A1A', '#7A1A1A', '#4A2A7A']

    for i, opp in enumerate(design_opportunities):
        x      = float(opp.get('effort_score', 5))
        y      = float(opp.get('interest_score', 5))
        colour = colours[i % len(colours)]
        jitter = (i - 2) * 0.18

        ax.scatter(x + jitter, y, s=220, color=colour, zorder=5, edgecolors='white', linewidth=1.5)
        ax.text(x + jitter, y, str(i+1), ha='center', va='center', fontsize=8, fontweight='bold', color='white', zorder=6)

        title = opp.get('title', '')[:32] + ('...' if len(opp.get('title','')) > 32 else '')
        ax.annotate(
            f"{i+1}. {title}\n(interest {opp.get('interest_score')}/10)",
            xy=(x + jitter, y), xytext=(10, 6), textcoords='offset points',
            fontsize=7.5, color=colour,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#FDFAF4', edgecolor=colour, alpha=0.9)
        )

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel('Effort to Implement  (1 = Easy, 10 = Very Hard)', fontsize=10, color='#3A3A3A')
    ax.set_ylabel('User Interest Score  (based on comment frequency)', fontsize=10, color='#3A3A3A')
    ax.set_title(f'Design Opportunity Priority Matrix\n{product_model}', fontsize=12, fontweight='bold', color='#1A3A5C', pad=14)
    ax.tick_params(colors='#6B6B6B')
    for spine in ax.spines.values():
        spine.set_color('#C8B99A')

    plt.tight_layout()
    return fig


def generate_final_report(openai_client, product_model, product_category,
                           sentiment_counts, total_comments,
                           pros, cons, overlaps,
                           competitor_gaps, top_competitors,
                           design_opportunities, keywords):
    pos_pct = int(100 * sentiment_counts.get('Positive', 0) / total_comments) if total_comments else 0
    neg_pct = int(100 * sentiment_counts.get('Negative', 0) / total_comments) if total_comments else 0

    pros_block = "\n".join([f"{i+1}. {p['title']} (~{p.get('frequency_estimate','?')} mentions): {p['description']}" for i, p in enumerate(pros)])
    cons_block = "\n".join([f"{i+1}. {c['title']} (~{c.get('frequency_estimate','?')} mentions): {c['description']}" for i, c in enumerate(cons)])
    comp_block = "\n".join([f"- {n} (freq: {d['frequency']}x): lacks {competitor_gaps.get(n,{}).get('features_we_lack',[])} vs us" for n,d in dict(top_competitors).items()])
    opps_block = "\n".join([f"{i+1}. {o.get('title')}: {o.get('specific_change')} [Interest {o.get('interest_score')}/10, Effort {o.get('effort_score')}/10]" for i, o in enumerate(design_opportunities)])

    prompt = f"""Write a professional product design analysis report for the {product_model} ({product_category}).
This will be presented to a CEO to justify investment in product redesign.

DATA:
- Total filtered reviews analysed: {total_comments}
- Sentiment: {pos_pct}% positive, {neg_pct}% negative
TOP PROS: {pros_block}
TOP CONS: {cons_block}
POLARISING OVERLAPS: {[o['overlap_description'] for o in overlaps]}
TOP COMPETITORS (by mention frequency): {[n for n,_ in top_competitors]}
COMPETITOR GAPS: {comp_block}
DESIGN OPPORTUNITIES: {opps_block}

Write a structured report with these sections:
1. Executive Summary (3-4 sentences)
2. User Sentiment Overview
3. Top Strengths
4. Top Weaknesses and Design Pain Points
5. Competitive Positioning
6. Design Opportunities (each with specific change, evidence, competitor benchmark)
7. Recommendation and Priority (justify using interest score / frequency data)

Be specific, evidence-referenced, and persuasive. Business English. Under 1,200 words."""

    resp = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000
    )
    return resp.choices[0].message.content


# ── Session state init ────────────────────────────────────────────────────────
if 'history' not in st.session_state:
    st.session_state.history = []
if 'result' not in st.session_state:
    st.session_state.result = None
if 'analysed_product' not in st.session_state:
    st.session_state.analysed_product = None


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="pr-title">ProductReview</div>', unsafe_allow_html=True)
st.markdown('<div class="pr-subtitle">Enter a product and model name to generate a data-driven design analysis report.</div>', unsafe_allow_html=True)

# ── API Key sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### API Keys")
    st.markdown("*Enter your keys to run the analysis.*")
    google_key = st.text_input("Google API Key", type="password", placeholder="AIza...")
    openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-...")
    st.markdown("---")
    st.markdown("Get free keys at:")
    st.markdown("- [console.cloud.google.com](https://console.cloud.google.com)")
    st.markdown("- [platform.openai.com](https://platform.openai.com)")
    st.markdown("- [tavily.com](https://tavily.com)")

# ── Input row ─────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    product_category = st.text_input("Product Category", placeholder="e.g. air fryer")
with col2:
    product_model = st.text_input("Product Model", placeholder="e.g. Ninja AF161 Max XL")
with col3:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    run_btn = st.button("Analyse")

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not product_category or not product_model:
        st.warning("Please enter both a product category and model name.")
    elif not google_key or not openai_key or not tavily_key:
        st.warning("Please enter all three API keys in the sidebar.")
    else:
        st.session_state.result = None
        st.session_state.analysed_product = f"{product_model} ({product_category})"

        # Status display
        status_placeholder = st.empty()
        progress_bar       = st.progress(0)

        def update_status(msg):
            status_placeholder.markdown(f'<div class="status-msg">{msg}</div>', unsafe_allow_html=True)

        try:
            youtube_c, openai_c, tavily_c = get_clients(google_key, openai_key, tavily_key)

            # Step 1: YouTube
            update_status("Step 1/8 — Searching YouTube for review videos...")
            progress_bar.progress(5)
            videos = search_youtube_videos(youtube_c, f"{product_model} {product_category} review", max_results=10)
            all_raw = []
            for i, v in enumerate(videos):
                update_status(f"Step 1/8 — Fetching comments from video {i+1}/{len(videos)}: {v['title'][:50]}...")
                comments = get_youtube_comments(youtube_c, v['id'], max_comments=300)
                all_raw.extend(comments)
                if len(all_raw) >= 3000:
                    break
                time.sleep(0.3)
            progress_bar.progress(20)

            update_status(f"Step 1/8 — Filtering {len(all_raw)} YouTube comments for relevance...")
            yt_texts = [c['text'] for c in all_raw if len(c['text']) > 30]
            yt_relevant = filter_yt_comments(openai_c, yt_texts, product_model, product_category)
            progress_bar.progress(32)

            # Step 2: Web reviews
            update_status("Step 2/8 — Scraping web reviews via Tavily...")
            all_web_pages, all_web_passages = scrape_web_reviews(
                tavily_c, openai_c, product_model, product_category, update_status
            )
            progress_bar.progress(45)

            # Step 3: Competitors
            update_status("Step 3/8 — Discovering top competitors by mention frequency...")
            top_competitors = find_competitors(tavily_c, openai_c, product_model, product_category)
            competitor_gaps = get_competitor_gaps(openai_c, product_model, top_competitors, all_web_passages, yt_relevant)
            progress_bar.progress(55)

            # Step 4: Spec sheet
            update_status("Step 4/8 — Fetching product specification sheet...")
            spec_text = get_spec_sheet(tavily_c, product_model, product_category)
            progress_bar.progress(60)

            # Step 5: Sentiment + keywords
            update_status("Step 5/8 — Running sentiment analysis...")
            all_texts = yt_relevant + [p['text'] for p in all_web_passages]
            sentiments = run_sentiment(openai_c, all_texts)
            sent_df = pd.DataFrame({'text': all_texts, 'sentiment': sentiments})
            keywords = extract_keywords(openai_c, all_texts, product_model)
            progress_bar.progress(70)

            # Step 6: Pros/Cons
            update_status("Step 6/8 — Identifying top pros and cons by frequency...")
            pc = get_pros_cons(openai_c, all_texts, product_model, top_n=5)
            pros    = pc.get('pros', [])
            cons    = pc.get('cons', [])
            overlaps = get_overlaps(openai_c, pros, cons, product_model)
            progress_bar.progress(80)

            # Step 7: Design opportunities
            update_status("Step 7/8 — Generating specific design opportunities...")
            design_opps = generate_design_opportunities(
                openai_c, product_model, product_category,
                pros, cons, competitor_gaps, top_competitors,
                spec_text, keywords
            )
            progress_bar.progress(88)

            # Step 8: Final report
            update_status("Step 8/8 — Generating executive report...")
            sc = sent_df['sentiment'].value_counts().to_dict()
            final_report = generate_final_report(
                openai_c, product_model, product_category,
                sc, len(sent_df),
                pros, cons, overlaps,
                competitor_gaps, top_competitors,
                design_opps, keywords
            )
            progress_bar.progress(100)
            status_placeholder.empty()
            progress_bar.empty()

            # Store result
            st.session_state.result = {
                'product_model':    product_model,
                'product_category': product_category,
                'yt_count_raw':     len(all_raw),
                'yt_count_filtered':len(yt_relevant),
                'web_pages':        len(all_web_pages),
                'web_passages':     len(all_web_passages),
                'total_analysed':   len(sent_df),
                'sentiment_df':     sent_df,
                'sentiment_counts': sc,
                'keywords':         keywords,
                'pros':             pros,
                'cons':             cons,
                'overlaps':         overlaps,
                'top_competitors':  top_competitors,
                'competitor_gaps':  competitor_gaps,
                'design_opps':      design_opps,
                'final_report':     final_report,
            }

        except Exception as e:
            status_placeholder.empty()
            progress_bar.empty()
            st.error(f"An error occurred: {e}")


# ── Results display ───────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    st.markdown('<hr class="pr-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="pr-title" style="font-size:1.6rem">{r["product_model"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pr-subtitle">{r["product_category"].title()} — Design Opportunity Analysis</div>', unsafe_allow_html=True)

    # ── Data collection stats ─────────────────────────────────────────────────
    st.markdown('<div class="pr-section-header">Data Collected</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{r["yt_count_raw"]}</div><div class="stat-label">YouTube comments scraped</div></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{r["yt_count_filtered"]}</div><div class="stat-label">relevant after AI filter</div></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{r["web_pages"]}</div><div class="stat-label">web pages scraped</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{r["total_analysed"]}</div><div class="stat-label">total reviews analysed</div></div>', unsafe_allow_html=True)

    # ── Sentiment ─────────────────────────────────────────────────────────────
    st.markdown('<div class="pr-section-header">Sentiment Overview</div>', unsafe_allow_html=True)
    sc = r['sentiment_counts']
    total = r['total_analysed']
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        pct = int(100 * sc.get('Positive',0) / total) if total else 0
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#2A7A2A">{pct}%</div><div class="stat-label">Positive</div></div>', unsafe_allow_html=True)
    with sc2:
        pct = int(100 * sc.get('Neutral',0) / total) if total else 0
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#8A7A3A">{pct}%</div><div class="stat-label">Neutral</div></div>', unsafe_allow_html=True)
    with sc3:
        pct = int(100 * sc.get('Negative',0) / total) if total else 0
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="color:#8A2A2A">{pct}%</div><div class="stat-label">Negative</div></div>', unsafe_allow_html=True)

    # ── Keywords ──────────────────────────────────────────────────────────────
    if r['keywords']:
        st.markdown('<div class="pr-section-header">Most Discussed Design Attributes</div>', unsafe_allow_html=True)
        kw_html = " ".join([f'<span class="kw-pill">{k}</span>' for k in r['keywords']])
        st.markdown(kw_html, unsafe_allow_html=True)

    # ── Pros and Cons ─────────────────────────────────────────────────────────
    st.markdown('<div class="pr-section-header">Top Strengths and Weaknesses</div>', unsafe_allow_html=True)
    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown("**Top Strengths**")
        for p in r['pros']:
            freq = p.get('frequency_estimate', '?')
            st.markdown(f"""<div class="pr-card">
<span class="badge-pro">Strength</span>
<strong>{p['title']}</strong> <span style="color:#6B6B6B;font-size:0.82rem">(~{freq} mentions)</span><br>
<span style="font-size:0.92rem">{p.get('description','')}</span><br>
<span style="font-size:0.82rem;color:#6B6B6B;font-style:italic">{p.get('evidence','')}</span>
</div>""", unsafe_allow_html=True)
    with pc2:
        st.markdown("**Top Weaknesses**")
        for c in r['cons']:
            freq = c.get('frequency_estimate', '?')
            st.markdown(f"""<div class="pr-card">
<span class="badge-con">Weakness</span>
<strong>{c['title']}</strong> <span style="color:#6B6B6B;font-size:0.82rem">(~{freq} mentions)</span><br>
<span style="font-size:0.92rem">{c.get('description','')}</span><br>
<span style="font-size:0.82rem;color:#6B6B6B;font-style:italic">{c.get('evidence','')}</span>
</div>""", unsafe_allow_html=True)

    # ── Overlaps ──────────────────────────────────────────────────────────────
    if r['overlaps']:
        st.markdown("**Polarising features** — mentioned by both satisfied and dissatisfied users:")
        for o in r['overlaps']:
            st.markdown(f'<div class="pr-card"><span class="badge-overlap">Polarising</span> {o.get("overlap_description","")}</div>', unsafe_allow_html=True)

    # ── Competitors ───────────────────────────────────────────────────────────
    st.markdown('<div class="pr-section-header">Competitive Positioning</div>', unsafe_allow_html=True)
    comp_html = " ".join([f'<span class="comp-tag">{n} &nbsp;·&nbsp; {d["frequency"]}x mentioned</span>' for n, d in r['top_competitors']])
    st.markdown(f"**Top competitors by online mention frequency:**<br>{comp_html}", unsafe_allow_html=True)

    for comp_name, _ in r['top_competitors']:
        gaps = r['competitor_gaps'].get(comp_name, {})
        lacks = gaps.get('features_we_lack', [])
        advs  = gaps.get('design_advantages', [])
        if lacks or advs:
            st.markdown(f"""<div class="pr-card">
<strong>{comp_name}</strong><br>
<span style="font-size:0.88rem;color:#4D1A1A">Features users miss in our product: {', '.join(lacks) if lacks else 'None identified'}</span><br>
<span style="font-size:0.88rem;color:#1A254D">Design advantages: {', '.join(advs) if advs else 'None identified'}</span>
</div>""", unsafe_allow_html=True)

    # ── Design Opportunities ──────────────────────────────────────────────────
    st.markdown('<div class="pr-section-header">Design Opportunities</div>', unsafe_allow_html=True)
    for i, opp in enumerate(r['design_opps']):
        interest = opp.get('interest_score', '?')
        effort   = opp.get('effort_score', '?')
        st.markdown(f"""<div class="pr-card">
<span class="badge-opp">Opportunity {i+1}</span>
<strong style="font-size:1.05rem">{opp.get('title','')}</strong><br>
<span style="font-size:0.92rem">{opp.get('specific_change','')}</span><br><br>
<span style="font-size:0.85rem;color:#4A4A4A"><strong>Evidence:</strong> {opp.get('evidence','')}</span><br>
<span style="font-size:0.85rem;color:#4A4A4A"><strong>Competitor benchmark:</strong> {opp.get('competitor_benchmark','')}</span><br>
<span style="font-size:0.85rem;color:#4A4A4A"><strong>Sustainability:</strong> {opp.get('sustainability_note','')}</span><br><br>
<span style="font-size:0.82rem;background:#E8EEF5;padding:2px 8px;border-radius:4px;color:#1A3A5C">Interest {interest}/10</span>&nbsp;
<span style="font-size:0.82rem;background:#F0E8D8;padding:2px 8px;border-radius:4px;color:#4A3A1A">Effort {effort}/10 — {opp.get('effort_justification','')}</span>
</div>""", unsafe_allow_html=True)

    # ── Priority Matrix ───────────────────────────────────────────────────────
    st.markdown('<div class="pr-section-header">Priority Matrix</div>', unsafe_allow_html=True)
    st.markdown("Interest score is derived from comment frequency — the more users raised this issue, the higher the score. Effort score is based on engineering complexity using predefined rules stated in each opportunity above.", unsafe_allow_html=False)
    fig = plot_priority_matrix(r['design_opps'], r['product_model'])
    st.pyplot(fig)
    plt.close()

    # ── Full Report ───────────────────────────────────────────────────────────
    st.markdown('<div class="pr-section-header">Full Executive Report</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pr-card report-body">{r["final_report"]}</div>', unsafe_allow_html=True)

    # ── Download button ───────────────────────────────────────────────────────
    st.download_button(
        label="Download Report as Text",
        data=r['final_report'],
        file_name=f"{r['product_model'].replace(' ','_')}_report.txt",
        mime="text/plain"
    )
