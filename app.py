import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
from datetime import datetime

st.title("ASIGNACION AUTOMATICA 👥")
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #eef2f3, #dfe9f3);
    }
    </style>
""", unsafe_allow_html=True)
ahora = datetime.now()
nombre_fecha = ahora.strftime("%Y%m%d")
dotacion = st.file_uploader("Subir dotacion", "xlsx")
base = st.file_uploader("Subir Base de datos", "csv")

if dotacion is None or base is None:
    st.warning("Subir los archivos necesarios")
else:
    maestro = pd.read_excel(dotacion)
    nuevo = pd.read_csv(base, sep=",")

    nuevo["SUPERVISOR"] = ""
    nuevo["JEFATURA"] = ""

    for banco, grupo in maestro.groupby("JEFATURA_FINAL"):

        supervisores = grupo["SUPERVISOR"].unique().tolist()

        mapa_jefatura = (
            grupo[["SUPERVISOR", "JEFATURA"]]
            .drop_duplicates()
            .set_index("SUPERVISOR")["JEFATURA"]
            .to_dict()
        )

        idx = nuevo[nuevo["JEFATURA_FINAL"] == banco].index

        cantidad = len(idx)

        if cantidad == 0:
            continue

        n_super = len(supervisores)

        cantidad_base = cantidad // n_super
        sobrante = cantidad % n_super

        asignados = []

        for i, supervisor in enumerate(supervisores):
            veces = cantidad_base + (1 if i < sobrante else 0)
            asignados.extend([supervisor] * veces)

        np.random.shuffle(asignados)

        nuevo.loc[idx, "SUPERVISOR"] = asignados
        nuevo.loc[idx, "JEFATURA"] = nuevo.loc[idx, "SUPERVISOR"].map(mapa_jefatura)
        nuevo_filtrado = nuevo[nuevo["cell_phone_number_id"].notna()]
    st.subheader("VISTA PREVIA")   
    st.dataframe(nuevo_filtrado)
    st.success("Se eliminaron los leads sin telefonos")

    jefaturas = sorted(nuevo_filtrado["JEFATURA"].dropna().unique().tolist())
    filtro_jefatura = st.multiselect("Filtrar por JEFATURA", jefaturas)
    data_filtrada = nuevo_filtrado[nuevo_filtrado["JEFATURA"].isin(filtro_jefatura)]
    tabla_resumen = pd.pivot_table(
    data_filtrada,
    index="JEFATURA_FINAL",
    columns="SUPERVISOR",
    values="cell_phone_number_id",
    aggfunc="count",
    fill_value=0,
    margins=True,
    margins_name="Total general"
    )

    st.subheader("Resumen por Jefatura y Supervisor")
    st.dataframe(tabla_resumen)
    buffer = BytesIO() 
    data_filtrada.to_excel(buffer, index=False, engine="openpyxl")
    st.download_button(
        label="Descargar Excel",
        data=buffer.getvalue(),
        file_name=f"BASE_ASIGNACION.xlsx {nombre_fecha}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
