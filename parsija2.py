# -*- coding: utf-8 -*-
#
# Tietokannan käsittelijä
#  Tietokanta-olioon tallennetaan ladatusta .px-tiedostosta UNITS-, VALUES- ja 
#  DATA-osiot. Muut kuin tyhjät arvot (".") tallennetaan liukulukuina
#
#  Muut funktiot tekevät ja yhdistävät tietokantahakuja ja -tuloksia
#
# Tekijä: Esko Niinimäki
# Versio: 0.3.1



import re
import pprint
import json

# Säilöö tietokannan arvot, hakusanat(="otsikot") ja otsikot(="taulukot")
# Datan järjestys on sama kuin .px-tiedostossa. Oikea arvo löydetään
# otsikoiden indeksien ja niitä vastaavien taulukoiden kertoimien avulla.
class Tietokanta:
	def __init__(self):
		self.taulukot = []
		self.otsikot = []
		self.arvot = []
		self.kertoimet = [1]
		self.yksikot = ""
		
	def lisaa_taulukko(self, taulukko, otsikot):
		self.taulukot.append(taulukko)
		self.otsikot.append(otsikot)
	
	def lisaa_arvot(self, arvot):
		self.arvot = arvot	

	def laske_kertoimet(self):
		for avain in reversed(self.otsikot[1:]):
			self.kertoimet.insert(0, len(avain)*self.kertoimet[0])
	# haluaa listan hakusanoista
	# palauttaa haetun arvon (joka on talletettu merkkijonona)
	def hae_solu(self, hakusanat):
		indeksi = 0
		# haetaan hakusanojen indeksit ja lisätään kertoimet
		for i in range(len(hakusanat)):
			indeksi += self.otsikot[i].index(hakusanat[i]) * self.kertoimet[i]
		return self.arvot[indeksi]

# Lukee .px-tiedoston sisällön merkkijonotaulukoksi: 1 rivi vastaa yhtä solua
def lue_data(tiedosto):
	data_raaka = open(tiedosto, 'r')
	# string-taulukko. erottimena ;\r\n
	# poistaa tyhjät alusta ja lopusta.
	data = [t.strip() for t in data_raaka.read().decode('ISO-8859-1').split(';\r\n')]
	data_raaka.close()
	return data

# Parsii annetun tiedoston UNITS, VALUES, ja DATA -kentät Tietokanta-olioon.
def parsi(tiedosto):
	# tiedosto string-taulukoksi
	data = lue_data(tiedosto) 	
	# haetaan VALUES-rivit säännöllisen merkkijonon avulla
	values_saanto = re.compile('VALUES\("(.*)"\)') #tällä estetään vääränkielisetkin
	tkanta = Tietokanta()
	for rivi in data:
		if not rivi:
			continue #jos rivi on tyhjä, hypätään yli
		# erotetaan arvot ja niiden nimi (otsikko/hakusana) toisistaan
		nimi, arvot = [t for t in rivi.split('=', 1)] #split riittää ajaa kerran
		# käsitellään UNITS-kohta, joka tulee vastaan ensimmäisenä
		if nimi == "UNITS":
			tkanta.yksikot = arvot[1:-1]
		on_values = values_saanto.match(nimi)
		# käsitellään VALUES-kohdat
		if on_values: #jos löytyy VALUES("<otsikko>")
			otsikko = on_values.group(1) #haetaan <otsikko>
			arvot = arvot.replace('\r\n', '') #muutetaan yksiriviseksi
			# erotetaan arvot listaan, 1. ja viimeinen " pois
			arvolista = arvot[1:-1].split('","') 		
			tkanta.lisaa_taulukko(otsikko, arvolista)
		# kaikki VALUES-kohdat on käsitelty
		# siirrytään (tiedostossa) DATA-kohtaan
		if nimi == "DATA":
			# hajotetaan listaksi, tyhjät merkit pois
			arvolista = [a.strip() for a in arvot.split(' ')]
	#		arvolista = [float(a.strip()) for a in arvot.split(' ')]
	#		arvolista = map(float, arvolista)
			# arvot (paitsi ".") luvuiksi
			for i in range(len(arvolista)):
				try:
					arvolista[i] = float(arvolista[i])
				except ValueError:
					continue
			tkanta.lisaa_arvot(arvolista)
	tkanta.laske_kertoimet()
	return tkanta

