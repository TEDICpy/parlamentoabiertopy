from scrapping.silpy_scrapper import SilpyScrapper
from scrapping.senadores_scrapper import SenadoresScrapper
from scrapping.diputados_scrapper import DiputadosScrapper

if __name__ == "__main__":
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

