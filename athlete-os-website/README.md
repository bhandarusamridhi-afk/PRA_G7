# AthleteOS

**Athlete Performance Intelligence Platform** — one place where athletes and coaches see the *whole athlete*, unifying physical and mental performance data instead of twelve scattered tabs.

Built with [Streamlit](https://streamlit.io). Fully self-contained (synthetic data, no database) so it runs instantly on **Streamlit Community Cloud**.

---

## Features

- **Athlete dashboard** — today's readiness gauge, recovery / sleep / stress / workload KPIs, 45-day trends, sleep-vs-readiness analysis, a mental profile radar, and a 60-second mental check-in.
- **Coach dashboard** — squad readiness comparison, a full squad overview table, mental-vs-physical correlation analytics, and per-athlete flags. **A coach only ever sees athletes from their own sport.**
- **AthleteOS Recommendations** — rule-based, data-backed guidance rendered in highlighted, color-coded cards that "pop" on both dashboards.
- **Modern sporty theme** — electric-blue dark mode, high-contrast bright text, glowing accents, and consistently styled Plotly charts.

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open http://localhost:8501.

---

## Deploy to Streamlit Community Cloud

1. Push this project to a **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, pick your repo/branch, and set the **Main file path** to:
   ```
   streamlit_app.py
   ```
4. Click **Deploy**. Streamlit installs `requirements.txt` automatically — no secrets or environment variables are required.

---

## Demo accounts

All data is synthetic and regenerated deterministically on each load.

### Coaches (password: `coach123`) — each sees only their own sport's squad
| User ID | Sport |
| --- | --- |
| `coach_maria` | Track & Field |
| `coach_david` | Swimming |
| `coach_tara` | Basketball |

### Athletes (password = `<id>123`, e.g. `alex123`)
| Sport | User IDs |
| --- | --- |
| Track & Field | `alex`, `jordan`, `maya`, `sam` |
| Swimming | `lena`, `tom`, `nina` |
| Basketball | `marcus`, `chris`, `andre` |

---

## Project structure

```
streamlit_app.py        # Entry point: login + routing
.streamlit/config.toml  # Electric-blue dark theme
core/
  data.py               # Synthetic data + accounts (same-sport squads)
  recommendations.py    # Rule-based AthleteOS recommendation engine
  theme.py              # CSS, recommendation cards, gauges, chart styling
views/
  athlete.py            # Athlete dashboard
  coach.py              # Coach dashboard
requirements.txt
```
