/*
tekij‰t:
    Heta Rekil‰
    Heli Kallio
    Ilari Jalli
    Esko Niinim‰ki
*/
/*
Piirtonappi
1. Poimii valitut hakusanat.

2. L‰hett‰‰ valinnat palvelimelle.
3. Piirt‰‰ saadun datan flotilla.
*/
jQuery(function($) {
$(silmukka).click(function() {


    var valitutOptionit = $("option").serializeArray();
    // kaivellaan listoista kaikki optionit ulos
    var listaOptionit = document.getElementsByTagName("option");
    



    // Kaivetaan x-akselinapit esille ja etsit‰‰n valittu.
    // Jos mik‰‰n ei valittuna, laitetaan x-akseliksi ensimm‰inen listasta
    var valittu = "";
    var valittuXAkseli = document.getElementsByTagName("input");
    var valittuXAkseliKohta = valittuXAkseli[0];

    for (w = 0; w < valittuXAkseli.length; w++) {

        currentOption1 = valittuXAkseli[w];
        if (currentOption1.checked === true) {
            valittu = currentOption1.id;
            break;
        } 
    }
    if (valittu === null) {return;}
    // korjataan valintamerkkijono
    valittu = valittu.slice(0, -1);


    // lopetetaan funktion kulkeminen jos yht‰‰n mit‰‰n ei ole valittuna
    if (valittu !== "enablePositio" || valittu === "esitys_line") {
        alert("Mit‰‰n ei ole valittuna, joten j‰tet‰‰n piirt‰m‰tt‰." + " Valitse ensiksi x-akseli, sitten piirrett√§v√§t datat");
        return;
    }

    // Tehd‰‰n otsikko esimerkkitulostukselle
    var valinnat = "<h2>Valintasi<\/h2>";
    valinnat += valittu;

    // k‰yd‰‰n kaikki optionit l‰pi ja poimitaan niist‰ valitut
    for (i = 0; i < listaOptionit.length; i++) {
        currentOption = listaOptionit[i];
        // jos valittu, tˆk‰t‰‰n se taulukkoon ja listaan
        if (currentOption.selected === true) {
            valinnat += " <li>" + currentOption.value + "<\/li> \n";
            valitutOptionit.push(currentOption.value);
        }
    }
    
    
    //var valitut = [];
   // muutetaan hakusanat merkkijonoksi palvelinpyyntˆ‰ varten
    var valitut = JSON.stringify(valitutOptionit);
    // tehd‰‰n HTTP POST -pyyntˆ hakusanoilla ja x-akselin valinnalla
    $.post("/arvot", {
            otsikot: valitut,
            xakseli: valittu
        },

        // vastaanotetaan piirrett‰v‰ data
        function(data, status) {
            // Kokeillaan onko kama oikeassa muodossa, alert ja pois jos ei ole
            try {
                var json = JSON.parse(data);
            } catch (e) {

                alert(JSON.stringify(data) + " Valintoja voi tehd‰ useampia kahdesta eri listasta, ja toisen n‰ist‰ on oltava x-akseli");
                return;
            }
            // poimitaan arvojen yksikˆt ja tulostetaan se
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
            // askelien (vaakaviivojen) m‰‰r‰ (1-)4-7
            askel = Math.floor(Math.max(i/4, 1));
            ylogticks = [];
            for (i = 1; i < eksp; i += askel) {
                ylogticks[ylogticks.length] = Math.pow(10, i);
            }
            // varsinainen hakutulos
            json = json["tulos"];
            // ilmoitetaan piirtonapissa datan hakemisesta k‰ytt‰j‰lle
            var $nappula = $(this).button("loading");
            // katsotaan mit‰ muotoa x-akseli on:
            var desimaalit = "0";
            // akselityypin oletus on null -> flot pit‰‰ liukulukuna

            var akselityyppi = null;
            // vuosiluvuille 0 desimaalia eli kokonaisluvut
            if (valittu == "Vuosi") {
                desimaalit = "0";
            }

            var akselipisteet = [];
            var xtick_lkm = 0;
            // Jos x-akseli ei ole vuosiluvut, oletetaan ne merkkijonoiksi.
            // Akselin arvopisteet muutetaan myˆhemmin muotoon 0 .. n ja 
            // niille annetaan labeliksi alkuper‰inen arvo=merkkijono.
            // Label n‰kyy t‰llˆin k‰ytt‰j‰lle.
            if (valittu != "Vuosi") {
                for (arvojoukko in json) {
                    // poimitaan t‰ss‰ samalla x-akselin pisteiden lkm
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
            // rajoitetaan piirrett‰vien x-akselin pisteiden m‰‰r‰ n. 10:een
            // flot osaa tulkita v‰lit kiitett‰v‰sti
            if (xtick_lkm > 10) { akselityyppi = 10 }

            //piirret‰‰n haetut arvopisteet
            
            var plotarea = $("#placeholder");
            var kaikki = [];
            var i = 0;
            // T‰ss‰ haetaan divi, jossa on esitystavan valinta. 
            // Tallennetaan omiin muuttujiin kunkin (bars, lines) tila,
            // halutaanko sit‰ n‰yttˆˆn vai ei
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

                    // ei tunnu tekev‰n mit‰‰n ?
                    inverseTransform: function (v) { return Math.exp(v); }
                };
            }
            else
                yvalinnat = {};
            
            // lasketaan piirrett‰vien arvojoukkojen lkm

            var arvojoukko_lkm = 0;
            for (arvojoukko in json) {
                arvojoukko_lkm++;
            }

            // Asetetaan piirrett‰v‰ data flotin ymm‰rt‰m‰‰n muotoon
            var i = 0;
            for (arvojoukko in json) {
                // Jos x-akseli ei ole Vuosi, akselin arvopisteet muotoon 0 .. 1 
                if (valittu != "Vuosi") {
                    for (j = 0; j < json[arvojoukko].length; j++) {
                        json[arvojoukko][j][0] = j;
                    }
                }

                // jos palkit valittu, ne piirret‰‰n vierekk‰in
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
                        show: barsBool, //T‰ss‰ barsBool kertoo, onko sen checkbox tai radiobutton valittu. Piirret‰‰n jos on

                        order: 1,
                        barWidth: 0.9/arvojoukko_lkm,
                        align: "center"
                    },
                    lines: {
                        show: linesBool
                    },  //T‰ss‰ linesBool kertoo, onko sen checkbox tai radiobutton valittu. Piirret‰‰n jos on
                    points: {
                        show: pointsBool
                    } //linesBool           
                }
            }

            // Piirrett‰v‰n datan asetukset
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

            // k‰sket‰‰n flotin piirt‰‰
            $.plot(plotarea, kaikki, options);
            
            
            // palautetaan piirtonappiin oletusteksti
            $nappula.button("reset");
            // luodaan tooltip-div, joka n‰ytet‰‰n tarvittaessa
            $("<div id='tooltip'></div>").css({
                position: "absolute",
                display: "none",
                border: "1px solid #fdd",
                padding: "2px",
                "background-color": "#fee",
                opacity: 0.80
            }).appendTo("body");
            
            
            // lis‰t‰‰n kuuntelija josko ollaan kuvaajan sellaseissa kohdassa ett‰ tarvitaan tooltippi‰
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
