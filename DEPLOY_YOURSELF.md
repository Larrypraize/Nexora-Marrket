# 🚀 Deploy NEXORA MARKET Yourself — No Coding Needed

This guide gets your website **live on the internet** with a real link, using only
your web browser. No terminal, no code. Plan ~30–45 minutes the first time.

You'll use 3 free tools:
1. **GitHub** — stores your project files online.
2. **Render.com** — runs the project and gives you a public link.
3. **An AI chatbot** (ChatGPT/Claude/etc.) — your on-demand helper if anything
   looks confusing. Copy any error message to it and ask "what do I do?"

> 💡 The project already includes a file called `render.yaml` that tells Render
> exactly how to run everything. That's why this is so simple.

---

## STEP 1 — Create free accounts (5 min)
1. Go to **github.com** → Sign up (free).
2. Go to **render.com** → click **"Get Started"** → choose **"Sign in with GitHub"**
   (this links the two automatically).

---

## STEP 2 — Put the project on GitHub (10 min)
You have the file `nexora-market-handoff.zip`. **Unzip it first** (double-click it)
so you have a folder called `nexora-market`.

1. On github.com, click the **➕ (top right) → New repository**.
2. Name it `nexora-market`. Leave everything else default. Click
   **Create repository**.
3. On the next page, click the link **"uploading an existing file"**.
4. Open your unzipped `nexora-market` folder, select **ALL** the files and folders
   inside it, and **drag them** into the GitHub upload box.
   - Wait for them to finish uploading (you'll see file names appear).
5. Scroll down, click the green **"Commit changes"** button.

✅ Your code now lives on GitHub.

---

## STEP 3 — Deploy on Render (10 min)
1. Go to **render.com** dashboard → click **"New +"** (top right) → **"Blueprint"**.
2. Select your **`nexora-market`** repository from the list → click **Connect**.
3. Render reads `render.yaml` automatically and shows a service called
   **nexora-market**. Click **"Apply"** / **"Create"**.
4. Wait ~3–5 minutes while it builds (you'll see logs scrolling — that's normal).
5. When it says **"Live"**, click the URL at the top
   (looks like `https://nexora-market.onrender.com`).

🎉 **That link is your live website. Share it with anyone.**

---

## STEP 4 — Add your API keys for REAL market data (10 min)
The site works immediately, but shows **demo data** until you add keys.
Get free API keys (sign up on each site, copy the key):

| Service | Where to get a free key |
|---|---|
| Finnhub | finnhub.io |
| Financial Modeling Prep | financialmodelingprep.com |
| Alpha Vantage | alphavantage.co |
| Twelve Data | twelvedata.com |
| MarketAux | marketaux.com |
| (Optional) AI replies | platform.openai.com |

Then in Render:
1. Open your **nexora-market** service → click **"Environment"** (left menu).
2. For each key, the variable name is already listed. Click **"Edit"**, paste your
   key value next to the matching name, e.g.:
   - `FINNHUB_API_KEY` → *paste your Finnhub key*
   - `FMP_API_KEY` → *paste your FMP key*
   - `ALPHA_VANTAGE_API_KEY`, `TWELVE_DATA_API_KEY`, `MARKETAUX_API_KEY` → same idea
   - `LLM_API_KEY` → *(optional)* your OpenAI key for smarter AI answers
3. Click **"Save Changes"**. Render restarts automatically (~1 min) with live data.

> You can add keys one at a time — you don't need all of them. Even one or two
> makes parts of the site show real data.

---

## ✅ You're done!
- Your website: the `https://...onrender.com` link from Step 3.
- To update the site later: change files on GitHub → Render redeploys automatically.

---

## 🆘 If you get stuck (use AI as your helper)
Whatever goes wrong, do this:
1. **Copy** the error text or describe what you see (a screenshot helps).
2. Paste it into ChatGPT/Claude and say:
   > "I'm deploying a FastAPI project on Render using a render.yaml blueprint.
   > Here's what I see: [paste]. I have no coding experience — tell me exactly
   > what to click."
3. Follow the steps it gives you.

Common things AI can walk you through:
- "Render says build failed" → it'll read the log and tell you the fix.
- "How do I find the Environment tab?" → step-by-step clicks.
- "My link shows demo data" → reminds you to add API keys (Step 4).

---

## 💸 Cost
- GitHub: free.
- Render: free tier works (note: free services **sleep after inactivity** and take
  ~30 sec to wake on the next visit). Upgrading to ~$7/month keeps it always-on.
- API keys: all have **free tiers** — fine for testing and light use.

---

## 🔁 Alternative one-click hosts (if you prefer)
The same GitHub repo also works on **Railway.app** and **Fly.io** — both let you
"deploy from GitHub." Render is the most beginner-friendly, so start there.
