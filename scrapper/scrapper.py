import click

from scrapper.silpy_scrapper import SilpyScrapper
from scrapper.senadores_scrapper import SenadoresScrapper
from scrapper.diputados_scrapper import DiputadosScrapper

from mapper.popit_mapper import map_popit
from mapper.billit_mapper import map_billit

@click.group()
def cli():
    pass

@click.command(help='extrae datos de senadores y diputados')
def all():
    print 'corriendo todos los scrappers'
    #senadores 
    silpy_senadores = SilpyScrapper()
    silpy_senadores.get_members_data('S')
    silpy_senadores.close_navigator()    
    senadores_scrapper = SenadoresScrapper()
    senadores_scrapper.get_all_articles()
    senadores_scrapper.extract_senators_data()
    #diputados
    silpy_diputados = SilpyScrapper()    
    silpy_diputados.get_members_data('D')
    silpy_diputados.close_navigator()
    diputados_scrapper = DiputadosScrapper()
    diputados_scrapper.get_members_data()

@click.command(help='Extrae solo los datos de los senadores.')
@click.option('--no-silpy', is_flag=True, help="No descarga datos del silpy.")
def senadores(no_silpy=False):
    print 'scrapping senadores'
    if not no_silpy:
        silpy_senadores = SilpyScrapper()
        silpy_senadores.get_members_data('S')
        silpy_senadores.close_navigator()

    senadores_scrapper = SenadoresScrapper()
    senadores_scrapper.extract_senators_data()
    #senadores_scrapper.get_all_articles()

@click.command(help="Extrae solo los datos de los diputados.")
@click.option('--no-silpy', is_flag=True, help="No descarga datos del silpy.")
def diputados(no_silpy=False):
    print 'scrapping diputados'
    if not no_silpy:
        silpy_diputados = SilpyScrapper()
        silpy_diputados.get_members_data('D')
        silpy_diputados.close_navigator()

    diputados_scrapper = DiputadosScrapper()
    diputados_scrapper.get_members_data()

@click.command(help="Exporta los datos a popit.")
def map_persons():
    print 'Exportando a popit.'
    map_popit()
    
@click.command(help="Exporta los datos a Bill-it.")
def map_bills():
    print 'Exportando a Bill-it.'
    map_billit()
    
@click.command(help="descarga los proyectos de leyes")
@click.option('--origin', default='all', help="Origen de datos, 'all' para todos," +
              " 's' para senadores y 'd' para diputados.")
@click.option('--new', is_flag=True, help="Descarga solo nuevos projectos de ley. Disponible solo para 'all'.")
@click.option('--no-files', is_flag=True, help="No descarga los archivos relacionados.")
def bills(origin='all', new=False, no_files=False):
    if origin == 'all':
        silpy_scrapper = SilpyScrapper()
        silpy_scrapper.download_all_bills(new, no_files)
    elif origin == 's':
        silpy_senadores = SilpyScrapper()
        silpy_senadores.update_members_bills_from_db('S')
    elif origin == 'd':
        silpy_diputados = SilpyScrapper()
        silpy_diputados.update_members_bills_from_db('D')

        
@click.command(help="Actualiza los proyectos de ley.")
def update_bills():
    print 'Actualizando Proyectos de Ley'
    silpy = SilpyScrapper()
    silpy.update_bills()
    
    
cli.add_command(all)
cli.add_command(senadores)
cli.add_command(diputados)
cli.add_command(map_persons)
cli.add_command(map_bills)
cli.add_command(bills)
cli.add_command(update_bills)

if __name__ == "__main__":
    cli()
