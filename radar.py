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

    titulo_lower = titulo.lower()

    texto_temas = " ".join(temas).lower()

    texto = titulo_lower + " " + texto_temas

    # ========================================================
    # CONTEÚDOS QUE NÃO DEVEM GERAR ALERTA
    # ========================================================

    termos_informativos = [
        "curso",
        "cursos",
        "capacitação",
        "treinamento",
        "evento",
        "seminário",
        "palestra",
        "workshop",
        "webinar",
        "campanha",
        "inscrição",
        "agenda",
        "consultar",
        "consulta",
        "serviço",
        "serviços",
    ]

    conteudo_informativo = any(
        termo in titulo_lower
        for termo in termos_informativos
    )

    # ========================================================
    # INDICADORES DE ALTERAÇÃO NORMATIVA
    # ========================================================

    alteracoes = [
        "altera",
        "alteração",
        "altera a redação",
        "nova redação",
        "modifica",
        "modificação",
        "aprova",
        "estabelece",
        "regulamenta",
        "revoga",
        "inclui",
        "exclui",
        "prorroga",
        "dispõe sobre",
        "entra em vigor",
    ]

    eh_alteracao = any(
        termo in titulo_lower
        for termo in alteracoes
    )

    # ========================================================
    # NORMAS RELEVANTES
    # ========================================================

    nr_relevante = any(
        termo in titulo_lower
        for termo in [
            "nr-01",
            "nr-1",
            "nr-17",
            "nr-18",
            "nr-35",
        ]
    )

    # ========================================================
    # TEMAS CRÍTICOS
    # ========================================================

    tema_critico = any(
        termo in texto
        for termo in [
            "riscos psicossociais",
            "risco psicossocial",
            "saúde mental",
            "doença ocupacional",
            "doença relacionada ao trabalho",
            "acidente de trabalho",
            "acidente do trabalho",
            "insalubridade",
            "periculosidade",
        ]
    )

    # ========================================================
    # ERGONOMIA
    # ========================================================

    ergonomia = any(
        termo in texto
        for termo in [
            "ergonomia",
            "ergonômico",
            "ergonômica",
            "avaliação ergonômica",
            "análise ergonômica",
            "aet",
        ]
    )

    # ========================================================
    # PGR / GRO
    # ========================================================

    pgr_gro = any(
        termo in texto
        for termo in [
            "pgr",
            "gro",
            "gerenciamento de riscos",
            "gerenciamento de riscos ocupacionais",
        ]
    )

    # ========================================================
    # ALTERAÇÃO NORMATIVA DE ALTA RELEVÂNCIA
    # ========================================================

    if eh_alteracao:

        if nr_relevante:
            return "IMPORTANTE"

        if tema_critico:
            return "IMPORTANTE"

        if ergonomia:
            return "IMPORTANTE"

        if pgr_gro:
            return "IMPORTANTE"

    # ========================================================
    # ATOS OFICIAIS
    # ========================================================

    ato_oficial = any(
        termo in titulo_lower
        for termo in [
            "portaria",
            "decreto",
            "instrução normativa",
            "resolução",
            "lei ",
            "medida provisória",
        ]
    )

    if ato_oficial:

        if (
            nr_relevante
            or tema_critico
            or ergonomia
            or pgr_gro
        ):
            return "IMPORTANTE"

        return "ATENÇÃO"

    # ========================================================
    # CURSOS, EVENTOS E SERVIÇOS
    # ========================================================

    if conteudo_informativo:
        return "INFORMATIVO"

    # ========================================================
    # CONTEÚDO TÉCNICO
    # ========================================================

    if ergonomia:
        return "ATENÇÃO"

    if tema_critico:
        return "ATENÇÃO"

    if pgr_gro:
        return "ATENÇÃO"

    # ========================================================
    # ACIDENTES
    # ========================================================

    if (
        "acidente de trabalho" in titulo_lower
        or "acidente do trabalho" in titulo_lower
    ):
        return "ATENÇÃO"

    # ========================================================
    # PADRÃO
    # ========================================================

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

        # ====================================================
        # NORMALIZAR URL
        # ====================================================

        if endereco.startswith("/"):

            endereco = (
                "https://www.gov.br"
                + endereco
            )

        titulo_lower = titulo.lower()
        endereco_lower = endereco.lower()

        # ====================================================
        # IGNORAR LINKS DE COMPARTILHAMENTO
        # ====================================================

        palavras_compartilhamento = [
            "whatsapp",
            "facebook",
            "linkedin",
            "twitter",
            "telegram",
            "compartilhar",
            "compartilhe"
        ]

        if any(
            palavra in titulo_lower
            or palavra in endereco_lower
            for palavra in palavras_compartilhamento
        ):
            continue

        # ====================================================
        # IGNORAR SISTEMAS E PÁGINAS DE SERVIÇO
        # ====================================================

        caminhos_bloqueados = [
            "/servicos/",
            "/apps/",
            "/categorias",
            "/composicao/orgaos-colegiados/",
            "cadastro-cat.inss.gov.br",
        ]

        if any(
            caminho in endereco_lower
            for caminho in caminhos_bloqueados
        ):
            continue

        # ====================================================
        # IGNORAR PÁGINAS INSTITUCIONAIS
        # ====================================================

        paginas_institucionais = [
            "portarias",
            "portarias internas",
            "sst portarias",
            "instruções normativas",
            "instrucoes normativas",
            "legislação",
            "legislacao",
            "normas regulamentadoras",
            "normas regulamentadoras (nr)",
            "normas regulamentadoras (nr) e legislação de segurança e saúde no trabalho",
            "fiscalização de segurança e saúde no trabalho",
            "sindicatos",
            "cadastro de entidades",
            "central sindical",
            "contribuição sindical",
            "mediação",
            "painel de relações do trabalho",
            "galeria de aplicativos",
            "categorias",
            "esocial",
        ]

        if titulo_lower in paginas_institucionais:
            continue

        # ====================================================
        # IGNORAR CONSULTAS E PÁGINAS ADMINISTRATIVAS
        # ====================================================

        if (
            titulo_lower.startswith("consultar ")
            or titulo_lower.startswith("consulta ")
            or titulo_lower.startswith("iniciar")
            or titulo_lower.startswith("acessar")
        ):
            continue

        if (
            "portarias de designação" in titulo_lower
            or "designação de fiscais" in titulo_lower
        ):
            continue

        # ====================================================
        # IGNORAR PÁGINAS PERMANENTES DAS NRs
        # ====================================================

        if titulo_lower.startswith("nr-"):

            partes = titulo_lower.split(
                " - ",
                1
            )

            if len(partes) == 2:

                numero_nr = (
                    partes[0]
                    .replace("nr-", "")
                    .strip()
                )

                if numero_nr.isdigit():
                    continue

        # ====================================================
        # IDENTIFICAÇÃO DOS TEMAS
        # ====================================================

        texto_completo = (
            titulo
            + " "
            + endereco
        )

        temas = identificar_temas(
            texto_completo
        )

        if not temas:
            continue

        # ====================================================
        # CRIAÇÃO DO REGISTRO
        # ====================================================

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
                    titulo,
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
