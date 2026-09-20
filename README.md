# Blackjack Assistant — exacte-samenstelling-versie

Windows-tool die live meekijkt met een schermregio, kaarten herkent, de
**exacte samenstelling van het schoen** onthoudt, en per beslissing de
**wiskundig exacte win-kans en verwachte waarde (EV)** berekent voor Hit,
Stand, Double en Split.

Bedoeld voor gratis/play-money spellen. Check de voorwaarden van de site die
je gebruikt — sommige verbieden automatisering ook bij gratis spelen.

## Wat maakt dit nauwkeuriger dan kaarttellen?

Puntensystemen zoals Hi-Lo (+1/0/−1 per kaart) zijn geheugentrucs voor
mensen: ze comprimeren de deckstand tot één getal, en zijn dus per definitie
een benadering. Deze tool doet dat niet. Hij houdt bij hoeveel azen, 2'en,
… 10-waarde-kaarten er **precies** nog in het schoen zitten, en rekent
daarmee via een uitputtende kansboom de werkelijke kansen uit.

Geen simulatie, geen Monte Carlo-schatting: voor elke mogelijke volgende
kaart wordt de exacte kans (aantal resterend ÷ totaal resterend) gewogen en
recursief doorgerekend tot elke hand is afgelopen.

**Dat het geheugen er echt toe doet**, blijkt uit dit voorbeeld (1 deck,
hand 16 tegen dealer-10):

| Schoen-situatie | HIT | STAND | Advies |
|---|---|---|---|
| Vers deck | −0,507 | −0,543 | **HIT** |
| Lage kaarten (2–6) grotendeels op | −0,815 | −0,769 | **STAND** |

Dezelfde hand, hetzelfde dealer-kaartje, ander advies — puur omdat de tool
weet wat er nog in het schoen zit.

## Omgang met de dealer

- De **zichtbare upcard** wordt gebruikt als basis voor de volledige
  dealer-uitkomstverdeling (kans op 17/18/19/20/21/bust).
- De **verdekte kaart** wordt *niet* uit het schoen gehaald zolang hij
  onzichtbaar is — hij wordt behandeld als een onbekende kaart uit het
  resterende schoen, wat wiskundig correct is.
- **Peek-regel**: bij een 10 of Aas als upcard heeft de dealer al
  gecontroleerd op blackjack. Had hij die, dan was de hand al voorbij. Die
  gevallen worden dus uit de kansverdeling geconditioneerd — zonder deze
  correctie worden alle EV's tegen een 10/Aas structureel te pessimistisch.
- Zodra de dealer zijn verdekte kaart omdraait, wordt die herkend en pas dán
  uit het schoen gehaald.

## Validatie
De engine is getoetst aan gepubliceerde referentiewaarden en aan de
standaard basisstrategie:

- 8,8 tegen dealer-10: engine geeft split-EV **−0,4748**; gepubliceerde
  referentie (Wizard of Odds) ligt op ≈ −0,4706.
- 12 standaard basisstrategie-situaties (hard, soft, pairs) leveren allemaal
  de verwachte actie op.

Meegemodelleerde regels: dealer staat op soft 17, double na split (DAS)
toegestaan, re-splitsen tot 4 handen, gesplitste azen krijgen één kaart.

## Betrouwbaarheid: waarschuwing bij gemiste/onzekere kaarten

Als de tool een kaartvorm vindt maar 'm niet met genoeg zekerheid aan een
template kan koppelen, wordt die kaart NIET meegeteld in de berekening -
en dat is precies het risico: het overlay zou dan stilzwijgend een net iets
verkeerde (te optimistische) berekening tonen.

Om dat te voorkomen toont het overlay nu een gele waarschuwingsbalk zodra dit
gebeurt, met twee niveaus:

- **"NIET herkend"**: er is een kaartvorm gevonden die aan geen enkel
  template gekoppeld kon worden. Deze kaart ontbreekt in de berekening — het
  advies is deze cyclus niet betrouwbaar. Het actie-label krijgt de
  toevoeging "(onzeker)" en de EV-cijfers worden grijs getoond.
