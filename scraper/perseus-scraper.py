#!/usr/bin/env python3

import os
import sys
import bs4
import requests
import logging
import time

# Iniciamos la clase Perseus()
class Perseus():
    # Iniciamos el constructor de la clase Perseus()
    def __init__(self):
        self.__perseusAPI_capabilities = 'http://www.perseus.tufts.edu/hopper/CTS?request=GetCapabilities'
        self.__greekMarker = 'greekLit:'

    urn_codes = []

    # Al llamar a este método, se recopilan todos los códigos URN correspondientes a textos en griego
    def get_urns(self):
        persAPIcap_req = requests.get(self.__perseusAPI_capabilities)
        persAPIcap_parser = bs4.BeautifulSoup(persAPIcap_req.text, 'xml')
        
        for textgroup in persAPIcap_parser.find_all('textgroup'):
            if self.__greekMarker in textgroup['projid']:
                for work in textgroup.find_all('work'):
                    logging.debug(work['urn'])
                    self.urn_codes.append(work['urn'])
        logging.debug('La cantidad de textos a scrapear es de: '+str(len(self.urn_codes)))




if __name__ == "__main__":
    
    # Configuración de modo DEBUG por parámetro
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
    
    if not 'DEBUG' in sys.argv:
        logging.disable(logging.DEBUG)
    logging.debug('Inicio del programa')

    perseusScrap = Perseus()
    perseusScrap.get_urns()
