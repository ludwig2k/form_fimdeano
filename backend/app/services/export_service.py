import io

from openpyxl import Workbook
from openpyxl.styles import Font

from .. import models
from ..cpf import format_cpf

COLUNAS = [
    "Nome completo",
    "CPF",
    "E-mail",
    "Unidade de lotação",
    "Anexo",
    "Status",
    "Data da inscrição",
    "Check-in realizado em",
]


def gerar_planilha_inscricoes(inscricoes: list[models.Inscricao]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Inscrições"

    ws.append(COLUNAS)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for inscricao in inscricoes:
        ws.append([
            inscricao.nome_completo,
            format_cpf(inscricao.cpf),
            inscricao.email,
            inscricao.unidade.nome,
            inscricao.anexo.nome,
            inscricao.status.value,
            inscricao.created_at.strftime("%d/%m/%Y %H:%M"),
            inscricao.checked_in_at.strftime("%d/%m/%Y %H:%M") if inscricao.checked_in_at else "",
        ])

    for column_cells in ws.columns:
        largura = max(len(str(cell.value)) for cell in column_cells if cell.value is not None)
        ws.column_dimensions[column_cells[0].column_letter].width = min(largura + 2, 40)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