# Palauttaa usean hakusanan mukaisen taulukon.
# Kuljetaan saatua listaa eteenpäin.
# Jos tulee vastaan hakusanalista, tehdään rekursiivinen kutsu.
# Lopulta haetaan ehdot täyttävä solu, ja palataan rekursiossa.
def hae_taulukko(hakusanalista, tkanta):
	arvolista = []	
	for listako in hakusanalista:
		if isinstance(listako, list):
			i = hakusanalista.index(listako)
			# luodaan uusi lista käsittelyä varten
			listanen = list(hakusanalista)
			# arvolista = haettujen arvojen muodostama lista
			for alkio in listako:
				listanen[i] = alkio
				arvolista.append(hae_taulukko(listanen, tkanta))
			break #alemmat tasot hoitavat loput
	if not arvolista: #on tyhjä:
		return tkanta.hae_solu(hakusanalista)
	return arvolista

"""
tilastollisten muuttujien laskemista:

minimi = min(lista)
maximaalisin = max(lista)
ka = sum(lista)/len(lista)
def median (lista):
	lajiteltu_lista = sorted(lista)
	i = len(lista) / 2
	if len(lajiteltu_lista) % 2 == 1:
		return lajiteltu_lista[i]
	else:
		return (lajiteltu_lista[i] + lajiteltu_lista[i + 1])/2.0
"""

def hae_arvoparit(hakusanalista, xots, tkanta):
	# haetaan otsikon indeksi
	x = tkanta.taulukot.index(xots) #x-akselin indeksi
	# tarkistetaan ettei yli 2 ei-x-akselilistaa
	monihaku = False
	listoja = 0
	for listako in hakusanalista:
		if isinstance(listako, list):
			if hakusanalista.index(listako) != x:
				monihakuindeksi = hakusanalista.index(listako)
				monihaku = True
			listoja += 1
		if listoja > 2:
			return	#virhe, jos listoja > 2
	
	# tulosmuuttuja
	haku = []
	xarvot = hakusanalista[x]
	#print "xarvot:"
	#pprint.pprint(xarvot)
	if isinstance(xarvot, list):
		# jos x-akseli on lista ja haettavia arvolistoja on useita
		if monihaku:
			# poimitaan hakulista muistiin
			monihakuarvot = hakusanalista[monihakuindeksi]
			# tietokantahaku jokaiselle arvolistalle
			for indeksi in monihakuarvot:
				hakusanalista[monihakuindeksi] = indeksi
				arvolista = hae_taulukko(hakusanalista, tkanta)
				# yhdistetään x-akseli ja haettu arvolista
				if isinstance(arvolista, list):
					arvolista = zip(xarvot, arvolista)
				# lisätään lista haettuihin
				haku.append(arvolista)
			# korjataan hakusanalista
			hakusanalista[monihakuindeksi] = monihakuarvot
		# jos x-akseli on lista ja haettavia arvolistoja on 1, tehdään 1
		# tietokantahaku
		else:
			arvolista = hae_taulukko(hakusanalista, tkanta)
			arvolista = zip(xarvot, arvolista)
			haku = arvolista
	# jos x-akseli ei ole lista, vaan 1 arvo
	else:
		arvolista = hae_taulukko(hakusanalista, tkanta)
		# jos x-akseli on 1 arvo ja haettavia arvoja on useita
		if monihaku:
			for i in range(len(arvolista)):
				arvolista[i] = [(xarvot, arvolista[i])]
		# jos x-akseli on 1 arvo ja haettavia arvoja on 1 kpl
		else:
			arvolista = [(xarvot, arvolista)]
		haku = arvolista
	print "haku:"
	pprint.pprint(haku)
	return haku

