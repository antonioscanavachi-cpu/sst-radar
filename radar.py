import requests
from bs4 import BeautifulSoup
import json
import hashlib
from datetime import datetime

# ============================================================
# SST RADAR
# Monitoramento inicial do Ministério do Trabalho e Emprego
# ============================================================

URL_PORTARIAS = (
    "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/"
    "inspecao-do-trabalho/seguranca-e-saude-no-trabalho/"
    "sst-portarias"
)

URL_NRS = (
    "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/"
    "inspecao-do-trabalho/seguranca-e-saude-no-trabalho/"
    "ctpp-nrs/normas-regulamentadoras-nrs"
)

ARQUIVO_HISTORICO = "historico.json"

PALAVRAS_CHAVE = [
    "segurança",
    "saúde",
    "segurança e saúde",
    "norma regulamentadora",
    "NR-01",
    "NR-1",
    "NR-17",
    "NR-35",
    "ergonomia",
    "ergonôm",
    "AET",
    "avaliação ergonômica",
    "PGR",
    "GRO",
    "risco ocupacional",
    "riscos psicossociais",
    "acidente de trabalho",
    "doença ocupacional",
    "CAT",
    "eSocial",
    "insalubridade",
    "periculosidade",
]


def baixar_pagina(url):
    """Baixa uma página oficial."""
    
    cabecalho = {
        "User-Agent": (
            "SST-Radar/1.0 "
            "(monitoramento de informações públicas de SST)"
        )
    }

    resposta = requests.get(
        url,
        headers=cabecalho,
        timeout=30
    )

    resposta.raise_for_status()

    return resposta.text


def criar_id(texto):
    """Cria um identificador único para uma publicação."""
    
    return hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()


def carregar_historico():
    """Carrega as publicações já encontradas."""
    
    try:
        with open(
            ARQUIVO_HISTORICO,
            "r",
            encoding="utf-8"
        ) as arquivo:
            return json.load(arquivo)

    except (FileNotFoundError, json.JSONDecodeError):
        return {"publicacoes": []}


def salvar_historico(historico):
    """Salva o histórico atualizado."""
    
    with open(
        ARQUIVO_HISTORICO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            historico,
            arquivo,
            ensure_ascii=False,
            indent=2
        )


def eh_relevante(texto):
    """Verifica se o conteúdo possui algum termo de SST."""
    
    texto = texto.lower()

    for palavra in PALAVRAS_CHAVE:
        if palavra.lower() in texto:
            return True

    return False


def analisar_portarias(html):
    """Extrai links encontrados na página de Portarias SST."""

    soup = BeautifulSoup(html, "html.parser")

    resultados = []

    for link in soup.find_all("a", href=True):

        titulo = link.get_text(" ", strip=True)

        endereco = link.get("href")

        if not titulo:
            continue

        texto = titulo.lower()

        if (
            "portaria" in texto
            or "nr-" in texto
            or "norma" in texto
        ):

            if endereco.startswith("/"):
                endereco = (
                    "https://www.gov.br" + endereco
                )

            identificador = criar_id(
                titulo + endereco
            )

            resultados.append({
                "id": identificador,
                "titulo": titulo,
                "url": endereco,
                "fonte": "MTE - Portarias SST",
                "data_coleta": datetime.now().isoformat()
            })

    return resultados


def analisar_nrs(html):
    """Extrai informações da página de NRs."""

    soup = BeautifulSoup(html, "html.parser")

    resultados = []

    for link in soup.find_all("a", href=True):

        titulo = link.get_text(" ", strip=True)

        endereco = link.get("href")

        if not titulo:
            continue

        if "NR-" in titulo.upper():

            if endereco.startswith("/"):
                endereco = (
                    "https://www.gov.br" + endereco
                )

            identificador = criar_id(
                titulo + endereco
            )

            resultados.append({
                "id": identificador,
                "titulo": titulo,
                "url": endereco,
                "fonte": "MTE - Normas Regulamentadoras",
                "data_coleta": datetime.now().isoformat()
            })

    return resultados


def executar():

    print("=" * 70)
    print("SST RADAR")
    print("Monitoramento automático de Saúde e Segurança do Trabalho")
    print("=" * 70)

    print(
        "Execução:",
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )

    historico = carregar_historico()

    ids_existentes = {
        item["id"]
        for item in historico["publicacoes"]
    }

    novas_publicacoes = []

    # --------------------------------------------------------
    # MTE - PORTARIAS SST
    # --------------------------------------------------------

    print("\nConsultando MTE - Portarias SST...")

    try:

        html = baixar_pagina(URL_PORTARIAS)

        publicacoes = analisar_portarias(html)

        print(
            f"Publicações encontradas: {len(publicacoes)}"
        )

        for publicacao in publicacoes:

            if publicacao["id"] not in ids_existentes:

                historico["publicacoes"].append(
                    publicacao
                )

                novas_publicacoes.append(
                    publicacao
                )

    except Exception as erro:

        print(
            "Erro ao consultar Portarias SST:",
            erro
        )

    # --------------------------------------------------------
    # MTE - NORMAS REGULAMENTADORAS
    # --------------------------------------------------------

    print("\nConsultando MTE - Normas Regulamentadoras...")

    try:

        html = baixar_pagina(URL_NRS)

        publicacoes = analisar_nrs(html)

        print(
            f"Informações encontradas: {len(publicacoes)}"
        )

        for publicacao in publicacoes:

            if publicacao["id"] not in ids_existentes:

                historico["publicacoes"].append(
                    publicacao
                )

                novas_publicacoes.append(
                    publicacao
                )

    except Exception as erro:

        print(
            "Erro ao consultar NRs:",
            erro
        )

    salvar_historico(historico)

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    print("\n" + "=" * 70)

    print(
        f"Novas publicações detectadas: "
        f"{len(novas_publicacoes)}"
    )

    if novas_publicacoes:

        print("\nNOVAS PUBLICAÇÕES:\n")

        for item in novas_publicacoes:

            print("Fonte:", item["fonte"])
            print("Título:", item["titulo"])
            print("Link:", item["url"])
            print("-" * 70)

    else:

        print(
            "\nNenhuma nova publicação encontrada."
        )

    print("\nHistórico atualizado.")


if __name__ == "__main__":
    executar()
