import requests
from bs4 import BeautifulSoup
import json
import hashlib
from datetime import datetime

# ============================================================
# SST RADAR
# Sistema de monitoramento de Saúde e Segurança do Trabalho
# ============================================================

ARQUIVO_HISTORICO = "historico.json"

FONTES = {
    "MTE - Portarias SST": (
        "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/"
        "inspecao-do-trabalho/seguranca-e-saude-no-trabalho/"
        "sst-portarias"
    ),

    "MTE - Normas Regulamentadoras": (
        "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/"
        "inspecao-do-trabalho/seguranca-e-saude-no-trabalho/"
        "ctpp-nrs/normas-regulamentadoras-nrs"
    ),

    "INSS - Notícias": (
        "https://www.gov.br/inss/pt-br/assuntos/noticias"
    ),

    "INSS - Legislação": (
        "https://www.gov.br/inss/pt-br/centrais-de-conteudo/"
        "legislacao"
    ),

    "INSS - CAT": (
        "https://www.gov.br/pt-br/servicos/"
        "registrar-comunicacao-de-acidente-de-trabalho-cat"
    ),

"Fundacentro": (
        "https://www.gov.br/fundacentro/pt-br"
    )
}

TEMAS = {
    "NR-01 / GRO / PGR": [
        "nr-01", "nr-1", "gro", "pgr",
        "gerenciamento de riscos",
        "programa de gerenciamento de riscos"
    ],

    "NR-17 / Ergonomia": [
        "nr-17", "ergonomia", "ergonômica",
        "ergonômico", "aet",
        "avaliação ergonômica"
    ],

    "Riscos psicossociais": [
        "psicossocial", "psicossociais",
        "organização do trabalho",
        "saúde mental"
    ],

    "Acidentes e doenças ocupacionais": [
        "acidente de trabalho",
        "acidente do trabalho",
        "doença ocupacional",
        "doença relacionada ao trabalho",
        "cat"
    ],

    "Insalubridade / Periculosidade": [
        "insalubridade",
        "periculosidade"
    ],

    "eSocial / SST": [
        "esocial",
        "s-2210",
        "s-2220",
        "s-2240"
    ],

    "Segurança do Trabalho": [
        "segurança do trabalho",
        "saúde e segurança",
        "saúde ocupacional",
        "segurança e saúde no trabalho"
    ]
}


def baixar_pagina(url):

    cabecalhos = {
        "User-Agent": (
            "SST-Radar/1.0 "
            "(monitoramento público de informações de SST)"
        )
    }

    resposta = requests.get(
        url,
        headers=cabecalhos,
        timeout=30
    )

    resposta.raise_for_status()

    return resposta.text


def criar_id(titulo, endereco):

    texto = titulo.strip() + "|" + endereco.strip()

    return hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()


