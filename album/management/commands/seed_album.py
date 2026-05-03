from django.core.management.base import BaseCommand

from album.models import CategoriaFigurinha, Figurinha, Selecao


class Command(BaseCommand):
    help = 'Cria dados ficticios baseados nas 48 selecoes da Copa 2026.'

    def handle(self, *args, **options):
        categorias = {}
        for nome in ['Escudo', 'Time', 'Jogador']:
            categorias[nome], _ = CategoriaFigurinha.objects.get_or_create(nome=nome)

        CategoriaFigurinha.objects.exclude(nome__in=categorias).delete()

        selecoes = [
            ('Mexico', 'A', 'mx', 'MEX'),
            ('Africa do Sul', 'A', 'za', 'RSA'),
            ('Coreia do Sul', 'A', 'kr', 'KOR'),
            ('Tchequia', 'A', 'cz', 'CZE'),
            ('Canada', 'B', 'ca', 'CAN'),
            ('Bosnia e Herzegovina', 'B', 'ba', 'BIH'),
            ('Qatar', 'B', 'qa', 'QAT'),
            ('Suica', 'B', 'ch', 'SUI'),
            ('Brasil', 'C', 'br', 'BRA'),
            ('Marrocos', 'C', 'ma', 'MAR'),
            ('Haiti', 'C', 'ht', 'HAI'),
            ('Escocia', 'C', 'gb-sct', 'SCO'),
            ('Estados Unidos', 'D', 'us', 'USA'),
            ('Paraguai', 'D', 'py', 'PAR'),
            ('Australia', 'D', 'au', 'AUS'),
            ('Turquia', 'D', 'tr', 'TUR'),
            ('Alemanha', 'E', 'de', 'GER'),
            ('Curacao', 'E', 'cw', 'CUW'),
            ('Costa do Marfim', 'E', 'ci', 'CIV'),
            ('Equador', 'E', 'ec', 'ECU'),
            ('Paises Baixos', 'F', 'nl', 'NED'),
            ('Japao', 'F', 'jp', 'JPN'),
            ('Suecia', 'F', 'se', 'SWE'),
            ('Tunisia', 'F', 'tn', 'TUN'),
            ('Belgica', 'G', 'be', 'BEL'),
            ('Egito', 'G', 'eg', 'EGY'),
            ('Ira', 'G', 'ir', 'IRN'),
            ('Nova Zelandia', 'G', 'nz', 'NZL'),
            ('Espanha', 'H', 'es', 'ESP'),
            ('Cabo Verde', 'H', 'cv', 'CPV'),
            ('Arabia Saudita', 'H', 'sa', 'KSA'),
            ('Uruguai', 'H', 'uy', 'URU'),
            ('Franca', 'I', 'fr', 'FRA'),
            ('Senegal', 'I', 'sn', 'SEN'),
            ('Iraque', 'I', 'iq', 'IRQ'),
            ('Noruega', 'I', 'no', 'NOR'),
            ('Argentina', 'J', 'ar', 'ARG'),
            ('Argelia', 'J', 'dz', 'ALG'),
            ('Austria', 'J', 'at', 'AUT'),
            ('Jordania', 'J', 'jo', 'JOR'),
            ('Portugal', 'K', 'pt', 'POR'),
            ('RD Congo', 'K', 'cd', 'COD'),
            ('Uzbequistao', 'K', 'uz', 'UZB'),
            ('Colombia', 'K', 'co', 'COL'),
            ('Inglaterra', 'L', 'gb-eng', 'ENG'),
            ('Croacia', 'L', 'hr', 'CRO'),
            ('Gana', 'L', 'gh', 'GHA'),
            ('Panama', 'L', 'pa', 'PAN'),
        ]

        numero = 1
        for ordem, (nome, grupo, bandeira_codigo, codigo_album) in enumerate(selecoes, start=1):
            selecao, _ = Selecao.objects.get_or_create(
                nome=nome,
                defaults={
                    'grupo': grupo,
                    'bandeira_codigo': bandeira_codigo,
                    'codigo_album': codigo_album,
                    'ordem': ordem,
                },
            )
            selecao.grupo = grupo
            selecao.bandeira_emoji = ''
            selecao.bandeira_codigo = bandeira_codigo
            selecao.codigo_album = codigo_album
            selecao.ordem = ordem
            selecao.save()

            figurinhas = []
            jogador = 1
            for posicao in range(1, 21):
                if posicao == 1:
                    figurinhas.append(('Escudo', f'Escudo {nome}', True))
                elif posicao == 13:
                    figurinhas.append(('Time', f'Time {nome}', False))
                else:
                    figurinhas.append(('Jogador', f'Jogador {jogador:02d} {nome}', False))
                    jogador += 1

            for posicao, (categoria_nome, figurinha_nome, especial) in enumerate(figurinhas, start=1):
                Figurinha.objects.update_or_create(
                    numero=numero,
                    defaults={
                        'nome': figurinha_nome,
                        'selecao': selecao,
                        'categoria': categorias[categoria_nome],
                        'descricao': 'Figurinha ficticia para testar o MVP.',
                        'especial': especial,
                        'ordem': posicao,
                    },
                )
                numero += 1

        self.stdout.write(self.style.SUCCESS('Dados iniciais criados com 48 selecoes e 960 figurinhas.'))
