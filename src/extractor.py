import pandas as pd
import pdfplumber
import re

def processar_fatura(arquivo):
    texto_completo = ""
    # Abre o arquivo carregado em memória pelo Streamlit
    with pdfplumber.open(arquivo) as pdf:
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text() + "\n"

    # Expressão regular simulada para capturar o bloco de histórico (ex: "JAN 26 350")
    padrao = r"([A-Z]{3} \d{2})\s+(\d+)"
    resultados = re.findall(padrao, texto_completo)

    if not resultados:
         return pd.DataFrame(columns=["Mes_Ano", "Consumo_kWh"])

    df = pd.DataFrame(resultados, columns=["Mes_Ano", "Consumo_kWh"])
    df['Consumo_kWh'] = pd.to_numeric(df['Consumo_kWh'])
    
    return df