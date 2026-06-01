from fastapi import FastAPI, Response
import pandas as pd
import requests
from io import StringIO

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.head("/health")
def health_head():
    return Response(status_code=200)

CSV_URL = "https://suameca.banrep.gov.co/estadisticas-economicas-back/rest/estadisticaEconomicaRestService/exportarReporteExcel?reportPath=/shared/Estadisticas_Banco_de_la_Republica/4_Sector_Externo_tasas_de_cambio_y_derivados/1_Tasas_de_cambio/1_Tasa_de_cambio_del_peso_colombiano_por_USD(TRM)/1_Tasa_de_Cambio_USD_COP/4_Serie_historica_TRM_iqy&formato=csv"

def cargar_datos():
    r = requests.get(CSV_URL, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(StringIO(r.content.decode("utf-8", errors="ignore")))
    df.columns = [c.strip() for c in df.columns]
    df["Fecha (dd/mm/aaaa)"] = pd.to_datetime(df["Fecha (dd/mm/aaaa)"], errors="coerce")
    df["TRM"] = pd.to_numeric(df["TRM"], errors="coerce")
    return df

@app.get("/trm")
def trm_ultimos_dos_anos():
    df = cargar_datos()
    hoy = pd.Timestamp.today().normalize()
    hace_dos_anos = hoy - pd.DateOffset(years=2)
    filtrado = df[(df["Fecha (dd/mm/aaaa)"] >= hace_dos_anos) & (df["Fecha (dd/mm/aaaa)"] <= hoy)].copy()
    filtrado = filtrado[["Fecha (dd/mm/aaaa)", "TRM"]]
    filtrado["Fecha (dd/mm/aaaa)"] = filtrado["Fecha (dd/mm/aaaa)"].dt.strftime("%Y-%m-%d")
    return filtrado.to_dict(orient="records")
