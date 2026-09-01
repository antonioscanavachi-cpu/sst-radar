import requests
from bs4 import BeautifulSoup
import json
import hashlib
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse


# ============================================================
# SST RADAR
# Sistema de monitoramento de Saúde e Segurança do Trabalho
# ============================================================

ARQUIVO_HISTORICO = "historico.json"


# ============================================================
# FONTES
# ============================================================

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


# ============================================================
# TEMAS
# ============================================================

TEMAS = {

    "NR-01 / GRO / PGR": [
        r"\bnr[\s-]?01\b",
        r"\bnr[\s-]?1\b",
        r"\bgro\b",
        r"\bpgr\b",
        r"gerenciamento de riscos",
        r"programa de gerenciamento de riscos"
    ],

    "NR-17 / Ergonomia": [
        r"\bnr[\s-]?17\b",
        r"ergonomia",
        r"ergonômica",
        r"ergonômico",
        r"\baet\b",
        r"avaliação ergonômica",
        r"análise ergonômica"
    ],

    "Riscos psicossociais": [
        r"psicossocial",
        r"psicossociais",
        r"organização do trabalho",
        r"saúde mental"
    ],

    "Acidentes e doenças ocupacionais": [
        r"acidente de trabalho",
        r"acidente do trabalho",
        r"doença ocupacional",
        r"doença relacionada ao trabalho",
        r"\bcat\b"
    ],

    "Insalubridade / Periculosidade": [
        r"insalubridade",
        r"periculosidade"
    ],

    "eSocial / SST": [
        r"\besocial\b",
        r"\bs-2210\b",
        r"\bs-2220\b",
        r"\bs-2240\b"
    ],

    "Segurança do Trabalho": [
        r"segurança do trabalho",
        r"saúde e segurança",
        r"saúde ocupacional",
        r"segurança e saúde no trabalho"
    ]
}


# ============================================================
# PALAVRAS QUE INDICAM CONTEÚDO INSTITUCIONAL
# ============================================================

PAGINAS_INSTITUCIONAIS = {
    "portarias",
    "portarias internas",
    "sst portarias",
    "instruções normativas",
    "instrucoes normativas",
    "legislação",
    "legislacao",
    "legislação de segurança e saúde no trabalho",
    "normas regulamentadoras",
    "normas regulamentadoras (nr)",
    "normas regulamentadoras (nr) e legislação de segurança e saúde no trabalho",
    "fiscalização de segurança e saúde no trabalho",
    "sindicatos",
    "cadastro de entidades",
    "central sindical",
    "contribuição sindical",
    "mediacao",
    "mediação",
    "painel de relações do trabalho",
    "galeria de aplicativos",
    "categorias",
    "esocial",
    "iniciar",
    "acessar",
}


# ============================================================
# CAMINHOS QUE NÃO DEVEM ENTRAR NO RADAR
# ============================================================

CAMINHOS_BLOQUEADOS = [
    "/servicos/",
    "/apps/",
    "/categorias",
    "/composicao/orgaos-colegiados/",
    "/acesso-a-informacao/",
    "/participacao-social/",
    "cadastro-cat.inss.gov.br",
    "api.whatsapp.com",
    "facebook.com",
    "linkedin.com",
    "twitter.com",
    "telegram.me",
]


# ============================================================
# BAIXAR PÁGINA
# ============================================================

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


# ============================================================
# CRIAR ID
# ============================================================

def criar_id(titulo, endereco):

    texto = (
        titulo.strip()
        + "|"
        + endereco.strip()
    )

    return hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()


# ============================================================
# CARREGAR HISTÓRICO
# ============================================================

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


# ============================================================
# SALVAR HISTÓRICO
# ============================================================

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


# ============================================================
# IDENTIFICAR TEMAS
# ============================================================

def identificar_temas(texto):

    texto = texto.lower()

    encontrados = []

    for tema, palavras in TEMAS.items():

        for padrao in palavras:

            if re.search(
                padrao,
                texto,
                flags=re.IGNORECASE
            ):

                encontrados.append(tema)

                break

    return encontrados


# ============================================================
# VERIFICAR PÁGINA INSTITUCIONAL
# ============================================================

