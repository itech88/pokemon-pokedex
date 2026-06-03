# Pokédex 📖

A kid-friendly visual Pokédex for all **1,025 Pokémon** (Generations 1–9), built with Streamlit and powered by PokéAPI data.

Features official HD artwork, animated battle sprites, Pokédex flavor text, type-color badges, and stat bars — designed so young Pokémon fans can explore and discover their favourite Pokémon.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app builds its database automatically from the included CSV files on first launch.

## What you can do

- 🔍 **Search** by name
- 🎨 **Filter** by type and generation  
- 🎲 **Surprise me!** — discover a random Pokémon
- 📖 **Click any card** to see full details: artwork, animated battle GIF, Pokédex entry, height, weight, egg groups, and stat bars
- ⭐ Filter to **Legendary & Mythical** Pokémon only

## Deploy to Streamlit Community Cloud

1. Fork this repo on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Point at `app.py` — Streamlit Cloud installs `requirements.txt` automatically

Data from [PokéAPI](https://pokeapi.co/) — free and open.
