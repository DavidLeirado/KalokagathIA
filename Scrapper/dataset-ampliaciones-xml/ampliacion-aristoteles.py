#!/usr/bin/env python3

import os, sys, bs4

count=0
for autor in os.listdir('Classics/'):

    try:
        for xml in os.listdir('Classics/'+autor+'/opensource/'):
            if '_gk' in xml:
                with open('Classics/'+autor+'/opensource/'+xml, 'r', encoding='utf-8') as rawtext:
                    
                    text = bs4.BeautifulSoup(rawtext, 'xml')
                    print(text.get_text())
                    count+=1
        
    except FileNotFoundError:
        print('El directorio '+xml+' está vacío')

print(count)
