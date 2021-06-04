#!/usr/bin/env python3

import os
import sys
import bs4
import requests
import logging
import time
import argparse

class Perseus():
    def __init__(self, scrap_mode):
        self.__perseusAPI_capabilities = 'http://www.perseus.tufts.edu/hopper/CTS?request=GetCapabilities'
        self.__perseusAPI_passages = 'http://www.perseus.tufts.edu/hopper/CTS?request=GetValidReff&urn='
        self.__perseusAPI_text = 'http://www.perseus.tufts.edu/hopper/CTS?request=GetPassage&urn='
        self.__greekMarker = 'greekLit:'
        self.scrap_mode = scrap_mode
        self.urn_codes = []
        self.urn_passages = []
        self.invalid_texts = []
        self.data = []
        self.urn_scraped = []
        self.urn_file = 'metadata/urn.txt'
        self.urn_fragment_file = 'metadata/urn_fragments.txt'
        self.urn_nonvalid_texts = 'metadata/urn_not_available_texts.txt'
        self.scraped_file = 'metadata/scraped.txt'

        if self.scrap_mode == "complete":
            self.complete_execution()
        elif self.scrap_mode == "update":
            self.update()


    def __get_urns(self):
        
        """
        This method collects every URN code relative to greek texts
        """

        persAPIcap_req = requests.get(self.__perseusAPI_capabilities)
        persAPIcap_parser = bs4.BeautifulSoup(persAPIcap_req.text, 'xml')
        
        for textgroup in persAPIcap_parser.find_all('textgroup'):
            if self.__greekMarker in textgroup['projid']:
                for work in textgroup.find_all('work'):
                    logging.debug(work['urn'])
                    self.urn_codes.append(work['urn'])
                    print(f"Scraped text URN = {work['urn']}")
        print(f'Total texts to scrap: {str(len(self.urn_codes))}')
    
    
    def __get_passages_urn(self):
        
        """
        This method gets the URN codes from the Perseus API of the texts fragments for every text URN
        """
        
        self.__get_urns()
        for urn in self.urn_codes:
            persAPIpassage_req = requests.get(self.__perseusAPI_passages+urn)
            persAPIpassage_parser = bs4.BeautifulSoup(persAPIpassage_req.text, 'xml')
        
            if persAPIpassage_parser.find('reff') == None:
                logging.debug(f'Text with refference \"{urn}\" could not be scraped')
                self.invalid_texts.append(urn)
            else:
                for passage_urn in persAPIpassage_parser.find('reff').find_all('urn'):
                    if 'lat' not in passage_urn.get_text():
                        print(f"Scraped fragment URN = {passage_urn.get_text()}")
                        self.urn_passages.append(passage_urn.get_text())
        
        print(f'Total valid fragments: {str(len(self.urn_passages))}')
        print(f'Total invalid texts: {str(len(self.invalid_texts))} of {str(len(self.urn_codes))}')

    
    def __get_text(self, mode):
   
        """
        This method extracts the fragments, authors and titles from the not broken URNs
        """

        with open('greek_texts.csv', mode) as f:
            print('Initializing files')
            if self.scrap_mode == 'complete':
                f.write('author,title,fragment,text\n')
                self.__write_data(['',''], self.scraped_file)
                self.scrap_mode='update'

            elif self.scrap_mode == 'update':
                f.write('\n')
            
            count = 0
            for urn in self.urn_passages:
                if urn not in self.urn_scraped:
                    try:
                        persAPItext_req = requests.get(self.__perseusAPI_text+urn)
                        persAPItext_parser = bs4.BeautifulSoup(persAPItext_req.text, 'xml')
    
                        author = persAPItext_parser.find('cts:groupname').get_text().strip()
                        title = persAPItext_parser.find('cts:title').get_text().strip()
                        fragment = persAPItext_parser.find('cts:psg').get_text().strip()
                        text = persAPItext_parser.find('tei:body').get_text().replace('\n', ' ').replace('  ', ' ').replace("\"", "").strip()
                        line = f"\"{author}\",\"{title}\",\"{fragment}\",\"{text}\"\n"
                        print(line)
                        f.write(line)
                        self.__write_data([urn, ''],self.scraped_file)
                        count +=1
                        if count == 5000:
                            print('Napping a bit zzz...')
                            time.sleep(10)
                            count = 0


                    except AttributeError:
                        logging.debug(f'AttributeError for {urn}')

                    except ConnectionError:
                        logging.debug('Conection Error. Progress was saved and you can continue the process by restarting the program with -u flag')
                        sys.exit(0)

    
    def __write_data(self, data, file_container):
        
        """
        This method writes the data into the files given as parameters
        """

        if self.scrap_mode=='update':
            with open(file_container, 'a') as f:
                f.write('\n'.join(data))

        elif self.scrap_mode=='complete':
            with open(file_container, 'w') as f:
                f.write('\n'.join(data))

    
    def __read_data(self, file_toread):

        """
        This method reads the data from the files given as parameters
        """

        with open(file_toread, 'r') as f:
            list_data = f.read().split('\n')
            logging.debug(f'Result of reading {file_toread} = {list_data}')
            return list_data

    
    def complete_execution(self):
        
        """
        This method starts the workflow if the class is instantiated in complete mode
        """

        self.__get_passages_urn()
        self.__write_data(self.urn_passages, self.urn_fragment_file)
        self.__get_text('w')

    def update(self):
        
        """
        This method starts the workflow if the class is instantiated in update mode
        """

        self.urn_scraped = self.__read_data(self.scraped_file)
        logging.debug(self.urn_scraped)
        self.__get_passages_urn()
        self.__get_text('a')

def main():
    
    """
    Parameter configuration, class instantiation and program initialization
    """
    
    # Parameter configuration, using argparse
    parser = argparse.ArgumentParser(description='This program extracts greek texts by calling the API Perseus offers. It allows to obtain every text in a single execution or actualize the texts you already have on each calling to the program')
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-t","--text", action='store_true', help='The program cleans already scraped data and starts from the beggining. Only recomended for the first execution')
    group.add_argument("-u","--update", action = 'store_true',help="The program checks for texts not in the csv and add them if possible")
    
    parser.add_argument("-D","--DEBUG",action = 'store_true',default=False, help="Starts the program in DEBUG mode")

    args = parser.parse_args()
    
    # Program start
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
    if not args.DEBUG:
        logging.disable(logging.DEBUG)
    logging.debug('Program starting')
    
    # For the complete execution
    if args.text:
        Perseus("complete")
    
    # For the update execution
    elif args.update:
        Perseus("update")
    
    else:
        print("No parameter specified. Use -h parameter to see the options")

if __name__ =='__main__':
    main()
