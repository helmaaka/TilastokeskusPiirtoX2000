/*
tekijät:
    Heta Rekilä
    Heli Kallio
    Ilari Jalli
    Esko Niinimäki
*/
/*
Piirtonappi
1. Poimii valitut hakusanat.

2. Lähettää valinnat palvelimelle.
3. Piirtää saadun datan flotilla.
*/
jQuery(function($) {
$(silmukka).click(function() {

    var valitutOptionit = $("option").serializeArray();
    // kaivellaan listoista kaikki optionit ulos
    var listaOptionit = document.getElementsByTagName("option");

    // Kaivetaan x-akselinapit esille ja etsitään valittu.
    // Jos mikään ei valittuna, laitetaan x-akseliksi ensimmäinen listasta
    var valittu = "";
    var valittuXAkseli = document.getElementsByTagName("input");
    var valittuXAkseliKohta = valittuXAkseli[0];

    for (w = 0; w < valittuXAkseli.length; w++) {

        currentOption1 = valittuXAkseli[w];
        if (currentOption1.checked === true) {
            valittu = currentOption1.id;
            break;
        } else {
            valittu = valittuXAkseliKohta.id;
        }
    }
    // korjataan valintamerkkijono
    valittu = valittu.slice(0, -1);

    // lopetetaan funktion kulkeminen jos yhtään mitään ei ole valittuna
    if (valittu === "enablePositio" || valittu === "esitys_line") {
        alert("Mitään ei ole valittuna, joten jätetään piirtämättä." + " Valitse ensiksi x-akseli, sitten piirrettävät datat");
        return;
    }

    // Tehdään otsikko esimerkkitulostukselle
    var valinnat = "<h2>Valintasi<\/h2>";
    valinnat += valittu;

    // käydään kaikki optionit läpi ja poimitaan niistä valitut
    for (i = 0; i < listaOptionit.length; i++) {
        currentOption = listaOptionit[i];
        // jos valittu, tökätään se taulukkoon ja listaan
        if (currentOption.selected === true) {
            valinnat += " <li>" + currentOption.value + "<\/li> \n";
            valitutOptionit.push(currentOption.value);
        }
    }
    
   // muutetaan hakusanat merkkijonoksi palvelinpyyntöä varten
    var valitut = JSON.stringify(valitutOptionit);
    // tehdään HTTP POST -pyyntö hakusanoilla ja x-akselin valinnalla
    $.post("/arvot", {
            otsikot: valitut,
            xakseli: valittu
        },

        // vastaanotetaan piirrettävä data
        function(data, status) {
            // Kokeillaan onko kama oikeassa muodossa, alert ja pois jos ei ole
            try {
                var json = JSON.parse(data);
            } catch (e) {

                alert(JSON.stringify(data) + " Valintoja voi tehdä useampia kahdesta eri listasta, ja toisen näistä on oltava x-akseli");
                return;
            }
            // poimitaan arvojen yksiköt ja tulostetaan se
            var yakselin_yksikot = json["yksikot"];
            $("#y_yksikko").empty().append("<p>" + yakselin_yksikot + "<\/p>");
            // poimitaan maksimiarvo ja lasketaan y-akselin arvopisteet (tickit)
            var ymaksimi = parseFloat(json["maksimi"]);
            var l = ymaksimi;
            var eksp = 1;
            var i = 0;
            while (l > 1) {
                l = ymaksimi/eksp;
                eksp *= 10;
                i++;
            }
            eksp = i;
            // askeleen koko jokin 10-potenssi
            // askelien (vaakaviivojen) määrä (1-)4-7
            askel = Math.floor(Math.max(i/4, 1));
            ylogticks = [];
            for (i = 1; i < eksp; i += askel) {
                ylogticks[ylogticks.length] = Math.pow(10, i);
            }
            // varsinainen hakutulos
            json = json["tulos"];
            // ilmoitetaan piirtonapissa datan hakemisesta käyttäjälle
            var $nappula = $(this).button("loading");
            // katsotaan mitä muotoa x-akseli on:
            var desimaalit = "0";
            // akselityypin oletus on null -> flot pitää liukulukuna

            var akselityyppi = null;
            // vuosiluvuille 0 desimaalia eli kokonaisluvut
            if (valittu == "Vuosi") {
                desimaalit = "0";
            }

            var akselipisteet = [];
            var xtick_lkm = 0;
            // Jos x-akseli ei ole vuosiluvut, oletetaan ne merkkijonoiksi.
            // Akselin arvopisteet muutetaan myöhemmin muotoon 0 .. n ja 
            // niille annetaan labeliksi alkuperäinen arvo=merkkijono.
            // Label näkyy tällöin käyttäjälle.
            if (valittu != "Vuosi") {
                for (arvojoukko in json) {
                    // poimitaan tässä samalla x-akselin pisteiden lkm
                    xtick_lkm = json[arvojoukko].length;
                    for (j = 0; j < json[arvojoukko].length; j++) {
                        // x-akselin pisteiden label
                        akselipisteet[akselipisteet.length] = [j, json[arvojoukko][j][0]];
                    }
                    // akselityyppi on nyt taulukko
                    akselityyppi = akselipisteet;
                    break;
                }
            }
            // rajoitetaan piirrettävien x-akselin pisteiden määrä n. 10:een
            // flot osaa tulkita välit kiitettävästi
            if (xtick_lkm > 10) { akselityyppi = 10 }

            //piirretään haetut arvopisteet
            
            var plotarea = $("#placeholder");
            var kaikki = [];
            var i = 0;
            // Tässä haetaan divi, jossa on esitystavan valinta. 
            // Tallennetaan omiin muuttujiin kunkin (bars, lines) tila,
            // halutaanko sitä näyttöön vai ei
            var esitysmuotoValintaForm = $("#esitysmuotoForm");
            var linesBool = document.getElementById('esitys_lines').checked;
            var barsBool = document.getElementById('esitys_bars').checked;
            var pointsBool = document.getElementById('esitys_points').checked;
            // Skaalaus on lineaarinen tai logaritminen
            var logBool = document.getElementById('esitys_log').checked;
            if (logBool) {
                var yvalinnat = {
                    ticks: ylogticks, //asetetaan y-akselin pisteet/vaakaviivat
                    transform:  function(v) {return v === 0 ? 0 : Math.log(v);},

                    // ei tunnu tekevän mitään ?
                    inverseTransform: function (v) { return Math.exp(v); }
                };
            }
            else
                yvalinnat = {};
            
            // lasketaan piirrettävien arvojoukkojen lkm

            var arvojoukko_lkm = 0;
            for (arvojoukko in json) {
                arvojoukko_lkm++;
            }

            // Asetetaan piirrettävä data flotin ymmärtämään muotoon
            var i = 0;
            for (arvojoukko in json) {
                // Jos x-akseli ei ole Vuosi, akselin arvopisteet muotoon 0 .. 1 
                if (valittu != "Vuosi") {
                    for (j = 0; j < json[arvojoukko].length; j++) {
                        json[arvojoukko][j][0] = j;
                    }
                }

                // jos palkit valittu, ne piirretään vierekkäin
                if (barsBool) {
                    var a_lkm = arvojoukko_lkm;
                    for (j = 0; j < json[arvojoukko].length; j++) {
                        json[arvojoukko][j][0] = parseFloat(json[arvojoukko][j][0]) + i*0.9/a_lkm + 0.45/a_lkm - 0.45;
                    }
                }
                i++;
                // arvojoukon tiedot
                kaikki[kaikki.length] = {
                    label: arvojoukko,
                    data: json[arvojoukko],

                    bars: {
                        show: barsBool, //Tässä barsBool kertoo, onko sen checkbox tai radiobutton valittu. Piirretään jos on
                        order: 1,
                        barWidth: 0.9/arvojoukko_lkm,
                        align: "center"
                    },
                    lines: {
                        show: linesBool
                    },  //Tässä linesBool kertoo, onko sen checkbox tai radiobutton valittu. Piirretään jos on
                    points: {
                        show: pointsBool
                    } //linesBool           
                }
            }

            // Piirrettävän datan asetukset
            var options = {
                legend: {
                    show: true,
                    container: $("#legendContainer")
                },
                xaxis: {
                    tickDecimals: desimaalit,
                    ticks: akselityyppi
                },
                yaxis: yvalinnat,
                // arvojen korostus
                grid: { hoverable: true, clickable: true, autoHighlight: true }

            };

            // käsketään flotin piirtää
            $.plot(plotarea, kaikki, options);
            
            // palautetaan piirtonappiin oletusteksti
            $nappula.button("reset");
            // luodaan tooltip-div, joka näytetään tarvittaessa
            $("<div id='tooltip'></div>").css({
                position: "absolute",
				display: "none",
				border: "1px solid #fdd",
				padding: "2px",
				"background-color": "#fee",
				opacity: 0.80
			}).appendTo("body");
			
			// lisätään kuuntelija josko ollaan kuvaajan sellaseissa kohdassa että tarvitaan tooltippiä
			$("#placeholder").bind("plothover", function(event, pos, item){
				if (item) {
						var y = item.datapoint[1];
						var kayran_nimi = item.series.label;
					$("#tooltip").html(y).css({
						top: item.pageY + 5,
						left: item.pageX + 5
					}).fadeIn(200);
					var legend_labelit = document.getElementsByClassName("legendLabel");
				} else {
					$("#tooltip").hide();
				}
			});
            
        });
});
});