def eh_pagina_institucional(titulo, endereco):

    titulo_lower = (
        titulo.lower()
        .strip()
    )

    endereco_lower = (
        endereco.lower()
        .strip()
    )

    # --------------------------------------------------------
    # Título exato
    # --------------------------------------------------------

    if titulo_lower in PAGINAS_INSTITUCIONAIS:
        return True

    # --------------------------------------------------------
    # Consultas
    # --------------------------------------------------------

    if (
        titulo_lower.startswith("consultar ")
        or titulo_lower.startswith("consulta ")
    ):
        return True

    # --------------------------------------------------------
    # Compartilhamento
    # --------------------------------------------------------

    palavras_compartilhamento = [
        "whatsapp",
        "facebook",
        "linkedin",
        "twitter",
        "telegram",
        "compartilhar",
        "compartilhe",
    ]

    if any(
        palavra in titulo_lower
        or palavra in endereco_lower
        for palavra in palavras_compartilhamento
    ):
        return True

    # --------------------------------------------------------
    # Caminhos bloqueados
    # --------------------------------------------------------

    if any(
        caminho in endereco_lower
        for caminho in CAMINHOS_BLOQUEADOS
    ):
        return True

    # --------------------------------------------------------
    # Designação administrativa
    # --------------------------------------------------------

    if (
        "portarias de designação" in titulo_lower
        or "designação de fiscais" in titulo_lower
    ):
        return True

    # --------------------------------------------------------
    # Páginas permanentes das NRs
    #
    # Exemplos:
    # NR-1
    # NR-01
    # NR-12
    # NR-35
    #
    # Mas NÃO:
    # "Cursos sobre NR-12"
    # "Alteração da NR-12"
    # --------------------------------------------------------

    if re.fullmatch(
        r"nr[\s-]?\d{1,2}",
        titulo_lower
    ):
        return True

    return False


# ============================================================
# CLASSIFICAR IMPORTÂNCIA
# ============================================================