# Yhdistää otsikot ja arvolistat sanakirjaksi
def arvolistat_otsikoihin(ylilista, alilista):
	sanakirja = {}
	if len(ylilista) != len(alilista):
		print "Listat eri kokoisia, ei yhdistetä, yli: %i, ali: %i" %(len(ylilista), len(alilista))
		return
	for i in range(len(ylilista)):
		sanakirja[ylilista[i]] = alilista[i]
	pprint.pprint(sanakirja) #saa tarkastella kivasti päätteestä
	return sanakirja

# Yhdistä yhden arvolistan yhteen otsikkoon
def arvot_otsikkoon(otsikko, arvot):
	sanakirja = {}
	sanakirja[otsikko] = arvot
	return sanakirja

# Yhdistää otsikot ja arvolistat sanakirjaksi riippumatta ovatko yhdistettävät
# listoja vai alkioita
def listat_pariksi(ylilista, alilista):
	sanakirja = {}
	# vain 1 liitettävä, eli alkio
	if isinstance(ylilista, basestring): 
		sanakirja[ylilista] = alilista
		return sanakirja
	# eri kokoisia ei voi yhdistää
	if len(ylilista) != len(alilista):
		print "Listat eri kokoisia, ei yhdistetä, yli: %i, ali: %i" %(len(ylilista), len(alilista))
		return -1 #virhe
	for i in range(len(ylilista)):
		sanakirja[ylilista[i]] = alilista[i]
	pprint.pprint(sanakirja) #saa tarkastella kivasti päätteestä
	return sanakirja

# Tallentaa sanakirjan json-tiedostoksi
def sanakirja_jsoniksi(sanakirja, tiedostonimi):
	with open(tiedostonimi, 'w') as tuleva_tiedosto:
		json.dump(sanakirja, tuleva_tiedosto)
	
# Palauttaa tietokannan otsikot sanakirjana
def otsikot_sanakirjaksi(tietokanta):
	sanakirja = {}
	for i in range(len(tietokanta.taulukot)):
		sanakirja[tietokanta.taulukot[i]] = tietokanta.otsikot[i]
	return sanakirja

# testifunktio
def test():
	tied = "tietokannat/008_vtutk_tau_102_fi.px"
	tkanta = parsi(tied)
	hakusanat = []
	lista = []
	hakusanat.append(tkanta.otsikot[0][0:3])
	hakusanat.append(tkanta.otsikot[1])
	hakusanat.append(tkanta.otsikot[2][1])
	lista = hae_taulukko(hakusanat, tkanta)
	hakutulos = asdf(hakusanat[0], lista)
	return json.dumps(hakutulos)

# testifunktio
def test2_annatietokanta():
	tied = "tietokannat/008_vtutk_tau_102_fi.px"
	tkanta = parsi(tied)
	hakusanat = []
	lista = []
	hakusanat.append(tkanta.otsikot[0][0:3])
	hakusanat.append(tkanta.otsikot[1])
	hakusanat.append(tkanta.otsikot[2][1])
	lista = hae_taulukko(hakusanat, tkanta)
	hakutulos = asdf(hakusanat[0], lista)
	return tkanta
	
	
#testausta
if __name__ == '__main__':
	tied = "tietokannat/008_vtutk_tau_102_fi.px"
	tkanta = parsi(tied)
	hakusanat = []
	lista = []
#	hakusanat.append(tkanta.otsikot[0][0:5])
#	hakusanat.append(tkanta.otsikot[1][0])
#	hakusanat.append(tkanta.otsikot[2])
	hakusanat.append(tkanta.otsikot[0][0:5])
	hakusanat.append(tkanta.otsikot[1])
	hakusanat.append(tkanta.otsikot[2][1])
	pprint.pprint(hakusanat)
	print "\n---------------------------------------\n"
	lista = hae_taulukko(hakusanat, tkanta)
	pprint.pprint(lista)
	print "\n"
	tuleva_nimi = "static/" + "asdf." + 'json'
	sanakirja_jsoniksi(otsikot_sanakirjaksi(tkanta), tuleva_nimi)
	hakutulos = asdf(hakusanat[0], lista)
	sanakirja_jsoniksi(hakutulos, "static/tuf.json")





