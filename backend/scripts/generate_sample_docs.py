"""
Gera documentos PDF de amostra para testar o pipeline RAG.
Simula o manual de produtos bancários de uma instituição fictícia.

Usage:
    python scripts/generate_sample_docs.py
    # Gera: docs/produtos_bancarios.pdf
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fpdf import FPDF


class BankingDocPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(30, 80, 160)
        self.cell(0, 8, "Banco Meridional S.A. - Guia de Produtos e Tarifas", align="C")
        self.set_text_color(0, 0, 0)
        self.ln(4)
        self.set_draw_color(30, 80, 160)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, f"Pagina {self.page_no()} | Vigencia: Jan/2026 | www.bancomeridional.com.br", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(230, 238, 255)
        self.set_text_color(20, 60, 140)
        self.cell(0, 9, f"  {title}", fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def subsection(self, title: str):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 50, 50)
        self.cell(0, 7, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def table_row(self, label: str, value: str, highlight: bool = False):
        if highlight:
            self.set_fill_color(245, 248, 255)
        else:
            self.set_fill_color(255, 255, 255)
        self.set_font("Helvetica", "", 10)
        self.cell(110, 7, f"  {label}", border=1, fill=True)
        self.set_font("Helvetica", "B", 10)
        self.cell(80, 7, f"  {value}", border=1, fill=True, ln=True)

    def table_header(self, col1: str, col2: str):
        self.set_fill_color(30, 80, 160)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.cell(110, 7, f"  {col1}", border=1, fill=True)
        self.cell(80, 7, f"  {col2}", border=1, fill=True, ln=True)
        self.set_text_color(0, 0, 0)

    def note(self, text: str):
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 5, f"* {text}")
        self.set_text_color(0, 0, 0)
        self.ln(2)


def generate(output_path: Path) -> None:
    pdf = BankingDocPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ------------------------------------------------------------------ #
    #  CAPA
    # ------------------------------------------------------------------ #
    pdf.ln(20)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 60, 140)
    pdf.cell(0, 12, "Banco Meridional S.A.", align="C", ln=True)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "Guia Completo de Produtos, Tarifas e Condicoes", align="C", ln=True)
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 7, "Vigencia: Janeiro a Dezembro de 2026", align="C", ln=True)
    pdf.ln(6)
    pdf.set_draw_color(30, 80, 160)
    pdf.set_line_width(1)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(
        0, 6,
        "Este documento contem informacoes sobre os produtos e servicos oferecidos pelo "
        "Banco Meridional S.A., incluindo taxas de juros, tarifas, requisitos de elegibilidade "
        "e condicoes gerais. As taxas apresentadas sao validas para o periodo de vigencia "
        "indicado e podem ser alteradas mediante aviso previo de 30 dias.",
        align="C",
    )
    pdf.set_text_color(0, 0, 0)

    # ------------------------------------------------------------------ #
    #  PAGINA 2 - EMPRESTIMO PESSOAL
    # ------------------------------------------------------------------ #
    pdf.add_page()
    pdf.section_title("1. Emprestimo Pessoal")

    pdf.body(
        "O Emprestimo Pessoal do Banco Meridional e uma linha de credito sem vinculacao "
        "de garantia real, disponivel para pessoas fisicas correntistas ha pelo menos 3 meses. "
        "O valor liberado e depositado diretamente na conta corrente do cliente em ate 1 dia util "
        "apos a aprovacao."
    )

    pdf.subsection("1.1 Taxas de Juros - Emprestimo Pessoal")
    pdf.body(
        "As taxas sao definidas com base no perfil de credito do cliente (score interno), "
        "no prazo escolhido e no relacionamento com o banco. Clientes com conta a mais de "
        "12 meses e domicilio bancario recebem reducao de 0,3 p.p. na taxa mensal."
    )

    pdf.table_header("Perfil do Cliente", "Taxa de Juros (a.m.)")
    pdf.table_row("Score A (800-1000) - Excelente", "1,49% a.m. (19,4% a.a.)", highlight=True)
    pdf.table_row("Score B (650-799) - Bom", "1,99% a.m. (26,6% a.a.)")
    pdf.table_row("Score C (500-649) - Regular", "2,79% a.m. (38,9% a.a.)", highlight=True)
    pdf.table_row("Score D (abaixo de 500) - Restrito", "3,49% a.m. (50,9% a.a.)")
    pdf.ln(3)

    pdf.subsection("1.2 Valores e Prazos")
    pdf.table_header("Parametro", "Condicao")
    pdf.table_row("Valor minimo do emprestimo", "R$ 1.000,00", highlight=True)
    pdf.table_row("Valor maximo do emprestimo", "R$ 80.000,00")
    pdf.table_row("Prazo minimo de pagamento", "12 meses", highlight=True)
    pdf.table_row("Prazo maximo de pagamento", "60 meses")
    pdf.table_row("Carencia disponivel", "Ate 90 dias para 1a parcela")
    pdf.ln(3)

    pdf.subsection("1.3 Requisitos de Elegibilidade")
    pdf.body(
        "Para solicitar o Emprestimo Pessoal, o cliente deve atender aos seguintes requisitos:\n"
        "- Ser pessoa fisica, maior de 18 anos, residente no Brasil\n"
        "- Possuir conta corrente ativa no Banco Meridional ha no minimo 3 meses\n"
        "- Nao possuir restricoes ativas no CPF (SPC, Serasa ou BACEN)\n"
        "- Renda mensal comprovada minima de R$ 1.500,00\n"
        "- Comprometimento de renda maximo de 30% (parcela/renda liquida)"
    )

    pdf.subsection("1.4 Documentacao Necessaria")
    pdf.body(
        "- Documento de identidade com foto (RG ou CNH)\n"
        "- CPF regularizado na Receita Federal\n"
        "- Comprovante de residencia com data de ate 90 dias\n"
        "- Comprovante de renda (contracheque, declaracao IR ou extrato bancario dos ultimos 3 meses)"
    )

    pdf.subsection("1.5 Multa e Mora por Atraso")
    pdf.table_header("Encargo", "Valor")
    pdf.table_row("Multa por atraso", "2% sobre o valor da parcela", highlight=True)
    pdf.table_row("Juros de mora", "1% a.m. (pro rata die)")
    pdf.table_row("Tarifa de cobranca (boleto)", "R$ 12,50 por boleto emitido", highlight=True)
    pdf.ln(3)

    pdf.note(
        "Nao ha cobranca de multa ou mora para atrasos de ate 3 dias uteis, desde que o "
        "cliente regularize o pagamento dentro desse prazo. A politica de tolerancia aplica-se "
        "somente uma vez por contrato."
    )

    # ------------------------------------------------------------------ #
    #  PAGINA 3 - CONTA POUPANCA E CONTA CORRENTE
    # ------------------------------------------------------------------ #
    pdf.add_page()
    pdf.section_title("2. Conta Poupanca")

    pdf.body(
        "A Conta Poupanca do Banco Meridional segue a remuneracao definida pelo Banco Central "
        "do Brasil. O rendimento e creditado mensalmente na data de aniversario da abertura da conta."
    )

    pdf.table_header("Parametro", "Condicao")
    pdf.table_row("Remuneracao (Selic <= 8,5% a.a.)", "70% da Selic + TR", highlight=True)
    pdf.table_row("Remuneracao (Selic > 8,5% a.a.)", "0,5% a.m. + TR")
    pdf.table_row("Saldo minimo para abertura", "Nao ha saldo minimo", highlight=True)
    pdf.table_row("Tarifa de manutencao", "Isenta")
    pdf.table_row("Limite de saques gratuitos/mes", "Ilimitado nos canais digitais", highlight=True)
    pdf.table_row("Garantia FGC", "Ate R$ 250.000,00 por CPF")
    pdf.ln(3)

    pdf.section_title("3. Conta Corrente")

    pdf.subsection("3.1 Planos Disponiveis")
    pdf.table_header("Plano", "Tarifa Mensal")
    pdf.table_row("Conta Digital (sem tarifas)", "R$ 0,00 - exclusivo app/internet", highlight=True)
    pdf.table_row("Conta Essencial", "R$ 19,90/mes")
    pdf.table_row("Conta Premium", "R$ 39,90/mes - servicos ilimitados", highlight=True)
    pdf.table_row("Conta Universitaria (ate 24 anos)", "R$ 0,00 por 12 meses")
    pdf.ln(3)

    pdf.subsection("3.2 Cheque Especial")
    pdf.body(
        "O limite do Cheque Especial e definido individualmente por analise de credito. "
        "A utilizacao e opcional e os juros sao cobrados apenas sobre o saldo utilizado."
    )
    pdf.table_header("Parametro", "Condicao")
    pdf.table_row("Taxa de juros maxima (regulamentacao BC)", "8% a.m.", highlight=True)
    pdf.table_row("Taxa praticada pelo Banco Meridional", "6,9% a.m.")
    pdf.table_row("Limite maximo disponivel", "Ate R$ 5.000,00")
    pdf.table_row("Carencia de utilizacao", "Sem carencia - juros diarios", highlight=True)
    pdf.ln(3)

    # ------------------------------------------------------------------ #
    #  PAGINA 4 - CREDITO IMOBILIARIO
    # ------------------------------------------------------------------ #
    pdf.add_page()
    pdf.section_title("4. Credito Imobiliario")

    pdf.body(
        "O Credito Imobiliario do Banco Meridional financia a aquisicao, construcao ou reforma "
        "de imoveis residenciais e comerciais. O financiamento pode ser feito pelo Sistema Financeiro "
        "de Habitacao (SFH) ou pelo Sistema de Financiamento Imobiliario (SFI), conforme o valor do imovel."
    )

    pdf.subsection("4.1 Taxas de Juros - Credito Imobiliario")
    pdf.table_header("Modalidade / Indexador", "Taxa de Juros")
    pdf.table_row("SFH - Taxa fixa (ate R$ 1,5 mi)", "10,5% a.a. + TR", highlight=True)
    pdf.table_row("SFH - IPCA (ate R$ 1,5 mi)", "IPCA + 4,5% a.a.")
    pdf.table_row("SFI - Taxa fixa (acima de R$ 1,5 mi)", "11,2% a.a. + TR", highlight=True)
    pdf.table_row("SFI - IPCA (acima de R$ 1,5 mi)", "IPCA + 5,2% a.a.")
    pdf.table_row("Construcao propria (autofin.)", "11,0% a.a. + TR")
    pdf.ln(3)

    pdf.subsection("4.2 Condicoes Gerais")
    pdf.table_header("Parametro", "Condicao")
    pdf.table_row("Entrada minima", "20% do valor do imovel", highlight=True)
    pdf.table_row("Prazo maximo de financiamento", "360 meses (30 anos)")
    pdf.table_row("Percentual maximo financiado", "80% do valor de avaliacao", highlight=True)
    pdf.table_row("Comprometimento de renda maximo", "30% da renda liquida mensal")
    pdf.table_row("Seguro MIP (morte e invalidez)", "Obrigatorio - incluso na parcela", highlight=True)
    pdf.table_row("Seguro DFI (danos fisicos)", "Obrigatorio - incluso na parcela")
    pdf.ln(3)

    pdf.note(
        "Para clientes com relacionamento acima de 5 anos e domicilio bancario, "
        "oferecemos reducao de 0,5 p.p. na taxa de juros do financiamento imobiliario, "
        "mediante analise e aprovacao de credito."
    )

    # ------------------------------------------------------------------ #
    #  PAGINA 5 - CARTAO DE CREDITO
    # ------------------------------------------------------------------ #
    pdf.add_page()
    pdf.section_title("5. Cartao de Credito")

    pdf.subsection("5.1 Modalidades Disponiveis")
    pdf.table_header("Cartao", "Anuidade")
    pdf.table_row("Meridional Basico (Visa Classic)", "R$ 0,00 - sem anuidade", highlight=True)
    pdf.table_row("Meridional Gold (Mastercard Gold)", "R$ 199,80/ano (12x R$ 16,65)")
    pdf.table_row("Meridional Platinum (Visa Platinum)", "R$ 399,60/ano (12x R$ 33,30)", highlight=True)
    pdf.table_row("Meridional Infinite (MC Black)", "R$ 799,20/ano - renda min. R$ 15k")
    pdf.ln(3)

    pdf.subsection("5.2 Taxas de Juros - Cartao de Credito")
    pdf.table_header("Modalidade", "Taxa")
    pdf.table_row("Rotativo total (fatura nao paga)", "15,9% a.m. (339% a.a.)", highlight=True)
    pdf.table_row("Rotativo parcelado (minimo 15%)", "8,9% a.m. (182% a.a.)")
    pdf.table_row("Parcelamento de fatura", "3,99% a.m. (60% a.a.)", highlight=True)
    pdf.table_row("Saque no credito (avanco)", "12,5% a.m. + R$ 10,00 por saque")
    pdf.ln(3)

    pdf.note(
        "O pagamento minimo da fatura corresponde a 15% do valor total. "
        "O uso do rotativo por mais de 2 meses consecutivos gera notificacao automatica "
        "para renegociacao com condicoes especiais."
    )

    # ------------------------------------------------------------------ #
    #  PAGINA 6 - INVESTIMENTOS
    # ------------------------------------------------------------------ #
    pdf.add_page()
    pdf.section_title("6. Produtos de Investimento")

    pdf.subsection("6.1 CDB - Certificado de Deposito Bancario")
    pdf.table_header("Prazo / Liquidez", "Rentabilidade")
    pdf.table_row("CDB 30 dias (liquidez diaria)", "100% do CDI", highlight=True)
    pdf.table_row("CDB 90 dias", "103% do CDI")
    pdf.table_row("CDB 180 dias", "106% do CDI", highlight=True)
    pdf.table_row("CDB 360 dias", "110% do CDI")
    pdf.table_row("CDB 720 dias (sem liquidez)", "115% do CDI", highlight=True)
    pdf.table_row("Aplicacao minima", "R$ 500,00")
    pdf.ln(3)

    pdf.subsection("6.2 LCI e LCA (Isencao de IR para PF)")
    pdf.table_header("Produto / Prazo", "Rentabilidade")
    pdf.table_row("LCI 90 dias (minimo legal)", "88% do CDI", highlight=True)
    pdf.table_row("LCI 180 dias", "91% do CDI")
    pdf.table_row("LCA 90 dias (minimo legal)", "87% do CDI", highlight=True)
    pdf.table_row("LCA 180 dias", "90% do CDI")
    pdf.table_row("Aplicacao minima LCI/LCA", "R$ 5.000,00")
    pdf.ln(3)

    pdf.note(
        "LCI (Letra de Credito Imobiliario) e LCA (Letra de Credito do Agronegocio) "
        "sao isentas de Imposto de Renda para pessoas fisicas. "
        "Garantidas pelo FGC ate R$ 250.000,00 por CPF por instituicao."
    )

    pdf.subsection("6.3 Tesouro Direto (intermediacao)")
    pdf.body(
        "O Banco Meridional oferece acesso ao Tesouro Direto com taxa de custodia de 0% a.a. "
        "(isencao total da tarifa de intermediacao). Disponivel para todos os clientes correntistas "
        "com investimento minimo de R$ 30,00."
    )

    # ------------------------------------------------------------------ #
    #  PAGINA 7 - SEGUROS E INFORMACOES GERAIS
    # ------------------------------------------------------------------ #
    pdf.add_page()
    pdf.section_title("7. Seguros")

    pdf.table_header("Produto", "Premio Mensal a partir de")
    pdf.table_row("Seguro de Vida Individual", "R$ 29,90/mes", highlight=True)
    pdf.table_row("Seguro Residencial", "R$ 39,90/mes")
    pdf.table_row("Seguro Auto (parceria Porto Seguro)", "Consultar tabela vigente", highlight=True)
    pdf.table_row("Seguro Prestamista (protecao parcelas)", "0,5% do saldo devedor/mes")
    pdf.ln(3)

    pdf.section_title("8. Atendimento e Canais")

    pdf.body(
        "O Banco Meridional oferece os seguintes canais de atendimento:\n"
        "- Aplicativo Meridional (iOS e Android): disponivel 24h\n"
        "- Internet Banking: www.bancomeridional.com.br\n"
        "- Central de Atendimento: 0800 720 4321 (24h, gratuito)\n"
        "- Atendimento Exclusivo (Premium e Infinite): 4004-8765\n"
        "- Agencias fisicas: segunda a sexta, das 10h as 16h\n"
        "- WhatsApp Meridional: (11) 91234-5678"
    )

    pdf.section_title("9. Ouvidoria e SAC")

    pdf.body(
        "SAC (Servico de Atendimento ao Consumidor): 0800 720 0001 - 24h, todos os dias.\n"
        "Ouvidoria: 0800 720 0002 - segunda a sexta, das 8h as 18h.\n\n"
        "O prazo de resposta da Ouvidoria e de ate 10 dias uteis, conforme regulamentacao "
        "do Banco Central do Brasil."
    )

    pdf.note(
        "Este documento e meramente ilustrativo e criado para fins de demonstracao de "
        "sistema RAG (Retrieval-Augmented Generation). As taxas, produtos e condicoes "
        "apresentados sao ficticioas e nao representam uma oferta real de servicos financeiros."
    )

    # Salvar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    print(f"PDF gerado: {output_path} ({output_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    output = Path(__file__).parent.parent.parent / "docs" / "produtos_bancarios.pdf"
    generate(output)
