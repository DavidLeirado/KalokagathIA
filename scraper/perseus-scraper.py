#!/usr/bin/env python3

import os
import sys
import bs4
import requests
import logging
import time
import argparse

# Iniciamos la clase Perseus()
class Perseus():
    # Iniciamos el constructor de la clase Perseus()
    def __init__(self):
        self.__perseusAPI_capabilities = 'http://www.perseus.tufts.edu/hopper/CTS?request=GetCapabilities'
        self.__perseusAPI_passages = 'http://www.perseus.tufts.edu/hopper/CTS?request=GetValidReff&urn='
        self.__perseusAPI_text = 'http://www.perseus.tufts.edu/hopper/CTS?request=GetPassage&urn='
        self.__greekMarker = 'greekLit:'

    scrap_mode = ''
    urn_codes = []
    urn_passages = []
    invalid_texts = []
    data = []
    urn_scraped = []
    urn_file = 'metadata/.urn.txt'
    urn_fragment_file = 'metadata/.urn_fragmentos.txt'
    urn_nonvalid_texts = 'metadata/.urn_textos_no_disponibles.txt'
    scrapeado_file = 'metadata/.scrapeado.txt'

    # Al llamar a este método, se recopilan todos los códigos URN correspondientes a textos en griego
    def __get_urns(self):
        persAPIcap_req = requests.get(self.__perseusAPI_capabilities)
        persAPIcap_parser = bs4.BeautifulSoup(persAPIcap_req.text, 'xml')
        
        for textgroup in persAPIcap_parser.find_all('textgroup'):
            if self.__greekMarker in textgroup['projid']:
                for work in textgroup.find_all('work'):
                    logging.debug(work['urn'])
                    self.urn_codes.append(work['urn'])
                    print("Recogido texto con código = {}".format(work['urn']))
        print('La cantidad de textos a scrapear es de: '+str(len(self.urn_codes)))
    
    # Este método coge el código urn de una obra y le pide a la API los códigos URN de sus respectivos pasajes
    def __get_passages_urn(self):
        self.__get_urns()
        for urn in self.urn_codes:
            persAPIpassage_req = requests.get(self.__perseusAPI_passages+urn)
            persAPIpassage_parser = bs4.BeautifulSoup(persAPIpassage_req.text, 'xml')
        
            if persAPIpassage_parser.find('reff') == None:
                logging.debug('El texto con referencia \"{}\" no se puede scrapear'.format(urn))
                self.invalid_texts.append(urn)
            else:
                for passage_urn in persAPIpassage_parser.find('reff').find_all('urn'):
                    if 'lat' not in passage_urn.get_text():
                        print("Recogido fragmento con código = {}".format(passage_urn.get_text()))
                        self.urn_passages.append(passage_urn.get_text())
        
        print('La cantidad de pasajes scrapeables es de: '+str(len(self.urn_passages)))
        print('La cantidad total de textos inaccesibles es: {} de {}'.format(str(len(self.invalid_texts)), str(len(self.urn_codes))))

    # Este método extrae el fragmento, autor y obra de las URN viables
    def __get_text(self, mode):
        with open('textos_griegos.csv', mode) as f:
            print('Iniciando archivos')
            if self.scrap_mode == 'complete':
                f.write('Autor,Obra,Fragmento,Texto\n')
                self.__write_data('', self.scrapeado_file)
                self.scrap_mode='update'

            elif self.scrap_mode == 'update':
                f.write('\n')
            
            count = 0
            for urn in self.urn_passages:
                if urn not in self.urn_scraped:
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
                        self.__write_data([urn, ''],self.scrapeado_file)
                        count +=1
                        if count == 5000:
                            print('Descansando un poco zzz...')
                            time.sleep(10)
                            count = 0

                
                    except AttributeError:
                        logging.debug('AttributeError para {}'.format(urn))
                    
                    except ConnectionError:
                        logging.debug('Error de conexión. El progreso está guardado y se puede continuar el scraping con el parámetro -u en una nueva ejecución')
                        sys.exit(0)

    def __write_data(self, data, file_container):
        if self.scrap_mode=='update':
            with open(file_container, 'a') as f:
                f.write('\n')
                f.write('\n'.join(data))

        elif self.scrap_mode=='complete':
            with open(file_container, 'w') as f:
                f.write('\n'.join(data))

    def __read_data(self, file_toread, var_tostore):
        with open(file_toread, 'r') as f:
            list_data = f.read().split('\n')
            logging.debug('Resultado de leer {} = {}'.format(file_toread, list_data))
            var_tostore = list_data

    def complete_execution(self):
        self.scrap_mode = 'complete'
        self.__get_passages_urn()
        self.__write_data(self.urn_passages, self.urn_fragment_file)
        self.__get_text('w')

    def actualizacion(self):
        self.scrap_mode = 'update'
        self.__read_data(self.scrapeado_file, self.urn_scraped)
        logging.debug(self.urn_scraped)
        self.__get_passages_urn()
        self.__get_text('a')


def main():
    parser = argparse.ArgumentParser(description='Este programa sirve para extraer textos en griego a través de la API que ofrece Perseus. Permite, según parámetros, obtener todos los textos o descargarlos por grupos actualizando los datos')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t","--text", action='store_true', help="El programa limpia los datos ya recabados y empieza su ejecución desde 0. Solo recomendado si es la primera ejecución")
    group.add_argument("-u","--update", action = 'store_true',help="El programa revisa los textos aún no añadidos al csv y actualiza la información de éste de ser posible")
    
    parser.add_argument("-D","--DEBUG",action = 'store_true',default=False, help="Inicia el programa en modo DEBUG")

    args = parser.parse_args()
    
    perseusScrap = Perseus()

    # Configuración de modo DEBUG por parámetro
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
    if not args.DEBUG:
        logging.disable(logging.DEBUG)
    logging.debug('Inicio del programa')
    if args.text:
        perseusScrap.complete_execution()
    elif args.update:
        perseusScrap.actualizacion()
    else:
        print("Ningún parámetro fue especificado. Por favor indique un modo de ejecución para el programa. El parámetro -h muestra las opciones disponibles")

if __name__ =='__main__':
    main()
