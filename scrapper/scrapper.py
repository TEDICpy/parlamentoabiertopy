import click

from scrapper.silpy_scrapper import SilpyScrapper
from scrapper.senadores_scrapper import SenadoresScrapper
from scrapper.diputados_scrapper import DiputadosScrapper

from mapper.popit_mapper import map_popit

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

@click.command(help="Exporta los datos a popit")
def map_popit_data():
    print 'Exportando a popit'
    map_popit()
    
@click.command(help="descarga los proyectos de leyes")
@click.option('--origin', default='all', help="origen de datos, 'all' para todos," +
              " 's' para senadores y 'd' para diputados")
def bills(origin):
    
    if origin == 'all':
        silpy_senadores = SilpyScrapper()
        silpy_senadores.update_members_bills_from_db('S')
        silpy_diputados = SilpyScrapper()
        silpy_diputados.update_members_bills_from_db('D')
    elif origin == 's':
        silpy_senadores = SilpyScrapper()
        silpy_senadores.update_members_bills_from_db('S')
    elif origin == 'd':
        silpy_diputados = SilpyScrapper()
        silpy_diputados.update_members_bills_from_db('D')
    
cli.add_command(all)
cli.add_command(senadores)
cli.add_command(diputados)
cli.add_command(map_popit_data)
cli.add_command(bills)

if __name__ == "__main__":
    cli()
