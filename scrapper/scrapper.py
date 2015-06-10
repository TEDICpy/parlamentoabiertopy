import click

from scrapper.silpy_scrapper import SilpyScrapper
from scrapper.senadores_scrapper import SenadoresScrapper
from scrapper.diputados_scrapper import DiputadosScrapper


@click.group()
def cli():
    pass

@click.command(help='extrae datos de senadores y diputados')
def all():
    print 'corriendo todos los scrappers'
    silpy_senadores = SilpyScrapper()
    silpy_diputados = SilpyScrapper()

    silpy_senadores.get_members_data('S')
    silpy_senadores.close_navigator()

    silpy_diputados.get_members_data('D')
    silpy_diputados.close_navigator()

    senadores_scrapper = SenadoresScrapper()
    senadores_scrapper.get_all_articles()
    senadores_scrapper.extract_senators_data()

    diputados_scrapper = DiputadosScrapper()
    diputados_scrapper.get_members_data()

@click.command(help='extrae solo los datos de los senadores')
def senadores():
    print 'secrapping senadores'
    silpy_senadores = SilpyScrapper()
    silpy_senadores.get_members_data('S')
    silpy_senadores.close_navigator()
    senadores_scrapper = SenadoresScrapper()
    senadores_scrapper.extract_senators_data()
    #senadores_scrapper.get_all_articles()


@click.command(help="extrae solo los datos de los diputados")
def diputados():
    print 'scrapping diputados'
    silpy_diputados = SilpyScrapper()
    silpy_diputados.get_members_data('D')
    silpy_diputados.close_navigator()
    diputados_scrapper = DiputadosScrapper()
    diputados_scrapper.get_members_data()

cli.add_command(all)
cli.add_command(senadores)
cli.add_command(diputados)


if __name__ == "__main__":
    cli()
