#!/usr/bin/env python3 

import requests, os, bs4, sys




class Llamar_url():
    def __init__(self, url, autor, obra, iden):
        self.autor = autor
        self.obra = obra
        self.iden = iden
        self.llamada = requests.get(url)
        self.parser = bs4.BeautifulSoup(self.llamada.text, 'xml')
        self.list = self.scrap()

    def scrap(self):
        lista = []
        for fragment in self.parser.find_all('div', {'type':'textpart'}):
            lista.append(self.formato(fragment))
        return lista

    def formato(self, fragmento):
        text = fragmento.get_text().strip().replace('\n',' ').replace('\t', '')
        linea = '{};{};{};{}'.format(self.autor, self.obra, fragmento[self.iden], text)
        return linea
 



class Lineparse(Llamar_url):
    def __init__(self, url, autor, obra, iden):
        super().__init__(url, autor, obra, iden)

    def scrap(self):
        lista = []
        for fragment in self.parser.find_all('l'):
            lista.append(self.formato(fragment))
        return lista




with open('textos.csv', 'r') as f:
        for line in f.readlines():
            parametros = line.replace('\n','').split('>>')
            
            if not 'l' in parametros:
                instancia = Llamar_url(parametros[0],parametros[1],parametros[2],parametros[3])
            elif 'l' in parametros:
                instancia = Lineparse(parametros[0], parametros[1], parametros[2], parametros[3])

            for dato in instancia.list:
                print(dato)

