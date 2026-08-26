import json

ARQUIVO_HISTORICO = "historico.json"


def classificar_importancia(titulo, temas):

    texto = (
        titulo + " " +
        " ".join(temas)
    ).lower()

    pontuacao = 0

    # Legislação e normas
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

    # GRO / PGR
    if "gro" in texto:
        pontuacao += 8

    if "pgr" in texto:
        pontuacao += 8

    if "gerenciamento de riscos" in texto:
        pontuacao += 8

    # Ergonomia
    if "ergonomia" in texto:
        pontuacao += 8

    if "ergonômica" in texto:
        pontuacao += 8

    if "ergonômico" in texto:
        pontuacao += 8

    if "aet" in texto:
        pontuacao += 8

    # Riscos psicossociais
    if "psicossocial" in texto:
        pontuacao += 10

    if "saúde mental" in texto:
        pontuacao += 7

    if "organização do trabalho" in texto:
        pontuacao += 6

    # Acidentes e doenças
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

    # Insalubridade / Periculosidade
    if "insalubridade" in texto:
        pontuacao += 7

    if "periculosidade" in texto:
        pontuacao += 7

    # eSocial
    if "esocial" in texto:
        pontuacao += 6

    if "s-2210" in texto:
        pontuacao += 8

    if "s-2220" in texto:
        pontuacao += 8

    if "s-2240" in texto:
        pontuacao += 8

    # Classificação
    if pontuacao >= 15:
        classificacao = "IMPORTANTE"

    elif pontuacao >= 8:
        classificacao = "ATENÇÃO"

    else:
        classificacao = "INFORMATIVO"

    return classificacao


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