def classificar_importancia(titulo, temas):

    titulo_lower = titulo.lower()

    texto_temas = " ".join(
        temas
    ).lower()

    texto = (
        titulo_lower
        + " "
        + texto_temas
    )

    # --------------------------------------------------------
    # CONTEÚDOS INFORMATIVOS
    # --------------------------------------------------------

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
        "aplicativo",
        "aplicativos",
        "congresso",
    ]

    conteudo_informativo = any(
        termo in titulo_lower
        for termo in termos_informativos
    )

    # --------------------------------------------------------
    # ALTERAÇÃO NORMATIVA
    # --------------------------------------------------------

    alteracoes = [
        "altera",
        "alteração",
        "alteracoes",
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

    # --------------------------------------------------------
    # NRs DE MAIOR INTERESSE
    # --------------------------------------------------------

    nr_relevante = any(
        re.search(
            padrao,
            titulo_lower
        )
        for padrao in [
            r"\bnr[\s-]?01\b",
            r"\bnr[\s-]?1\b",
            r"\bnr[\s-]?17\b",
            r"\bnr[\s-]?18\b",
            r"\bnr[\s-]?35\b",
        ]
    )

    # --------------------------------------------------------
    # TEMAS CRÍTICOS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ERGONOMIA
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PGR / GRO
    # --------------------------------------------------------

    pgr_gro = any(
        termo in texto
        for termo in [
            "pgr",
            "gro",
            "gerenciamento de riscos",
            "gerenciamento de riscos ocupacionais",
        ]
    )

    # --------------------------------------------------------
    # ALTERAÇÃO NORMATIVA DE ALTA RELEVÂNCIA
    # --------------------------------------------------------

    if eh_alteracao:

        if nr_relevante:
            return "IMPORTANTE"

        if tema_critico:
            return "IMPORTANTE"

        if ergonomia:
            return "IMPORTANTE"

        if pgr_gro:
            return "IMPORTANTE"

    # --------------------------------------------------------
    # ATOS OFICIAIS
    # --------------------------------------------------------

    ato_oficial = any(
        termo in titulo_lower
        for termo in [
            "portaria",
            "decreto",
            "instrução normativa",
            "instrucoes normativas",
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

    # --------------------------------------------------------
    # CURSOS, EVENTOS E SERVIÇOS
    # --------------------------------------------------------

    if conteudo_informativo:
        return "INFORMATIVO"

    # --------------------------------------------------------
    # CONTEÚDO TÉCNICO
    # --------------------------------------------------------

    if ergonomia:
        return "ATENÇÃO"

    if tema_critico:
        return "ATENÇÃO"

    if pgr_gro:
        return "ATENÇÃO"

    # --------------------------------------------------------
    # ACIDENTES
    # --------------------------------------------------------

    if (
        "acidente de trabalho" in titulo_lower
        or "acidente do trabalho" in titulo_lower
    ):
        return "ATENÇÃO"

    # --------------------------------------------------------
    # PADRÃO
    # --------------------------------------------------------

    return "INFORMATIVO"


# ============================================================
# EXTRAIR LINKS
# ============================================================

def extrair_links(html, fonte):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    resultados = []

    ids_desta_pagina = set()

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

        # ----------------------------------------------------
        # NORMALIZAR URL
        # ----------------------------------------------------

        endereco = urljoin(
            "https://www.gov.br",
            endereco
        )

        endereco = endereco.strip()

        # ----------------------------------------------------
        # SOMENTE HTTP/HTTPS
        # ----------------------------------------------------

        esquema = urlparse(
            endereco
        ).scheme.lower()

        if esquema not in [
            "http",
            "https"
        ]:
            continue

        titulo_lower = titulo.lower()
        endereco_lower = endereco.lower()

        # ----------------------------------------------------
        # EVITAR ÂNCORAS E LINKS INTERNOS
        # ----------------------------------------------------

        if endereco.startswith("#"):
            continue

        # ----------------------------------------------------
        # PÁGINAS INSTITUCIONAIS
        # ----------------------------------------------------

        if eh_pagina_institucional(
            titulo,
            endereco
        ):
            continue

        # ----------------------------------------------------
        # IDENTIFICAÇÃO DOS TEMAS
        #
        # IMPORTANTE:
        # somente o título é usado.
        #
        # Isso evita que palavras presentes na URL
        # criem falsos positivos.
        # ----------------------------------------------------

        temas = identificar_temas(
            titulo
        )

        if not temas:
            continue

        # ----------------------------------------------------
        # CRIAR ID
        # ----------------------------------------------------

        identificador = criar_id(
            titulo,
            endereco
        )

        # ----------------------------------------------------
        # EVITAR DUPLICAÇÃO NA MESMA PÁGINA
        # ----------------------------------------------------

        if identificador in ids_desta_pagina:
            continue

        ids_desta_pagina.add(
            identificador
        )

        # ----------------------------------------------------
        # REGISTRO
        # ----------------------------------------------------

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


# ============================================================
# LIMPAR DUPLICIDADES DO HISTÓRICO
# ============================================================

def limpar_historico(historico):

    publicacoes = historico.get(
        "publicacoes",
        []
    )

    resultado = []

    ids = set()

    removidos = 0

    for item in publicacoes:

        titulo = item.get(
            "titulo",
            ""
        )

        endereco = item.get(
            "url",
            ""
        )

        identificador = item.get(
            "id"
        )

        # ----------------------------------------------------
        # Recriar ID quando necessário
        # ----------------------------------------------------

        if titulo and endereco:

            novo_id = criar_id(
                titulo,
                endereco
            )

            identificador = novo_id

            item["id"] = novo_id

        # ----------------------------------------------------
        # Remover duplicados
        # ----------------------------------------------------

        if identificador in ids:

            removidos += 1

            continue

        ids.add(
            identificador
        )

        # ----------------------------------------------------
        # Remover páginas institucionais antigas
        # ----------------------------------------------------

        if eh_pagina_institucional(
            titulo,
            endereco
        ):

            removidos += 1

            continue

        # ----------------------------------------------------
        # Corrigir temas antigos
        # ----------------------------------------------------

        temas = identificar_temas(
            titulo
        )

        if not temas:

            removidos += 1

            continue

        item["temas"] = temas

        item["importancia"] = (
            classificar_importancia(
                titulo,
                temas
            )
        )

        resultado.append(
            item
        )

    historico["publicacoes"] = resultado

    return removidos


# ============================================================
# EXECUTAR
# ============================================================

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

    # --------------------------------------------------------
    # LIMPAR HISTÓRICO ANTIGO
    # --------------------------------------------------------

    quantidade_antes = len(
        historico.get(
            "publicacoes",
            []
        )
    )

    removidos = limpar_historico(
        historico
    )

    quantidade_depois = len(
        historico["publicacoes"]
    )

    if removidos > 0:

        print()
        print(
            "Limpeza do histórico:"
        )

        print(
            "Registros anteriores:",
            quantidade_antes
        )

        print(
            "Registros removidos:",
            removidos
        )

        print(
            "Registros válidos:",
            quantidade_depois
        )

    # --------------------------------------------------------
    # IDs EXISTENTES
    # --------------------------------------------------------

    ids_existentes = {
        item.get("id")
        for item in historico["publicacoes"]
    }

    novas = []

    # --------------------------------------------------------
    # CONSULTAR FONTES
    # --------------------------------------------------------

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

                if item["id"] in ids_existentes:
                    continue

                historico[
                    "publicacoes"
                ].append(item)

                ids_existentes.add(
                    item["id"]
                )

                novas.append(
                    item
                )

        except Exception as erro:

            print(
                "ERRO:",
                erro
            )

    # --------------------------------------------------------
    # LIMITAR HISTÓRICO
    # --------------------------------------------------------

    historico["publicacoes"] = (
        historico["publicacoes"][-1000:]
    )

    salvar_historico(
        historico
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # RESUMO DO HISTÓRICO
    # --------------------------------------------------------

    contagem = {
        "IMPORTANTE": 0,
        "ATENÇÃO": 0,
        "INFORMATIVO": 0
    }

    for item in historico["publicacoes"]:

        importancia = item.get(
            "importancia",
            "INFORMATIVO"
        )

        if importancia in contagem:

            contagem[
                importancia
            ] += 1

    print()
    print(
        "Total armazenado no histórico:",
        len(
            historico["publicacoes"]
        )
    )

    print(
        "IMPORTANTE:",
        contagem["IMPORTANTE"]
    )

    print(
        "ATENÇÃO:",
        contagem["ATENÇÃO"]
    )

    print(
        "INFORMATIVO:",
        contagem["INFORMATIVO"]
    )

    print()
    print(
        "SST Radar finalizado."
    )


# ============================================================
# INÍCIO
# ============================================================

if __name__ == "__main__":

    executar()
