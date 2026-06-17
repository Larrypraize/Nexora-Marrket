# 🚀 NEXORA MARKET — Deploy It Yourself (No Coding) — START HERE

Follow these steps in order. Only a web browser is needed. ~30–45 min first time.

There are 5 parts:
- PART A: Create free accounts
- PART B: Put your project on GitHub
- PART C: Deploy it (get your live link)
- PART D: Get your API keys (for real data)
- PART E: Add the keys to make data live

Keep an AI chatbot (ChatGPT/Claude) open in another tab. If ANY screen looks
different or shows an error, screenshot it and ask the AI: "I have no coding
experience, what do I click next?"

================================================================
PART A — CREATE FREE ACCOUNTS (5 min)
================================================================
1. Open a browser tab → go to  github.com  → click **Sign up**.
   - Enter email, password, pick a username, verify your email.
2. Open a new tab → go to  render.com  → click **Get Started**.
   - Choose **"GitHub"** to sign in (this links the two accounts). Approve access.

✅ You now have GitHub + Render, connected.

================================================================
PART B — PUT YOUR PROJECT ON GITHUB (10 min)
================================================================
You have the file **nexora-market-handoff.zip**.

1. **Unzip it**: double-click the zip. You now have a folder named
   **nexora-market** containing files like `index.html`, `backend`, `render.yaml`.
2. Go to  github.com  → click the **➕** at the top-right → **New repository**.
3. Repository name: type  nexora-market
4. Leave everything else as default → click the green **Create repository**.
5. On the next page, find the small link that says
   **"uploading an existing file"** → click it.
6. Open your **nexora-market** folder. Select **everything inside it**
   (Ctrl+A on Windows / Cmd+A on Mac), then **drag** it all into the big upload
   box on GitHub.
   - ⏳ Wait until all file names finish appearing.
7. Scroll down → click the green **Commit changes** button.

✅ Your project is now on GitHub.

> Tip: if drag-and-drop is fussy, use the "choose your files" link instead and
> select all the files. Make sure the `backend` folder and `render.yaml` are
> included.

================================================================
PART C — DEPLOY IT / GET YOUR LIVE LINK (10 min)
================================================================
1. Go to  render.com  → you'll land on the **Dashboard**.
2. Click **New +** (top-right) → choose **Blueprint**.
3. Find **nexora-market** in the repo list → click **Connect**.
   - (If asked, give Render permission to see your GitHub repos.)
4. Render reads the `render.yaml` file and shows a service named
   **nexora-market**. Click **Apply** (or **Create / Deploy**).
5. ⏳ Wait 3–5 minutes. You'll see logs scrolling — that's normal building.
6. When the status turns to **Live**, click the link near the top. It looks like:
   **https://nexora-market.onrender.com**

🎉 THAT LINK IS YOUR LIVE WEBSITE. Open it, share it — it works on phone & desktop.

> At this point the site shows clearly-labeled DEMO data. That's expected.
> Do Parts D & E to switch on real market data.

================================================================
PART D — GET YOUR FREE API KEYS (10–15 min)
================================================================
Each provider gives a free key after a quick signup. Get as many as you want —
even 1–2 makes parts of the site show real data. Copy each key into a notes file
temporarily.

1) FINNHUB  (stock prices)
   - Go to  finnhub.io  → **Sign up** (free) → verify email.
   - After login you land on the **Dashboard**; your **API key** is shown there.
   - Click **Copy**. Save it as: FINNHUB = <your key>

2) FINANCIAL MODELING PREP / FMP  (movers, sectors)
   - Go to  site.financialmodelingprep.com  → **Sign up** (free).
   - Open your **Dashboard** → find **API Keys** → copy the key.
   - Save it as: FMP = <your key>

3) ALPHA VANTAGE  (prices + news sentiment)
   - Go to  alphavantage.co  → click **Get Free API Key**.
   - Fill the short form → it shows your key on screen instantly.
   - Save it as: ALPHA = <your key>

4) TWELVE DATA  (prices, charts)
   - Go to  twelvedata.com  → **Sign up** (free).
   - Go to your **Dashboard / API Keys** → copy the key.
   - Save it as: TWELVE = <your key>

5) MARKETAUX  (financial news)
   - Go to  marketaux.com  → **Sign up** (free).
   - Open your **Dashboard** → copy the **API Token**.
   - Save it as: MARKETAUX = <your key>

6) (OPTIONAL) OPENAI  (smarter AI answers; otherwise built-in AI is used)
   - Go to  platform.openai.com  → sign up → **API keys** → **Create new key**.
   - Save it as: LLM = <your key>   (note: this one may require adding credit)

> 🔐 These keys are like passwords. Don't share them or post them publicly.

================================================================
PART E — ADD KEYS SO DATA GOES LIVE (5 min)
================================================================
1. In  render.com  → open your **nexora-market** service.
2. In the left menu, click **Environment**.
3. You'll see a list of variable NAMES already there. For each, click into the
   value box and paste the matching key you saved:
      FINNHUB_API_KEY        → paste FINNHUB
      FMP_API_KEY            → paste FMP
      ALPHA_VANTAGE_API_KEY  → paste ALPHA
      TWELVE_DATA_API_KEY    → paste TWELVE
      MARKETAUX_API_KEY      → paste MARKETAUX
      LLM_API_KEY            → paste LLM  (optional)
   (Skip any you didn't get — the site still works.)
4. Click **Save Changes**.
5. ⏳ Render restarts automatically (~1 min). Refresh your website link.

✅ Your site now shows REAL market data. A "Live data" badge appears.

================================================================
DONE! WHAT NOW?
================================================================
- Your link: the https://...onrender.com address from Part C.
- To check it's healthy, visit:  <your link>/health
- To see the developer API docs, visit:  <your link>/docs

UPDATING LATER:
- Change a file on GitHub → Render automatically redeploys. That's it.

COST:
- GitHub: free.  Render: free tier works (free apps "sleep" when idle and take
  ~30 sec to wake on the next visit; ~$7/month keeps it always awake).
- All 5 data APIs have free tiers.

================================================================
🆘 IF YOU GET STUCK (your AI helper)
================================================================
Copy the error or take a screenshot, then paste into ChatGPT/Claude with:

  "I'm deploying a FastAPI project on Render using a render.yaml blueprint.
   I have NO coding experience. Here is what I see: [paste/screenshot].
   Tell me exactly what to click next."

Examples it can solve instantly:
  - "Build failed" → it reads the log and tells you the fix.
  - "I can't find the Environment tab" → step-by-step clicks.
  - "My site shows demo data" → reminds you to add keys (Parts D & E).
