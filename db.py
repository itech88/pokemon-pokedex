import duckdb
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DB_PATH  = Path(__file__).parent / "pokemon.duckdb"

TYPE_COLORS = {
    "Normal":"#A8A77A","Fire":"#EE8130","Water":"#6390F0","Electric":"#F7D02C",
    "Grass":"#7AC74C","Ice":"#96D9D6","Fighting":"#C22E28","Poison":"#A33EA1",
    "Ground":"#E2BF65","Flying":"#A98FF3","Psychic":"#F95587","Bug":"#A6B91A",
    "Rock":"#B6A136","Ghost":"#735797","Dragon":"#6F35FC","Dark":"#705746",
    "Steel":"#B7B7CE","Fairy":"#D685AD",
}

TYPE_ORDER = [
    "Normal","Fire","Water","Electric","Grass","Ice","Fighting","Poison",
    "Ground","Flying","Psychic","Bug","Rock","Ghost","Dragon","Dark","Steel","Fairy",
]


def _build(db_path: Path) -> None:
    con = duckdb.connect(str(db_path))
    pokemon_csv  = str(DATA_DIR / "pokemon_data.csv")
    pokedex_csv  = str(DATA_DIR / "pokedex_data.csv")

    con.execute("DROP TABLE IF EXISTS raw_pokemon CASCADE")
    con.execute("DROP TABLE IF EXISTS raw_pokedex  CASCADE")

    con.execute(f"CREATE TABLE raw_pokemon AS SELECT * FROM read_csv_auto('{pokemon_csv}', header=true)")
    con.execute(f"CREATE TABLE raw_pokedex  AS SELECT * FROM read_csv_auto('{pokedex_csv}',  header=true)")

    con.execute("DROP VIEW IF EXISTS pokemon_base")
    con.execute("""
        CREATE VIEW pokemon_base AS
        SELECT *, HP+Attack+Defense+SpAtk+SpDef+Speed AS TotalStats,
               Name LIKE '%(%' AS IsForm
        FROM raw_pokemon
    """)

    con.execute("DROP VIEW IF EXISTS pokedex_full")
    con.execute("""
        CREATE VIEW pokedex_full AS
        SELECT p.Number, p.Name, p.Type1, p.Type2,
               p.HP, p.Attack, p.Defense, p.SpAtk, p.SpDef, p.Speed, p.TotalStats,
               p.Generation, p.Legendary,
               d.HeightM, d.WeightKg, d.ArtworkURL, d.AnimatedGifURL,
               d.CaptureRate, d.Genus, d.FlavorText,
               d.EggGroup1, d.EggGroup2, d.Habitat, d.GrowthRate
        FROM pokemon_base p
        LEFT JOIN raw_pokedex d ON d.Number = p.Number
        WHERE p.IsForm = false
    """)
    con.execute("CHECKPOINT")
    con.close()


@st.cache_resource
def get_con():
    if not DB_PATH.exists():
        _build(DB_PATH)
    return duckdb.connect(str(DB_PATH), read_only=True)
