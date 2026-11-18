# BanderasRojas · Banderas rojas y alteraciones emocionales en la primera infancia

Proyecto de Aula «Analítica de Datos para la Transformación Social».
Tablero web con analítica **descriptiva, diagnóstica, predictiva y prescriptiva** sobre 1.054 cuestionarios
Q-CHAT-10 (niños de 12 a 36 meses). Es un tamizaje: una alerta indica derivar a valoración, no diagnostica.

## Contenido

| Archivo | Qué es |
|---|---|
| `index.html` | El tablero completo (un solo archivo, sin servidor). Trae el dataset precargado. |
| `analisis_banderas_rojas.py` | Python: depuración, descriptivo, predictivo y prescriptivo; genera `salidas/`. |
| `comparar_datasets_online.py` | Python: descarga datasets de UCI y los compara con el de toddlers. |
| `data/` | Dataset original (Thabtah, 2018, Kaggle). |

## Usar la web

1. Abre `index.html` en el navegador (o la URL publicada).
2. Menú **Recolección y depuración → Agregar datos (formulario)** para sumar casos nuevos sin CSV.
3. El botón **Subir otro CSV** (al final de la página «Dataset») permite cargar otro archivo.

> Los casos del formulario se guardan **solo en el navegador de quien los escribe** (`localStorage`);
> no se comparten entre visitantes. Para conservarlos, usa **Descargar CSV completo**.
> No escribas datos que identifiquen a un niño.

## Ejecutar el análisis en Python

```bash
pip install pandas numpy matplotlib scikit-learn openpyxl
python analisis_banderas_rojas.py data/Toddler_Autism_dataset_July_2018.csv
```

## Subir a GitHub y publicar con GitHub Pages

```bash
git init
git add .
git commit -m "Primera versión del tablero de banderas rojas"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/banderas-rojas.git
git push -u origin main
```

Luego, en GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch →
Branch: `main` / `(root)` → Save**. En uno o dos minutos queda en:
`https://TU_USUARIO.github.io/banderas-rojas/`

## Créditos y referencias

- Thabtah, F. (2018). *Autism screening data for toddlers* [Conjunto de datos]. Kaggle.
- Fayyad, U., Piatetsky-Shapiro, G., & Smyth, P. (1996). From data mining to knowledge discovery in databases. *AI Magazine, 17*(3), 37–54.

Integrantes: [nombres del equipo] · Docente: [nombre del docente]
