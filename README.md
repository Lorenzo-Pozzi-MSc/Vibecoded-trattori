# AgriSelector 🚜

Desktop app (PySide6) to match tractors and agricultural implements from Excel databases.

## Setup

```bash
pip install -r requirements.txt
```

Place your Excel files in the project root **or** in the `data/` folder:
- `DB trattori.xlsx`
- `DB macchine.xlsx`

## Run

```bash
python app.py
```

Or press ▶ in VS Code (requires `.vscode/launch.json` — see below).

## VS Code play-button setup

Create `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "AgriSelector",
            "type": "debugpy",
            "request": "launch",
            "program": "app.py"
        }
    ]
}
```

## Project structure

```
agri-selector/
├── app.py                  ← entry point
├── requirements.txt
├── data/
│   └── loader.py           ← Excel loading
├── logic/
│   └── matcher.py          ← filtering + scoring (pure pandas, no UI)
└── ui/
    ├── styles.py            ← all QSS
    ├── filter_panel.py      ← left sidebar
    ├── results_panel.py     ← right results area
    └── main_window.py       ← top-level window
```
