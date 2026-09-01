import json

ARQUIVO_HISTORICO = "historico.json"

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

def eh_pagina_institucional(titulo, url=""):

    titulo_lower = titulo.lower().strip()
    url_lower = url.lower().strip()

    paginas = [
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
        "esocial",
        "sindicatos",
        "cadastro de entidades",
        "central sindical",
        "contribuição sindical",
        "mediação",
        "painel de relações do trabalho",
        "categorias",
        "galeria de aplicativos",
    ]

    if titulo_lower in paginas:
        return True

    if (
        titulo_lower.startswith("consultar ")
        or titulo_lower.startswith("consulta ")
    ):
        return True

    # Páginas permanentes das NRs
    # Ex.: "NR-1 - DISPOSIÇÕES GERAIS..."
    if titulo_lower.startswith("nr-"):

        partes = titulo_lower.split(" - ", 1)

        if len(partes) == 2:

            numero_nr = partes[0].replace(
                "nr-",
                ""
            ).strip()

            if numero_nr.isdigit():
                return True

    if "portarias de designação" in titulo_lower:
        return True

    if "designação de fiscais" in titulo_lower:
        return True

    # Caminhos que normalmente indicam páginas institucionais
    caminhos_institucionais = [
        "/categorias",
        "/apps/",
        "/composicao/orgaos-colegiados/",
        "/servicos/sindicatos",
    ]

    for caminho in caminhos_institucionais:

        if caminho in url_lower:
            return True

    return False

def executar():

    print("=" * 70)
    print("RECLASSIFICAÇÃO DO HISTÓRICO SST")
    print("=" * 70)

    with open(
        ARQUIVO_HISTORICO,
        "r",
        encoding="utf-8"
    ) as arquivo:

        historico = json.load(arquivo)

    publicacoes = historico.get(
        "publicacoes",
        []
    )

    print()
    print(
        "Registros encontrados:",
        len(publicacoes)
    )

    contagem = {
        "IMPORTANTE": 0,
        "ATENÇÃO": 0,
        "INFORMATIVO": 0
    }

    # ========================================================
    # REMOVER PÁGINAS INSTITUCIONAIS DO HISTÓRICO
    # ========================================================

    historico_original = len(publicacoes)

    publicacoes_filtradas = []

    removidas = 0

    for item in publicacoes:

        titulo = item.get(
            "titulo",
            ""
        )

        if eh_pagina_institucional(
            titulo,
            item.get("url", "")
        ):

            removidas += 1

            continue

        publicacoes_filtradas.append(
            item
        )

    historico["publicacoes"] = (
        publicacoes_filtradas
    )

    publicacoes = (
        historico["publicacoes"]
    )

    for item in publicacoes:

        titulo = item.get(
            "titulo",
            ""
        )

        temas = item.get(
            "temas",
            []
        )

        nova_classificacao = (
            classificar_importancia(
                titulo,
                temas
            )
        )

        item["importancia"] = (
            nova_classificacao
        )

        contagem[
            nova_classificacao
        ] += 1

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

    print()
    print("RECLASSIFICAÇÃO CONCLUÍDA")
    print()

    print(
        "Páginas institucionais removidas:",
        removidas
    )

    print(
        "Registros mantidos:",
        len(publicacoes)
    )

    print()
    
    print(
        "🔴 Importantes:",
        contagem["IMPORTANTE"]
    )

    print(
        "🟠 Atenção:",
        contagem["ATENÇÃO"]
    )

    print(
        "🔵 Informativas:",
        contagem["INFORMATIVO"]
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    executar()
