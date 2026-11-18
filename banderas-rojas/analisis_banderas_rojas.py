"""Banderas rojas en la primera infancia: depuración + descriptivo + predictivo + prescriptivo.

Uso:  python analisis_banderas_rojas.py "Toddler Autism dataset July 2018.csv"
Requiere: pip install pandas numpy matplotlib scikit-learn openpyxl
Genera la carpeta salidas/ con: CSV limpio, CSV predictivo, tabla de ganancia, Excel de tablas y gráficos.
"""
import os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score

ruta = sys.argv[1] if len(sys.argv) > 1 else "Toddler Autism dataset July 2018.csv"
OUT = "salidas"; os.makedirs(f"{OUT}/graficos", exist_ok=True)
ITEMS = [f"A{i}" for i in range(1, 11)]

# ---------- 1. Depuración ----------
df = pd.read_csv(ruta)
df.columns = (df.columns.str.strip().str.replace(r"[-/ ]", "_", regex=True)
              .str.replace("Who_completed_the_test", "Who_completed_test"))
for c in ["Sex", "Ethnicity", "Jaundice", "Family_mem_with_ASD", "Who_completed_test"]:
    df[c] = df[c].astype(str).str.strip().str.lower()
df["Sex"] = df["Sex"].map({"f": "Femenino", "m": "Masculino"})
for c in ["Jaundice", "Family_mem_with_ASD"]:
    df[c] = df[c].map({"yes": "Sí", "no": "No"})
n_et = df["Ethnicity"].value_counts()
raras = list(n_et[n_et < 30].index) + ["others"]
df["Etnia_agrupada"] = df["Ethnicity"].where(~df["Ethnicity"].isin(raras), "otras / mixtas")
df["Total_banderas"] = df[ITEMS].sum(axis=1)
df["Alerta"] = (df["Total_banderas"] > 3).astype(int)          # regla del Q-CHAT-10
df["Grupo_edad"] = pd.cut(df["Age_Mons"], [11, 17, 23, 29, 36],
                          labels=["12-17", "18-23", "24-29", "30-36"])
print(f"Filas: {len(df)} | nulos: {int(df.isna().sum().sum())} | "
      f"duplicados exactos: {int(df.duplicated().sum())}")
df.to_csv(f"{OUT}/toddlers_limpio.csv", index=False, encoding="utf-8-sig")

# ---------- 2. Descriptivo ----------
tablas = {"Cuantitativas": df[["Age_Mons", "Total_banderas"]].agg(["mean", "median", "std", "min", "max"]).T.round(2).reset_index()}
tablas["Indicadores"] = (df[ITEMS].mean() * 100).round(1).sort_values(ascending=False).rename("% con bandera").reset_index()
for c in ["Grupo_edad", "Sex", "Jaundice", "Family_mem_with_ASD", "Etnia_agrupada"]:
    t = df.groupby(c, observed=True)["Alerta"].agg(Ninos="size", En_alerta="sum")
    t["% en alerta"] = (t.En_alerta / t.Ninos * 100).round(1)
    tablas[f"Alerta_por_{c}"] = t.reset_index()
tablas["Alerta_por_Grupo_edad"].plot.bar(x="Grupo_edad", y="% en alerta", legend=False, color="#d1495b")
plt.ylabel("% en alerta"); plt.tight_layout(); plt.savefig(f"{OUT}/graficos/alerta_por_edad.png", dpi=150); plt.close()
(df[ITEMS].mean() * 100).sort_values().plot.barh(color="#2f6fdb")
plt.xlabel("% con bandera"); plt.tight_layout(); plt.savefig(f"{OUT}/graficos/indicadores.png", dpi=150); plt.close()

# ---------- 3. Predictivo (solo perfil; sin A1..A10 porque el puntaje sale de ellos) ----------
X = pd.get_dummies(df[["Sex", "Jaundice", "Family_mem_with_ASD", "Etnia_agrupada"]]).astype(float)
z = (df["Age_Mons"] - df["Age_Mons"].mean()) / df["Age_Mons"].std()
X["Age"], X["Age2"] = z, z ** 2
y = df["Alerta"].values
p = cross_val_predict(LogisticRegression(max_iter=3000), X, y,
                      cv=StratifiedKFold(5, shuffle=True, random_state=42), method="predict_proba")[:, 1]
auc = roc_auc_score(y, p)
print(f"AUC (validación cruzada): {auc:.3f} | exactitud: {((p > .5) == y).mean():.3f} | base: {max(y.mean(), 1 - y.mean()):.3f}")
df["Prob_alerta_modelo"] = p.round(4)
df["Nivel_riesgo_modelo"] = pd.qcut(p, 3, labels=["Bajo", "Medio", "Alto"])

# ---------- 4. Prescriptivo ----------
df["Nivel_priorizacion"] = pd.cut(df["Total_banderas"], [-1, 3, 5, 7, 10],
    labels=["1 Seguimiento rutinario (0-3)", "2 Observación reforzada (4-5)",
            "3 Valoración prioritaria (6-7)", "4 Derivación urgente (8-10)"])
tablas["Niveles_priorizacion"] = df["Nivel_priorizacion"].value_counts().sort_index().rename("Niños").reset_index()
d = df.sort_values("Prob_alerta_modelo", ascending=False).reset_index(drop=True)
d["dec"] = d.index * 10 // len(d)
g = d.groupby("dec").agg(n=("Alerta", "size"), alertas=("Alerta", "sum"))
g["pct_pob"] = (g.n.cumsum() / len(d)).round(3)
g["capt"] = (g.alertas.cumsum() / d.Alerta.sum()).round(3)
g.reset_index().to_csv(f"{OUT}/tabla_ganancia.csv", index=False)
plt.plot(g.pct_pob, g.capt, color="#d1495b", label="Modelo de perfil")
plt.plot([0, 1], [0, 1], "--", color="gray", label="Azar")
plt.xlabel("% de niños priorizados"); plt.ylabel("% de alertas captadas"); plt.legend()
plt.tight_layout(); plt.savefig(f"{OUT}/graficos/curva_ganancia.png", dpi=150); plt.close()

# ---------- 5. Exportar ----------
df.to_csv(f"{OUT}/toddlers_predictivo.csv", index=False, encoding="utf-8-sig")
with pd.ExcelWriter(f"{OUT}/tablas_descriptivas.xlsx") as xw:
    for nombre, t in tablas.items():
        t.to_excel(xw, sheet_name=nombre[:31], index=False)
print(f"Listo: revisa la carpeta {OUT}/")