- **"lage herkenningszekerheid"**: de kaart is wel herkend, maar met een
  score die maar net over de drempel zit. Waarschijnlijk klopt het, maar
  controleer het even.

Dit is een per-cyclus waarschuwing: zodra de volgende screenshot de kaart wél
goed herkent, verdwijnt de balk vanzelf.

## Kalibratie-voortgang op het scherm

`calibrate.py` opent nu automatisch een tweede, klein always-on-top venster
met een 13×4-rooster (alle rangen × alle kleuren). Elke kaart die je
kalibreert kleurt direct groen, met een teller "x/52 kaarten gekalibreerd"
erboven. Zo zie je in één oogopslag welke kaarten je nog mist, zonder de
console-tekst te hoeven bijhouden. De live-overlay (`main.py`) toont er ook
een regel van: "Kalibratie: x/52 kaarten geladen".

## Een .exe-bestand maken (optioneel)

Ik kan vanaf hier geen kant-en-klare Windows-.exe meeleveren — die moet
gebouwd worden ÓP Windows zelf (PyInstaller compileert niet cross-platform).
Het is wel met één commando te doen:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
build_exe.bat
```

Dit levert `dist\BJAssistant.exe` en `dist\BJKalibreren.exe` op. Zet ze
samen in dezelfde map (ze delen `config.json` en `templates\`, die als je ze
voor het eerst start naast de .exe-bestanden worden aangemaakt) en dubbelklik
om te starten — geen Python-installatie meer nodig om ze te gebruiken.

**Als het bouwen een tkinter-fout geeft**: herinstalleer Python en zorg dat
tijdens de installatie het vinkje bij "tcl/tk and IDLE" aanstaat (staat
standaard aan bij de officiële installer van python.org).

## Snelste manier om te starten

Dubbelklik op **`run.bat`**. Dat regelt alles automatisch: Python-detectie,
de virtuele omgeving, de benodigde pakketten, en een simpel menu om te
kalibreren of te starten. Geen PowerShell-commando's nodig.

De eerste keer duurt langer (installeert de pakketten); daarna start het
menu meteen. Als Python zelf nog ontbreekt of het tcl/tk-onderdeel mist,
zie je een duidelijke Nederlandse melding met wat te doen, in plaats van een
Python-foutmelding.

## Nog makkelijker: laat GitHub de .exe voor je bouwen

Heb je op je eigen pc problemen met Python (bijvoorbeeld een kapotte
tcl/tk-installatie)? Dan hoef je daar niets aan te repareren. GitHub heeft
eigen, schone Windows-machines die de `.exe`-bestanden voor je kunnen bouwen
— jij hebt dan zelf helemaal geen werkende Python nodig, alleen om de
uiteindelijke `.exe` te *gebruiken* op de site zelf (en zelfs dat niet, een
losse `.exe` draait zonder Python-installatie).

1. Maak een gratis account op [github.com](https://github.com) als je er
   nog geen hebt.
2. Klik rechtsboven op **+** → **New repository**. Geef een naam (bv.
   `bj-assistant`), laat 'm gerust private, klik **Create repository**.
3. Op de nieuwe, lege repo-pagina: klik **uploading an existing file**.
   Sleep alle bestanden en mappen uit deze projectmap erin (inclusief de
   verborgen map `.github`) en klik **Commit changes**.
4. Ga naar het tabblad **Actions** bovenaan de repo. Er start automatisch
   een workflow genaamd "Build Windows EXE" (dit kan 2-3 minuten duren).
5. Als hij groen is (klaar), klik erop, en onderaan de pagina staat
   **Artifacts** → **BJAssistant-windows**. Download die zip: hierin zitten
   `BJAssistant.exe` en `BJKalibreren.exe`, gebouwd op een schone
   Windows-machine, klaar om te gebruiken zonder dat jouw pc Python nodig
   heeft.

Dit lost het tcl/tk-probleem definitief op, omdat de build niet meer
afhankelijk is van jouw lokale Python-installatie.

## Installatie (Windows) — handmatige/gedetailleerde route

1. Installeer [Python 3.10+](https://www.python.org/downloads/) (vink
   "Add python.exe to PATH" aan).
2. In PowerShell, in de projectmap:
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Gebruik

### Stap 1 — Kalibreren (eenmalig per site)

```powershell
python src\calibrate.py
```

Elke site tekent kaarten anders, dus de tool moet één keer leren hoe ze er
daar uitzien. Typ per kaart de rang en kleur, teken er een strak vak omheen.
Labels: rang `A,2..10,J,Q,K`, kleur `S/H/D/C`. Je kan later opnieuw draaien om
ontbrekende kaarten aan te vullen; bestaande templates blijven bewaard.

### Stap 2 — Regio's instellen en starten

```powershell
python src\main.py --setup --decks 6
```

Teken het vak om jouw kaarten, daarna om de dealerkaart(en). Kies ze ruim
genoeg voor een hand van 4+ kaarten. Daarna volstaat:

```powershell
python src\main.py
```

### Bij schudden

Klik op **"Nieuw schoen (geschud)"** in het overlay. Dat zet het geheugen
terug naar een vol schoen. Dit is belangrijk: zonder die reset rekent de tool
verder met een schoenstand die niet meer klopt.

## Instellingen (`config.json`)

- `num_decks` — aantal decks; moet kloppen met de site (vaak 6 of 8).
- `capture_interval_ms` — hoe vaak het scherm gelezen wordt.
- `match_threshold` — strengheid kaartherkenning (0–1). Verkeerde
  herkenningen? Verhogen. Te weinig herkenning? Verlagen.

## Wat de tool níet automatisch weet

- **Het aantal decks** leest hij niet van het scherm; dat stel jij in.
- **Wanneer er geschud wordt** ziet hij niet; dat geef jij aan met de knop.
- Bij online RNG-blackjack wordt vaak na élke hand opnieuw geschud. Dan heeft
  schoen-geheugen geen voorspellende waarde — elke hand is onafhankelijk. Het
  geheugen is alleen zinvol bij spellen met een doorlopend schoen (typisch
  live-dealer tafels).

## Prestaties

De meeste handen zijn binnen ~0,5 seconde doorgerekend. Zware gevallen (A,A
met re-splits) kunnen enkele seconden duren; daarom draait de berekening in
een achtergrondthread met caching, zodat het overlay soepel blijft en je
"Berekenen…" ziet in plaats van een bevroren venster.

## Projectstructuur

```
bj-assistant/
├── requirements.txt
├── build.spec              PyInstaller-configuratie voor de .exe's
├── build_exe.bat            1-klik build-script (op Windows draaien)
├── config.json            (na --setup)
├── templates/             (kaart-templates uit calibrate.py)
└── src/
    ├── capture.py          schermopname
    ├── region_selector.py  vak-selectie met de muis
    ├── card_detect.py      kaart-rechthoeken vinden
    ├── card_matcher.py     kaart identificeren
    ├── calibrate.py        kalibratietool
    ├── calibrate_overlay.py voortgangsvenster tijdens kalibreren
    ├── shoe.py             EXACTE schoen-samenstelling + geheugen
    ├── exact_engine.py     exacte kansberekening (kansboom)
    ├── engine_worker.py    achtergrondthread + cache
    ├── counter.py          Hi-Lo telling (optioneel, ter referentie)
    ├── strategy.py         basisstrategie-tabellen (fallback/referentie)
    ├── overlay.py          advies-venster
    └── main.py             hoofdloop
```

## Beperkingen, eerlijk

- Kaartherkenning via beeld is nooit 100%; bij UI-wijzigingen van de site
  moet je mogelijk opnieuw kalibreren. De rekenkant is exact, de *waarneming*
  is de zwakke schakel.
- De split-EV negeert de kleine correlatie tussen de twee split-handen
  (gangbare vereenvoudiging, ook in professionele tools).
- Surrender en verzekering zitten niet in de engine.
- Als de kaartherkenning een kaart mist, klopt het schoen-geheugen niet meer.
  Dit is nu zichtbaar: het overlay waarschuwt actief wanneer dit gebeurt (zie
  hierboven), in plaats van stilzwijgend door te rekenen. Bij twijfel: klik na
  een shuffle op "Nieuw schoen" en controleer de kaartentelling in het
  overlay tegen wat je op het scherm ziet.
