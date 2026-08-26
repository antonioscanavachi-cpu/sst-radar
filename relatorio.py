import json
from datetime import datetime

ARQUIVO_HISTORICO = "historico.json"
ARQUIVO_RELATORIO = "relatorio_sst.md"


def carregar_historico():

    try:
        with open(
            ARQUIVO_HISTORICO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    except Exception:

        return {"publicacoes": []}


def gerar_relatorio():

    historico = carregar_historico()

    publicacoes = historico.get(
        "publicacoes",
        []
    )

    # Ordena pelas publicações mais recentes
    publicacoes = sorted(
        publicacoes,
        key=lambda x: x.get(
            "data_coleta",
            ""
        ),
        reverse=True
    )

    agora = datetime.now()

    linhas = []

    linhas.append(
        "# 📡 SST RADAR"
    )

    linhas.append("")

    linhas.append(
        "## Relatório de monitoramento"
    )

    linhas.append("")

    linhas.append(
        "**Gerado em:** "
        + agora.strftime(
            "%d/%m/%Y %H:%M:%S"
        )
    )

    linhas.append("")

    linhas.append(
        "**Total de registros:** "
        + str(len(publicacoes))
    )

    linhas.append("")

    linhas.append(
        "---"
    )

    linhas.append("")

    # ========================================================
    # SEPARAR POR IMPORTÂNCIA
    # ========================================================

    importantes = [
        p for p in publicacoes
        if p.get("importancia")
        == "IMPORTANTE"
    ]

    atencao = [
        p for p in publicacoes
        if p.get("importancia")
        == "ATENÇÃO"
    ]

    informativas = [
        p for p in publicacoes
        if p.get("importancia")
        == "INFORMATIVO"
    ]

    # ========================================================
    # RESUMO
    # ========================================================

    linhas.append(
        "## 📊 Resumo"
    )

    linhas.append("")

    linhas.append(
        f"- 🔴 Importantes: {len(importantes)}"
    )

    linhas.append(
        f"- 🟠 Atenção: {len(atencao)}"
    )

    linhas.append(
        f"- 🔵 Informativas: {len(informativas)}"
    )

    linhas.append("")

    # ========================================================
    # FUNÇÃO PARA MOSTRAR PUBLICAÇÕES
    # ========================================================

    def adicionar_secao(
        titulo,
        lista
    ):

        if not lista:
            return

        linhas.append(
            f"## {titulo}"
        )

        linhas.append("")

        for item in lista[:30]:

            linhas.append(
                "### "
                + item.get(
                    "titulo",
                    "Sem título"
                )
            )

            linhas.append("")

            linhas.append(
                "**Fonte:** "
                + item.get(
                    "fonte",
                    "Não informado"
                )
            )

            linhas.append("")

            temas = item.get(
                "temas",
                []
            )

            if temas:

                linhas.append(
                    "**Temas:** "
                    + ", ".join(temas)
                )

                linhas.append("")

            linhas.append(
                "**Importância:** "
                + item.get(
                    "importancia",
                    "Não classificada"
                )
            )

            linhas.append("")

            linhas.append(
                "**Link:** "
                + item.get(
                    "url",
                    ""
                )
            )

            linhas.append("")

            linhas.append("---")

            linhas.append("")

    # ========================================================
    # PUBLICAÇÕES
    # ========================================================

    adicionar_secao(
        "🔴 Publicações importantes",
        importantes
    )

    adicionar_secao(
        "🟠 Publicações que merecem atenção",
        atencao
    )

    adicionar_secao(
        "🔵 Publicações informativas",
        informativas
    )

    # ========================================================
    # SALVAR
    # ========================================================

    with open(
        ARQUIVO_RELATORIO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(
            "\n".join(linhas)
        )

    print()
    print(
        "Relatório criado com sucesso."
    )

    print(
        "Arquivo:",
        ARQUIVO_RELATORIO
    )


if __name__ == "__main__":

    gerar_relatorio()
