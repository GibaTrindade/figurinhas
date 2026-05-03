import unicodedata

from .models import ColecaoFigurinha, Figurinha, SecaoEspecial, Selecao


PAGE_WIDTH = 842
PAGE_HEIGHT = 595


def exportar_faltantes_pdf(user):
    linhas = _linhas_album(user)
    pdf = _Pdf()
    pdf.text(28, 568, 'Album Copa 2026 - Faltantes', 14, bold=True)
    pdf.text(650, 568, f'Usuario: {_ascii(user.username)}', 8)
    pdf.text(28, 552, 'Faltantes: circulos vermelhos vazados  |  Repetidas para troca: circulos amarelos preenchidos', 7)

    y = 535
    row_height = 10
    for linha in linhas:
        pdf.set_stroke(0.86, 0.88, 0.91)
        pdf.line(24, y - 3.8, 818, y - 3.8)
        pdf.text(28, y - 1.7, linha['nome'], 6.7, bold=True)
        pdf.text(100, y - 1.7, linha['codigo'], 6.5)

        x = 132
        for numero in linha['faltantes']:
            pdf.circle(x, y, 3.4, stroke=(0.82, 0.12, 0.12), fill=None)
            pdf.text_center(x, y - 1.7, str(numero), 4.4, color=(0.62, 0.05, 0.05))
            x += 10.5

        if linha['repetidas']:
            pdf.text(470, y - 1.7, 'Rep.', 6.2, color=(0.38, 0.28, 0))
            x = 496
            for numero, quantidade in linha['repetidas']:
                pdf.circle(x, y, 3.6, stroke=(0.78, 0.56, 0), fill=(1, 0.82, 0.18))
                pdf.text_center(x, y - 1.7, str(numero), 4.3, color=(0.20, 0.15, 0))
                if quantidade > 1:
                    pdf.text(x + 4.2, y - 4.2, f'x{quantidade}', 3.8, color=(0.20, 0.15, 0))
                x += 13.5

        y -= row_height

    return pdf.render()


def _linhas_album(user):
    colecoes = {
        colecao.figurinha_id: colecao.quantidade
        for colecao in ColecaoFigurinha.objects.filter(user=user).select_related('figurinha')
    }
    linhas = []

    for selecao in Selecao.objects.order_by('grupo', 'ordem', 'nome'):
        figurinhas = Figurinha.objects.filter(selecao=selecao).order_by('ordem')
        linhas.append(_linha(selecao.nome, selecao.codigo_album, figurinhas, colecoes))

    for secao in SecaoEspecial.objects.order_by('ordem', 'nome'):
        figurinhas = Figurinha.objects.filter(secao_especial=secao).order_by('ordem')
        linhas.append(_linha(secao.nome, secao.codigo_album, figurinhas, colecoes))

    return linhas


def _linha(nome, codigo, figurinhas, colecoes):
    faltantes = []
    repetidas = []
    for figurinha in figurinhas:
        quantidade = colecoes.get(figurinha.id, 0)
        if quantidade == 0:
            faltantes.append(figurinha.ordem)
        elif quantidade > 1:
            repetidas.append((figurinha.ordem, quantidade - 1))

    return {
        'nome': _ascii(nome)[:22],
        'codigo': _ascii(codigo),
        'faltantes': faltantes,
        'repetidas': repetidas,
    }


def _ascii(texto):
    return unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii')


class _Pdf:
    def __init__(self):
        self.commands = []
        self.font = 'F1'

    def set_stroke(self, r, g, b):
        self.commands.append(f'{r:.3f} {g:.3f} {b:.3f} RG')

    def set_fill(self, r, g, b):
        self.commands.append(f'{r:.3f} {g:.3f} {b:.3f} rg')

    def text(self, x, y, value, size, bold=False, color=(0, 0, 0)):
        font = 'F2' if bold else 'F1'
        self.set_fill(*color)
        self.commands.append(f'BT /{font} {size:.2f} Tf {x:.2f} {y:.2f} Td ({_escape(value)}) Tj ET')

    def text_center(self, x, y, value, size, color=(0, 0, 0)):
        width = len(str(value)) * size * 0.28
        self.text(x - width, y, value, size, color=color)

    def line(self, x1, y1, x2, y2):
        self.commands.append(f'{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S')

    def circle(self, x, y, radius, stroke=(0, 0, 0), fill=None):
        c = radius * 0.5522847498
        self.set_stroke(*stroke)
        if fill:
            self.set_fill(*fill)
        self.commands.append(
            f'{x:.2f} {y + radius:.2f} m '
            f'{x + c:.2f} {y + radius:.2f} {x + radius:.2f} {y + c:.2f} {x + radius:.2f} {y:.2f} c '
            f'{x + radius:.2f} {y - c:.2f} {x + c:.2f} {y - radius:.2f} {x:.2f} {y - radius:.2f} c '
            f'{x - c:.2f} {y - radius:.2f} {x - radius:.2f} {y - c:.2f} {x - radius:.2f} {y:.2f} c '
            f'{x - radius:.2f} {y + c:.2f} {x - c:.2f} {y + radius:.2f} {x:.2f} {y + radius:.2f} c '
            f'{"B" if fill else "S"}'
        )

    def render(self):
        stream = '\n'.join(self.commands).encode('latin-1')
        objects = [
            b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>',
            b'<< /Length ' + str(len(stream)).encode('ascii') + b' >>\nstream\n' + stream + b'\nendstream',
        ]
        pdf = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f'{index} 0 obj\n'.encode('ascii'))
            pdf.extend(obj)
            pdf.extend(b'\nendobj\n')
        xref = len(pdf)
        pdf.extend(f'xref\n0 {len(objects) + 1}\n'.encode('ascii'))
        pdf.extend(b'0000000000 65535 f \n')
        for offset in offsets[1:]:
            pdf.extend(f'{offset:010d} 00000 n \n'.encode('ascii'))
        pdf.extend(
            f'trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode('ascii')
        )
        return bytes(pdf)


def _escape(value):
    return _ascii(value).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
