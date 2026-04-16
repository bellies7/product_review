# ProductReview — Web App

A product design analysis tool that scrapes YouTube and web reviews to generate data-driven design opportunities.

## How to deploy (free, shareable link in 5 minutes)

### Step 1 — Upload to GitHub
1. Go to github.com and create a new **public** repository called `productreview`
2. Upload these two files: `app.py` and `requirements.txt`

### Step 2 — Deploy on Streamlit Community Cloud
1. Go to share.streamlit.io and sign in with your GitHub account
2. Click **New app**
3. Select your `productreview` repository
4. Set **Main file path** to `app.py`
5. Click **Deploy**

Streamlit will give you a public URL like:
`https://yourname-productreview-app-xxxx.streamlit.app`

Share this link with your teammates — no installation needed on their end.

## API Keys needed
- **Google API Key** — console.cloud.google.com (enable YouTube Data API v3)
- **OpenAI API Key** — platform.openai.com
- **Tavily API Key** — tavily.com (free tier: 1000 searches/month)

Keys are entered in the sidebar when running the app. They are never stored.

## Local development
```
pip install -r requirements.txt
streamlit run app.py
```
