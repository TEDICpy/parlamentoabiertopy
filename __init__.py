from silpy_scrapper import SilpyScrapper
from senadores_scrapper import SenadoresScrapper
from diputados_scrapper import DiputadosScrapper


if __name__ == "__main__":
    senadores_scrapper = SilpyScrapper()
    diputadossc_scrapper = SilpyScrapper()

    senadores_scrapper.get_members_data('S')
    senadores_scrapper.close_navigator()

    diputadossc_scrapper.get_members_data('D')
    diputadossc_scrapper.close_navigator()

    scrapper = SenadoresScrapper()
    scrapper.extract_senators_data()
    scrapper.get_all_articles()


