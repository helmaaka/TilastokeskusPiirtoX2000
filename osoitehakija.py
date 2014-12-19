# -*- coding: utf-8 -*-
# 
# Hakee px-tietokantojen puurakenteen tilastokeskusken sivulta 2 vaiheessa
# 1. kansiorakenne
# 2. tietokantojen osoitteet
#
# Tehty indeksijakija.py:n pohjalta
# Tekijä: Esko Niinimäki
#

from selenium import webdriver
import pprint
import pickle
from collections import OrderedDict
import json
import time
import pdb


# tee_sanakirjan täyttämä sanakirja tieokantojen linkit sisältävien
# sivujen osoitteista.
# kasvata_lehdet hakee tieokantojen osoitteet tämän avulla
lehdet = {} 

# Käydään lehdet rekursiivistesti läpi ja lisätään vastaava sanakirja.
def kasvata_lehdet(selain, puu):
	global lehdet 
	#tiedostot = {}
	# käydään kaikki puu-sanakirjan arvot läpi
	for hakemisto in puu:
		# jos hakemisto(=arvo) on tyhjä, haetaan tietokantojen osoitteet ja
		# liitetään ne avaimeen
		if not puu[hakemisto]: #jos hakemisto on tyhjä eli on lehti
			selain.get(lehdet[hakemisto])
			# "default"-nimisiä on aina 2:
			#  1. antaa tietokannan osoitteen
			#  2. antaa tietokannan nimen
			nimet = selain.find_elements_by_class_name("default")
			linkit = selain.find_elements_by_link_text("Lataa koko taulukko PC-Axis tiedostomuodossa")
			tiedostot = {}
			for i in range(len(linkit)):
					avain = nimet[i*2].text
					arvo = linkit[i].get_attribute("href")
					tiedostot[avain] = arvo
			puu[hakemisto] = tiedostot
		# muussa tapauksessa kutsutaan funktiota alipuulla
		else:
			puu[hakemisto] = kasvata_lehdet(selain, puu[hakemisto])
	return puu

# rekursiivinen sanakirjan luonti
# palauttaa sanakirjan kansiorakenteesta
def tee_sanakirja(selain, URL, otsikot, kutsuja, viitteet, tasoraja):
	skirja = {}
	global lehdet
	# tämän hakemistotason alku- ja loppualkiot otsikot- ja viitteet-listoissa:
	alku = tasoraja[0]
	loppu = tasoraja[1]
	i = 0
	# etsitään löytyykö kutsujaa alkiolle
	for viite in range(alku, loppu):
		# jos kutsuja löytyi, uusitaan rekursio:
		#  hakemisto, jolle löytyi kutsuja, on uusi kutsuja
		#  taso vaihtuu pykälää syvempään
		if viitteet[viite] == kutsuja:
			skirja[otsikot[viite].text] = tee_sanakirja(selain, URL, otsikot, viite, viitteet, tasoraja[1:])
			# jos rekursio palautti tyhjän, ollaan alimmalla tasolla
			# otetaan linkki muistiin globaaliin listaan
			if not skirja[otsikot[viite].text]:
				linkki = otsikot[viite].get_attribute("href")
				lehdet[otsikot[viite].text] = linkki
	return skirja
def hae():
	alku = time.time()
	URL = 'http://pxweb2.stat.fi/database/StatFin/databasetree_fi.asp'
	ALKIO_LKM = 350 #alkioita oli 337 kpl:tta viimeksi tilastokeskuksen sivuilla
	TIED_NIMI = "otsikot"
	lapi = False
	kayty = [False] * ALKIO_LKM
	# otetaan Firefox käyttöön
	selain = webdriver.Firefox()
	kaikki = [] #kaikkien lisättyjen alkioiden säilytyslista
	# avataan selain
	selain.get(URL)
	viitteet = [] #lisättyjen alkioiden viitteet ylätason alkioon
	alkio_lkm = 0 #kaikkien alkioiden lkm
	tasoraja = [] #tasojen 1. alkioiden indeksit listoissa
	# lisätään juurihakemisto indeksiin 0, 1. taso alkaa 1:stä
	tasoraja.append(1)
	kaikki.append(0)
	viitteet.append(0)
	taso_lkm = 0 #tason alkioiden lkm
	# haetaan kansiorakenne seleniumilla
	while not lapi:
		lapi = True
		a = [] #tason alkioiden säilytyslista
		viite = 0
		# käydään avaamattomat kansiot läpi ja lisätään ne
		for i in range(1, ALKIO_LKM):#jos ei olla käyty(/avattu/löydetty)
			if not not kayty[i]: #jos ei ole false
				viite = kayty[i]
			else:
				# lisätään alkio, jos löytyi haetulla id:llä
				alkio = selain.find_elements_by_id("itemTextLink%d" %i)
				if not not alkio:
					taso_lkm += 1
					alkio_lkm += 1
					a.append(alkio[0])
					kaikki.append(alkio[0])#.text)
					viitteet.append(viite)
					kayty[i] = taso_lkm
					lapi = False
		tasoraja.append(alkio_lkm + 1)
		# avataan uudet lisätyt kansiot, joissa alikansiorakenne
		for i in range(len(a)):
			linkki = a[-i-1].get_attribute("href")
			#ei avata hakemistoa, jos osoite vaihtuisi
			if linkki[:5] != "javas": 
				continue
			url_nyt = a[-i-1].click()
	# poimitaan vielä varmuuden vuoksi verkko-osoite uudestaan
	URL = selain.current_url
	# luodaan kansiorakenteesta sanakirja
	s = tee_sanakirja(selain, URL, kaikki, 0, viitteet, tasoraja)
	# haetaan tietokantatiedostojen osoitteet ja lisätään sanakirjaan
	s = kasvata_lehdet(selain, s)
	# viedään valmis otsikkosanakirja json-tiedostoon
	luo_json(s, TIED_NIMI)
	selain.quit()
	# ilmoitetaan vielä, kauanko koko hommaan meni aikaa
	loppu = time.time()
	print "aikaa kului", loppu - alku, "s"

# luo json-tiedoston sanakirjasta
def luo_json(sanakirja, nimi):
	nimi = nimi + ".json"
	with open(nimi, 'w') as fp: 
		json.dump(sanakirja, fp, sort_keys= True)
	
if __name__ == '__main__':
	hae()



