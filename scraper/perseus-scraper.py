#!/usr/bin/env python3

import os
import sys
import bs4
import requests
import logging

class Perseus():
    def __init__(self):
        perseusAPI = https://scaife.perseus.org/library/
        greekMarker = 'urn:cts:greekLit:'



if __name__ == "__main__":
    
    # Configuración de modo DEBUG por parámetro
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
    
    if not 'DEBUG' in sys.argv:
        logging.disable(logging.DEBUG)
    logging.debug('Inicio del programa')
