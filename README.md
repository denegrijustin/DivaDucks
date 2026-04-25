# 🦆 DivaDucks Flag Football Lineup Optimizer

A complete, production-ready Streamlit app for generating legal, fair, competitive, and coach-friendly flag football lineups using a constraint-based optimizer.

---

## GitHub Setup Checklist

Before pushing, confirm your remote and branch:

1. **Confirm current remote:**
   ```
   git remote -v
   ```
2. **If the remote is wrong, reset it:**
   ```
   git remote set-url origin https://github.com/denegrijustin/DivaDucks.git
   ```
3. **Confirm branch:**
   ```
   git branch
   ```
4. **Push using the correct branch (main):**
   ```
   git push -u origin main --no-verify
   ```
5. **If branch is not main:**
   ```
   git push -u origin YOUR_BRANCH_NAME --no-verify
   ```

> **Important:** Use the standard hyphen (`--no-verify`), not a long dash (`–no-verify`).

---

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open your browser to `http://localhost:8501`.

---

## How to Deploy to Streamlit Community Cloud

1. Push this repository to GitHub: `https://github.com/denegrijustin/DivaDucks.git`
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and sign in with your GitHub account.
3. Click **New app**.
4. Select your repository (`denegrijustin/DivaDucks`), branch (`main`), and main file (`app.py`).
5. Click **Deploy**. Your app will be live in about 60 seconds.

---

## How to Share with Other Coaches

Once deployed, Streamlit Community Cloud gives you a public URL like:
```
https://divaducks.streamlit.app
```
Share this link with other coaches. They can:
- Open the link on any device — no installation required.
- Enter or update the roster directly in the app.
- Adjust player ratings and generate lineups.
- Export PDFs for field use.

---

## How PDF Export Works

PDF generation uses [ReportLab](https://www.reportlab.com/) only. No browser dependency is required. The PDF is created in memory (BytesIO) and delivered via Streamlit's `st.download_button`.

Two PDF types:
- **Full PDF** — Complete lineup tables for all segments, rules check results, player usage table, optimizer score, and notes.
- **Field Card PDF** — Condensed landscape format designed to fit on a 5×8 index card or half-sheet. One row per segment with position labels.

Both use black body text and red headers/borders on a white background.

---

## Lineup Rules

- **7 players on field** at all times (never changes).
- **No player may sit out in two consecutive segments** — this is the primary hard rule.
- Segments alternate: 1H Offense 1 → 1H Defense 1 → 1H Offense 2 → ... → 2H Defense N.
- Sit counts are balanced: every player should sit within 1 of the target sits per game.
- Offense/defense sits are balanced per player when possible.
- Sit-out pairs rotate; the same pair should not sit together more than twice.
- QB rules are respected: locked QB, rotating QB, or group QB modes.

---

## Validation Severity

| Status | Meaning |
|--------|---------|
| ✅ PASS | Rule fully satisfied |
| ⚠️ WARNING | Technically OK but borderline (sit spread of 2, same pair twice, etc.) |
| ❌ FAIL | Hard rule violation — blocks PDF export |

---

## GitHub Push Troubleshooting

**If `git push` fails:**
- Confirm you are on the correct branch: `git branch`
- Confirm remote URL: `git remote -v`
- Try: `git push -u origin main --no-verify`

**If you get 403 Permission Denied:**
- Verify you are logged into the correct GitHub account.
- Verify repository ownership and access at `https://github.com/denegrijustin/DivaDucks`.
- Verify your token or credential manager has push access.
- Verify the origin URL is exactly: `https://github.com/denegrijustin/DivaDucks.git`
- Re-authenticate: `git credential-manager erase` then retry the push.

> **Note:** Always use standard hyphens in `--no-verify`. The long dash `–no-verify` will not work and causes a confusing error.

---

## Project Structure

```
app.py            # Complete single-file Streamlit app
requirements.txt  # Python dependencies
README.md         # This file
.gitignore        # Files excluded from git
```

---

## Default Sample Roster

Katrina, Isla, Timber, Francie, Felicity, Sophia, Quinn, Adriana, Olivia, Maya

All players default to rating 3 on every attribute. Click **Load Sample Roster** in the app to populate the roster instantly.
