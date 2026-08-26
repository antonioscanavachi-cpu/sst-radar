import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import json
import re

# ============================================================
# SST RADAR - MÓDULO DOU
# Monitoramento do Diário Oficial da União
# ============================================================

URL_DOU = "https://www.in.gov.br/consulta"

ARQUIVO_TESTE = "dou_teste.json"

PALAVRAS_SST = [
    "segurança e saúde no trabalho",
    "segurança do trabalho",
    "saúde ocupacional",
    "saúde do trabalhador",
    "saúde do trabalho",
    "ergonomia",
    "ergonômico",
    "ergonômica",
    "NR-01",
    "NR-1",
    "NR-17",
    "NR-18",
    "NR-35",
    "GRO",
    "PGR",
    "riscos psicossociais",
    "risco ocupacional",
    "acidente de trabalho",
    "acidente do trabalho",
    "doença ocupacional",
    "doença relacionada ao trabalho",
    "CAT",
    "insalubridade",
    "periculosidade",
    "higiene ocupacional",
    "Fundacentro",
    "Ministério do Trabalho",
    "INSS",
    "previdência social",
    "eSocial",
]


def criar_id(texto):

    return hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()


def baixar_pagina(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "SST-Radar/1.0"
        )
    }

    resposta = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    resposta.raise_for_status()

    return resposta.text


def encontrar_termos(texto):

    texto_lower = texto.lower()

    encontrados = []

    for termo in PALAVRAS_SST:

        if termo.lower() in texto_lower:

            encontrados.append(termo)

    return encontrados


def executar():

    print()
    print("=" * 70)
    print("SST RADAR - TESTE DO DOU")
    print("=" * 70)

    print(
        "Data:",
        datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )

    print()
    print("Acessando Diário Oficial da União...")

    try:

        html = baixar_pagina(
            URL_DOU
        )

    except Exception as erro:

        print()
        print("ERRO AO ACESSAR O DOU:")
        print(erro)

        return

    print("Página acessada com sucesso.")

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    texto = soup.get_text(
        " ",
        strip=True
    )

    termos = encontrar_termos(
        texto
    )

    print()
    print(
        "Termos relacionados a SST encontrados:",
        len(termos)
    )

    if termos:

        print()
        print("TERMOS ENCONTRADOS:")

        for termo in termos:

            print(
                "-",
                termo
            )

    else:

        print()
        print(
            "Nenhum termo de SST encontrado "
            "na página inicial."
        )

    # --------------------------------------------------------
    # SALVAR RESULTADO DO TESTE
    # --------------------------------------------------------

    resultado = {

        "data_teste":
            datetime.now().isoformat(),

        "fonte":
            "Diário Oficial da União",

        "termos_encontrados":
            termos,

        "id":
            criar_id(
                datetime.now().strftime(
                    "%Y-%m-%d"
                )
                + "|DOU"
            )

    }

    try:

        with open(
            ARQUIVO_TESTE,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                resultado,
                arquivo,
                ensure_ascii=False,
                indent=2
            )

        print()
        print(
            "Resultado salvo em:",
            ARQUIVO_TESTE
        )

    except Exception as erro:

        print(
            "Erro ao salvar resultado:",
            erro
        )

    print()
    print("=" * 70)
    print("TESTE DO DOU FINALIZADO")
    print("=" * 70)


if __name__ == "__main__":

    executar()
