import math
import pandas as pd

HSP_POR_ESTADO = {
    "RS": 4.2,
    "SC": 4.1,
    "PR": 4.3,
    "SP": 4.5
}

CUSTO_DISPONIBILIDADE = {
    "Monofásico": 30,
    "Bifásico": 50,
    "Trifásico": 100
}

def calcular_sistema_fotovoltaico(df_consumo: pd.DataFrame, estado: str, padrao_entrada: str, 
                                  potencia_modulo_w: int = 550, pr: float = 0.80):
  
    if df_consumo.empty:
        return None

    # Consumo médio
    consumo_medio = df_consumo['Consumo_kWh'].mean()

    taxa_minima = CUSTO_DISPONIBILIDADE.get(padrao_entrada, 50)
    consumo_alvo = max(consumo_medio - taxa_minima, 0)
    
    if consumo_alvo == 0:
         consumo_alvo = consumo_medio

    # Tamanho do sistema (kWp) e número de módulos
    hsp = HSP_POR_ESTADO.get(estado, 4.0)
    dias_mes = 30
    
    potencia_necessaria_kwp = consumo_alvo / (hsp * dias_mes * pr)
    potencia_modulo_kw = potencia_modulo_w / 1000
    
    numero_de_modulos = math.ceil(potencia_necessaria_kwp / potencia_modulo_kw)
    tamanho_sistema_kwp = numero_de_modulos * potencia_modulo_kw

    return {
        "consumo_medio_kwh": round(consumo_medio, 2),
        "tamanho_sistema_kwp": round(tamanho_sistema_kwp, 2),
        "numero_de_modulos": numero_de_modulos
    }