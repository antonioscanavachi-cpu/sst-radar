import feedparser
from datetime import datetime

FONTES = {
    "MTE - SST": "https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/seguranca-e-saude-no-trabalho",
    "Fundacentro": "https://www.gov.br/fundacentro/pt-br",
}

PALAVRAS_CHAVE = [
    "segurança do trabalho",
    "saúde do trabalho",
    "saúde e segurança",
    "norma regulamentadora",
    "NR-01",
    "NR-1",
    "NR-17",
    "ergonomia",
    "AET",
    "PGR",
    "GRO",
    "riscos psicossociais",
    "acidente de trabalho",
    "doença ocupacional",
    "CAT",
    "eSocial",
]

print("=" * 60)
print("SST RADAR")
print("Monitoramento de Saúde e Segurança do Trabalho")
print("=" * 60)
print("Execução:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

print("\nPalavras-chave monitoradas:")

for palavra in PALAVRAS_CHAVE:
    print(" -", palavra)

print("\nFontes configuradas:")

for nome, endereco in FONTES.items():
    print(" -", nome)
    print("   ", endereco)

print("\nSST Radar iniciado.")
