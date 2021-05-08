#!/usr/bin/env python3

import os
import sys
import bs4
import requests
import logging


if __name__ == "__main__":
    
    # Configuración de modo DEBUG por parámetro
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
    
    if not 'DEBUG' in sys.argv:
        logging.disable(logging.DEBUG)
    logging.debug('Inicio del programa')