def carregar_historico():

    try:

        with open(
            ARQUIVO_HISTORICO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(arquivo)

            if "publicacoes" not in dados:
                dados["publicacoes"] = []

            return dados

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        return {
            "publicacoes": []
        }


def salvar_historico(historico):

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

def identificar_temas(texto):

    texto = texto.lower()

    encontrados = []

    for tema, palavras in TEMAS.items():

        for palavra in palavras:

            if palavra.lower() in texto:

                encontrados.append(tema)

                break

    return encontrados

def classificar_importancia(titulo, temas):

    texto = (
        titulo + " " +
        " ".join(temas)
    ).lower()

    pontuacao = 0

    # ========================================================
    # LEGISLAÇÃO E NORMAS
    # ========================================================

    if "nr-01" in texto or "nr-1" in texto:
        pontuacao += 10

    if "nr-17" in texto:
        pontuacao += 10

    if "nr-18" in texto:
        pontuacao += 8

    if "nr-35" in texto:
        pontuacao += 8

    if "portaria" in texto:
        pontuacao += 6

    if "instrução normativa" in texto:
        pontuacao += 6

    if "decreto" in texto:
        pontuacao += 5

    # ========================================================
    # GRO / PGR
    # ========================================================

    if "gro" in texto:
        pontuacao += 8

    if "pgr" in texto:
        pontuacao += 8

    if "gerenciamento de riscos" in texto:
        pontuacao += 8

    # ========================================================
    # ERGONOMIA
    # ========================================================

    if "ergonomia" in texto:
        pontuacao += 8

    if "ergonômica" in texto:
        pontuacao += 8

    if "ergonômico" in texto:
        pontuacao += 8

    if "aet" in texto:
        pontuacao += 8

    # ========================================================
    # RISCOS PSICOSSOCIAIS
    # ========================================================

    if "psicossocial" in texto:
        pontuacao += 10

    if "saúde mental" in texto:
        pontuacao += 7

    if "organização do trabalho" in texto:
        pontuacao += 6

    # ========================================================
    # ACIDENTES E DOENÇAS
    # ========================================================

    if "acidente de trabalho" in texto:
        pontuacao += 8

    if "acidente do trabalho" in texto:
        pontuacao += 8

    if "doença ocupacional" in texto:
        pontuacao += 8

    if "doença relacionada ao trabalho" in texto:
        pontuacao += 8

    if "cat" in texto:
        pontuacao += 6

    # ========================================================
    # INSALUBRIDADE / PERICULOSIDADE
    # ========================================================

    if "insalubridade" in texto:
        pontuacao += 7

    if "periculosidade" in texto:
        pontuacao += 7

    # ========================================================
    # eSOCIAL
    # ========================================================

    if "esocial" in texto:
        pontuacao += 6

    if "s-2210" in texto:
        pontuacao += 8

    if "s-2220" in texto:
        pontuacao += 8

    if "s-2240" in texto:
        pontuacao += 8

    # ========================================================
    # CLASSIFICAÇÃO
    # ========================================================

    if pontuacao >= 15:

        return "IMPORTANTE"

    elif pontuacao >= 8:

        return "ATENÇÃO"

    else:

        return "INFORMATIVO"

def extrair_links(html, fonte):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    resultados = []

    for link in soup.find_all(
        "a",
        href=True
    ):

        titulo = link.get_text(
            " ",
            strip=True
        )

        endereco = link.get(
            "href"
        )

        if not titulo or not endereco:
            continue

        if endereco.startswith("/"):

            endereco = (
                "https://www.gov.br"
                + endereco
            )

        texto_completo = (
            titulo
            + " "
            + endereco
        )

        temas = identificar_temas(
            texto_completo
        )

        # Se não encontrou nenhum tema,
        # não entra no radar.

        if not temas:
            continue

        identificador = criar_id(
            titulo,
            endereco
        )

        resultados.append({

            "id": identificador,

            "titulo": titulo,

            "url": endereco,

            "fonte": fonte,

            "temas": temas,

            "importancia":
                classificar_importancia(
                    temas
                ),

            "data_coleta":
                datetime.now().isoformat()

        })

    return resultados


def executar():

    print()
    print("=" * 70)
    print("              SST RADAR")
    print("Monitoramento de Saúde e Segurança do Trabalho")
    print("=" * 70)

    agora = datetime.now()

    print(
        "Data:",
        agora.strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )

    historico = carregar_historico()

    ids_existentes = {
        item.get("id")
        for item in historico["publicacoes"]
    }

    novas = []

    # ========================================================
    # CONSULTAR FONTES
    # ========================================================

    for nome_fonte, endereco in FONTES.items():

        print()
        print(
            "Consultando:",
            nome_fonte
        )

        try:

            html = baixar_pagina(
                endereco
            )

            resultados = extrair_links(
                html,
                nome_fonte
            )

            print(
                "Itens relevantes encontrados:",
                len(resultados)
            )

            for item in resultados:

                if item["id"] not in ids_existentes:

                    historico[
                        "publicacoes"
                    ].append(item)

                    ids_existentes.add(
                        item["id"]
                    )

                    novas.append(item)

        except Exception as erro:

            print(
                "ERRO:",
                erro
            )

    # ========================================================
    # LIMITAR HISTÓRICO
    # ========================================================

    # Mantemos os 1.000 registros mais recentes.

    historico["publicacoes"] = (
        historico["publicacoes"][-1000:]
    )

    salvar_historico(
        historico
    )

    # ========================================================
    # RESULTADO
    # ========================================================

    print()
    print("=" * 70)

    print(
        "NOVAS PUBLICAÇÕES:",
        len(novas)
    )

    if novas:

        print()

        for item in novas:

            print(
                "IMPORTÂNCIA:",
                item["importancia"]
            )

            print(
                "FONTE:",
                item["fonte"]
            )

            print(
                "TEMAS:",
                ", ".join(
                    item["temas"]
                )
            )

            print(
                "TÍTULO:",
                item["titulo"]
            )

            print(
                "LINK:",
                item["url"]
            )

            print("-" * 70)

    else:

        print(
            "Nenhuma nova publicação relevante."
        )

    print()
    print(
        "Total armazenado no histórico:",
        len(
            historico["publicacoes"]
        )
    )

    print()
    print(
        "SST Radar finalizado."
    )


if __name__ == "__main__":

    executar()
