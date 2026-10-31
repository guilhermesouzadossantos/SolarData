import streamlit as st
import os
from src.extractor import processar_fatura

st.set_page_config(page_title="Dimensionamento Solar", layout="centered")

st.title("Automação de Dimensionamento Fotovoltaico")
st.write("Preencha os dados do cliente e anexe a fatura para extração do consumo.")

# Formulário integrado
with st.form("form_cliente"):
    nome = st.text_input("Nome do Cliente")
    estado = st.selectbox("Estado", ("RS", "SC", "PR", "SP"))
    telefone = st.text_input("Telefone de Contato")
    arquivo_fatura = st.file_uploader("Anexar Fatura de Energia", type=["pdf"])
    
    submit = st.form_submit_button("Processar Fatura")

if submit:
    if not arquivo_fatura:
        st.error("Documento ausente. Por favor, anexe uma fatura em PDF.")
    else:
        with st.spinner("Lendo histórico de consumo..."):
            # Salva cópia temporária na camada raw
            caminho_raw = os.path.join("data", "raw", arquivo_fatura.name)
            os.makedirs(os.path.dirname(caminho_raw), exist_ok=True)
            with open(caminho_raw, "wb") as f:
                f.write(arquivo_fatura.getbuffer())

            # Executa a extração
            df_consumo = processar_fatura(arquivo_fatura)

            if df_consumo.empty:
                st.warning("Padrão de consumo não localizado. Verifique o arquivo enviado.")
            else:
                st.success(f"Fatura de {nome} processada com sucesso!")
                
                # Exibe a planilha dinamicamente na interface
                st.dataframe(df_consumo, use_container_width=True)
                
                # Botão para exportação do arquivo
                csv = df_consumo.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Baixar Planilha (CSV)",
                    data=csv,
                    file_name=f"historico_{nome.replace(' ', '_')}.csv",
                    mime="text/csv"
                )