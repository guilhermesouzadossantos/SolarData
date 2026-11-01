import streamlit as st
import os
from src.extractor import processar_fatura
from src.sizing import calcular_sistema_fotovoltaico

st.set_page_config(page_title="Dimensionamento Solar", page_icon="☀️", layout="centered")

st.title("☀️ Automação de Dimensionamento Fotovoltaico")
st.markdown("Preencha os dados do cliente e anexe a fatura para extração do consumo.")

with st.form("form_cliente"):
    st.subheader("👤 Dados do Cliente")
    col_nome, col_tel = st.columns(2)
    nome = col_nome.text_input("Nome do Cliente", placeholder="Ex: João da Silva")
    telefone = col_tel.text_input("Telefone de Contato", placeholder="(00) 00000-0000")
    
    col_est, col_padrao = st.columns(2)
    estado = col_est.selectbox("Estado", ("RS", "SC", "PR", "SP"))
    padrao_entrada = col_padrao.selectbox("Padrão de Entrada", ("Monofásico", "Bifásico", "Trifásico"))
    
    st.subheader("📄 Documentação")
    arquivo_fatura = st.file_uploader("Anexar Fatura de Energia", type=["pdf"], help="Faça o upload da conta de luz em formato PDF.")
    
    submit = st.form_submit_button("🚀 Processar Fatura", use_container_width=True)

if submit:
    if not arquivo_fatura:
        st.error("⚠️ Documento ausente. Por favor, anexe uma fatura em PDF.")
    elif not nome.strip():
        st.warning("⚠️ Por favor, preencha o nome do cliente.")
    else:
        with st.spinner("Lendo histórico de consumo e calculando dimensionamento..."):
            caminho_raw = os.path.join("data", "raw", arquivo_fatura.name)
            os.makedirs(os.path.dirname(caminho_raw), exist_ok=True)
            with open(caminho_raw, "wb") as f:
                f.write(arquivo_fatura.getbuffer())

            df_consumo = processar_fatura(arquivo_fatura)

            if df_consumo.empty:
                st.warning("⚠️ Padrão de consumo não localizado. Verifique o arquivo enviado.")
            else:
                st.success(f"✅ Fatura de **{nome}** processada com sucesso!")
                st.divider() # Linha divisória 
                
                dimensionamento = calcular_sistema_fotovoltaico(
                    df_consumo=df_consumo,
                    estado=estado,
                    padrao_entrada=padrao_entrada,
                    potencia_modulo_w=550
                )
                
                if dimensionamento:
                    st.subheader("📊 Resultados do Dimensionamento")
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Consumo Médio", f"{dimensionamento['consumo_medio_kwh']} kWh/mês")
                    col2.metric("Tamanho do Sistema", f"{dimensionamento['tamanho_sistema_kwp']} kWp")
                    
                    st.info(f"💡 **Recomendação de Equipamentos:** Serão necessários **{dimensionamento['numero_de_modulos']} módulos** de 550W.")
                    
                    with st.expander("📂 Ver Histórico Extraído da Fatura", expanded=False):
                        st.dataframe(df_consumo, use_container_width=True)
                        
                        csv = df_consumo.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="⬇️ Baixar Planilha (CSV)",
                            data=csv,
                            file_name=f"historico_{nome.replace(' ', '_')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.error("Erro ao gerar o dimensionamento a partir dos dados de consumo.")
