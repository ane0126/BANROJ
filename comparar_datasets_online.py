"""Compara en línea el dataset de toddlers con los datasets de autismo de UCI.

Requiere internet:  pip install ucimlrepo pandas
Uso:  python comparar_datasets_online.py "Toddler Autism dataset July 2018.csv"
Genera comparacion_datasets.csv. La parte de descarga depende de tu conexión.
"""
import sys
import pandas as pd
from ucimlrepo import fetch_ucirepo

RUTA = sys.argv[1] if len(sys.argv) > 1 else "Toddler Autism dataset July 2018.csv"
UCI = {"Niños (UCI 419)": 419, "Adolescentes (UCI 420)": 420, "Adultos (UCI 426)": 426}
A = [f"A{i}" for i in range(1, 11)]
filas = []

td = pd.read_csv(RUTA)
td.columns = td.columns.str.strip()
filas.append({
    "Dataset": "Toddlers (Kaggle, precargado)", "Filas": len(td),
    "Edad media (años)": round(td["Age_Mons"].mean() / 12, 1),
    "Puntaje medio": round(td[A].sum(axis=1).mean(), 2),
    "% alerta (etiqueta)": round((td["Class/ASD Traits"].astype(str).str.strip().str.lower() == "yes").mean() * 100, 1),
    "Nulos": int(td.isna().sum().sum()),
})

for nombre, ident in UCI.items():
    try:
        d = fetch_ucirepo(id=ident).data.original
        score_cols = [c for c in d.columns if c.endswith("_Score")]
        clase = [c for c in d.columns if c.lower().startswith("class")][0]
        filas.append({
            "Dataset": nombre, "Filas": len(d),
            "Edad media (años)": round(pd.to_numeric(d["age"], errors="coerce").mean(), 1),
            "Puntaje medio": round(d[score_cols].sum(axis=1).mean(), 2),
            "% alerta (etiqueta)": round((d[clase].astype(str).str.upper() == "YES").mean() * 100, 1),
            "Nulos": int(d.isna().sum().sum()),
        })
    except Exception as e:  # sin internet, cambio de formato, etc.
        print(f"No se pudo descargar {nombre}: {e}")

res = pd.DataFrame(filas)
# Misma regla de decisión que el tablero: fuente más adecuada a primera infancia, con etiqueta coherente
print(res.to_string(index=False))
res.to_csv("comparacion_datasets.csv", index=False, encoding="utf-8-sig")
print("\nDecisión: se mantiene el dataset de toddlers (único de primera infancia, 12 a 36 meses).")
