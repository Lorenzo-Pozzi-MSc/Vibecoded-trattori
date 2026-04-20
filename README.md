# AgriSelector 🚜

Match tractors and agricultural implements from your Excel databases.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place your Excel files in the project root OR in data/
#    - "DB trattori.xlsx"
#    - "DB macchine.xlsx"

# 3. Run the app
streamlit run app.py
```

## Project structure

```
agri-selector/
├── app.py               ← Streamlit entry point
├── requirements.txt
├── data/
│   ├── loader.py        ← Excel loading + caching
│   ├── DB trattori.xlsx ← (you provide)
│   └── DB macchine.xlsx ← (you provide)
├── logic/
│   └── matcher.py       ← Filtering + scoring engine
└── ui/
    ├── styles.py        ← Custom CSS
    ├── sidebar.py       ← Filter widgets
    └── results.py       ← Card + table rendering
```

## How matching works

Filters are split into two tiers:

| Tier | Behaviour |
|------|-----------|
| **Hard** | Rows that fail are excluded from results |
| **Soft** | Rows that fail lose score points, but aren't excluded |

Every result shows a **% score** (top-right badge) indicating what fraction of active soft criteria it satisfies. Results are sorted by score descending.

## Extending the logic

All matching is in `logic/matcher.py`. Each filter is a clearly labelled section — add new hard or soft criteria by following the same pattern.
