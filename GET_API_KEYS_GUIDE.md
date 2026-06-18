# 🔑 How to Get Your Free API Keys — Step by Step

An "API key" is a free password-like code each data company gives you so your
website can pull their data. You'll get one from each provider below.

**Before you start:** open a blank notes file (Notepad / Notes app). Each time you
copy a key, paste it there with a label, like:
    FINNHUB = abc123yourkey
    FMP = def456yourkey
You'll paste these into Render later (see START_HERE_DEPLOY_GUIDE.md, Part E).

⏱️ Total time: ~10–15 minutes for all five.
🔐 Keep these keys private — treat them like passwords.

================================================================
0) NGX PULSE  — Nigerian stocks (MOST IMPORTANT for this platform)
================================================================
This is what powers all the Nigerian (NGX) stock data — prices, gainers/losers,
sectors. Get this one first.
1. Go to:  https://ngxpulse.ng/api
2. Scroll to the "Request Access" / API key form.
3. Choose the **Personal / Learning** tier (free, issued instantly).
4. Enter your email → submit → you receive your **API key**.
5. Copy it. In your notes file write:  NGX = <paste here>
   (Free tier = 100 requests/day, which is fine because the app caches data.)

================================================================
1) FINNHUB  — US stock prices
================================================================
1. Go to:  https://finnhub.io
2. Click **Get free API key** (or **Sign up**) at the top.
3. Enter your email + password → submit. Verify your email if asked.
4. After you log in, you land on the **Dashboard**.
5. You'll see a box labeled **API Key** with a code and a **Copy** button.
6. Click **Copy**.
7. In your notes file write:  FINNHUB = <paste here>

================================================================
2) FINANCIAL MODELING PREP (FMP)  — market movers & sectors
================================================================
1. Go to:  https://site.financialmodelingprep.com
2. Click **Sign Up** (top right) → create a free account → verify email.
3. Log in. Click your account/**Dashboard**.
4. Find the section called **API Keys** (or "API Dashboard").
5. Your key is shown there — click to **Copy** it.
6. In your notes file write:  FMP = <paste here>

================================================================
3) ALPHA VANTAGE  — prices + news sentiment  (easiest, instant)
================================================================
1. Go to:  https://www.alphavantage.co/support/#api-key
2. Fill the short form (pick "Investor" or "Software Developer", enter your
   email, organization can be anything like "Personal").
3. Click **GET FREE API KEY**.
4. Your key appears **right on the screen** instantly.
5. Copy it. In your notes file write:  ALPHA = <paste here>

================================================================
4) TWELVE DATA  — prices & charts
================================================================
1. Go to:  https://twelvedata.com
2. Click **Get Free API Key** / **Sign Up** → create account → verify email.
3. Log in — you arrive at your **Dashboard**.
4. Your **API Key** is shown on the dashboard (often under "API Keys").
5. Click **Copy**.
6. In your notes file write:  TWELVE = <paste here>

================================================================
5) MARKETAUX  — financial news
================================================================
1. Go to:  https://www.marketaux.com
2. Click **Sign Up** / **Get Free API Token** → create account → verify email.
3. Log in → open your **Dashboard**.
4. Find your **API Token** → click **Copy**.
5. In your notes file write:  MARKETAUX = <paste here>

================================================================
6) (OPTIONAL) OPENAI  — smarter AI answers
================================================================
You can SKIP this — the site has a built-in AI that works without it. Add this
only if you want more conversational AI replies. Note: OpenAI may ask you to add
a small amount of credit (a few dollars).
1. Go to:  https://platform.openai.com
2. Sign up / log in.
3. Click your profile (top right) → **View API keys** (or go to
   platform.openai.com/api-keys).
4. Click **Create new secret key** → **Copy** it immediately (it's only shown
   once!).
5. In your notes file write:  LLM = <paste here>

================================================================
✅ WHAT NOW
================================================================
You should have a notes file like:
    FINNHUB = ...
    FMP = ...
    ALPHA = ...
    TWELVE = ...
    MARKETAUX = ...
    LLM = ...   (optional)

Next: open START_HERE_DEPLOY_GUIDE.md → **Part E** and paste each key into the
matching box on Render:
    NGX_API_KEY            ← NGX  (Nigerian stocks — most important)
    FINNHUB_API_KEY        ← FINNHUB
    FMP_API_KEY            ← FMP
    ALPHA_VANTAGE_API_KEY  ← ALPHA
    TWELVE_DATA_API_KEY    ← TWELVE
    MARKETAUX_API_KEY      ← MARKETAUX
    LLM_API_KEY            ← LLM (optional)

You don't need ALL of them — even one or two will make parts of the site show
real data. The site also works with NO keys (it shows clearly-labeled demo data).

================================================================
🆘 STUCK?
================================================================
If a website looks different than described (they redesign sometimes), paste this
into ChatGPT/Claude:
   "I signed up on [website name]. I have no coding experience. Where do I find
    and copy my free API key? Walk me through the exact clicks."

Common notes:
- Didn't get a verification email? Check spam, or resend from the login page.
- Free tiers have limits (e.g. a max number of requests per minute/day). That's
  fine for testing and normal use.
- A key looks like a random string of letters/numbers — copy the WHOLE thing, no
  spaces.
