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
        self.__perseusAPI_passages = 'http://www.perseus.tufts.edu/hopper/CTS?request=GetValidReff&urn='
        self.__perseusAPI_text = 'http://www.perseus.tufts.edu/hopper/CTS?request=GetPassage&urn='
        self.__greekMarker = 'greekLit:'

    urn_codes = []
    urn_passages = []
    invalid_texts = []
    data = []
    urn_file = 'urn.txt'
    urn_fragment_file = 'urn_fragmentos.txt'

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
    
    # Este método coge el código urn de una obra y le pide a la API los códigos URN de sus respectivos pasajes
    def get_passages_urn(self):
        for urn in self.urn_codes:
            persAPIpassage_req = requests.get(self.__perseusAPI_passages+urn)
            persAPIpassage_parser = bs4.BeautifulSoup(persAPIpassage_req.text, 'xml')
        
            if persAPIpassage_parser.find('reff') == None:
                logging.debug('El texto con referencia \"{}\" no se puede scrapear'.format(urn))
                self.invalid_texts.append(urn)
            else:
                for passage_urn in persAPIpassage_parser.find('reff').find_all('urn'):
                    logging.debug(passage_urn.get_text())
                    self.urn_passages.append(passage_urn.get_text())
        
        logging.debug('La cantidad de pasajes scrapeables es de: '+str(len(self.urn_passages)))
        logging.debug('La cantidad total de textos inaccesibles es: {} de {}'.format(str(len(self.invalid_texts)), str(len(self.urn_codes))))

    # Este método extrae el fragmento, autor y obra de las URN viables
    def get_text(self):
        with open('textos_griegos.csv', 'w') as f:
            f.write('Autor,Obra,Fragmento,Texto\n')
            for urn in self.urn_passages:
                try:
                    persAPItext_req = requests.get(self.__perseusAPI_text+urn)
                    persAPItext_parser = bs4.BeautifulSoup(persAPItext_req.text, 'xml')
    
                    autor = persAPItext_parser.find('cts:groupname').get_text().strip()
                    obra = persAPItext_parser.find('cts:title').get_text().strip()
                    fragmento = persAPItext_parser.find('cts:psg').get_text().strip()
                    texto = persAPItext_parser.find('tei:body').get_text().replace('\n', ' ').replace('  ', ' ').replace("\"", "").strip().replace('.', '..').replace(',','.')
                    line = "\"{}\",\"{}\",\"{}\",\"{}\"\n".format(autor, obra, fragmento, texto)                         
                    print(line)
                    f.write(line)
                except AttributeError:
                    logging.debug('AttributeError para {}'.format(urn))

    def write_data(self, data, file_container):
        with open(file_container, 'w') as f:
            f.write('\n'.join(data))
            data = []

    def read_data(self, file_toread):
        if file_toread == self.urn_file:
            with open(file_toread, 'r') as f:
                list_data = f.read().split('\n')
                logging.debug('Resultado de leer {} = {}'.format(file_toread, list_data))
                self.urn_codes = list_data
        elif file_toread == self.urn_fragment_file:
            with open(file_toread, 'r') as f:
                list_data = f.read().split('\n')
                logging.debug('Resultado de leer {} = {}'.format(file_toread, list_data))
                self.urn_passages = list_data



def main():
    # Configuración de modo DEBUG por parámetro
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
    if not 'DEBUG' in sys.argv:
        logging.disable(logging.DEBUG)
    logging.debug('Inicio del programa')

    perseusScrap = Perseus()

    if '-rT' in sys.argv:
        perseusScrap.read_data(perseusScrap.urn_file)
    else:
        perseusScrap.get_urns()

    if '-wT' in sys.argv:
        perseusScrap.write_data(perseusScrap.urn_codes, perseusScrap.urn_file)

    if '-rF' in sys.argv:
        perseusScrap.read_data(perseusScrap.urn_fragment_file)
    else:
        perseusScrap.get_passages_urn()

    if '-wF' in sys.argv:
        perseusScrap.write_data(perseusScrap.urn_passages, perseusScrap.urn_fragment_file)

    if '-t' in sys.argv:
        perseusScrap.get_text()

    if len(sys.argv)==1:
        perseusScrap.get_urns()
        perseusScrap.get_passage_urn()
        perseusScrap.get_text()


if __name__ =='__main__':
    main()
