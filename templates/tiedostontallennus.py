# -*- coding: utf-8 -*-

# kutsutaan 
# import tiedostontallennus
# tiedostontallennus.Lataa_tiedosto("http://pxweb2.stat.fi/database/StatFin/asu/asas/010_asas_tau_101.px")
#
# tallentaa tiedoston samaan paikkaan kuin kutsuva ohjelma
import urllib
'''
 tekijä:
     Heta Rekilä
'''

# korvaa vanhemman tiedoston, jos on samanniminen
def Lataa_tiedosto(linkki):
    indeksi = linkki.rfind("/")
    if (indeksi <= -1):
        indeksi = 0
        nimi = "/" + linkki
    else:
        nimi = linkki[indeksi:]
    palautus = nimi[1:]
    try:
        urllib.urlretrieve(linkki, palautus)
    except IOError:
        palautus = "Lataus epäonnistui!"
    finally:
       return palautus

'''
print Lataa_tiedosto("http://pxweb2.stat.fi/database/StatFin/asu/asas/010_asas_tau_101.px")
print Lataa_tiedosto("http://pxweb2.stat.fi/database/StatFin/asu/asas/020_asas_tau_102.px")
print Lataa_tiedosto("020_asas_tau_102.px") # epäonnistuu
'''
