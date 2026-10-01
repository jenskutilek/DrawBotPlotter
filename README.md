# DrawBotPlotter

Plotter support for DrawBot

## Chiplotle

Chiplotle ([Website](https://sites.music.columbia.edu/cmc/chiplotle/)/[GitHub](https://github.com/drepetto/chiplotle)) is a Python library that implements and extends the HPGL (Hewlett-Packard Graphics Language) plotter control language.

## USB to Serial connection

- You will need a USB to serial (DB9 Male) adapter that is supported by Mac OS. Try one of these:
  PL2303 (driver below) / FT232 / CP2102 / CH340G
  https://www.prolific.com.tw/en/page/2/?s=PL2303

- And a DB9 Female to DB25 Male serial cable with the following wiring:
  https://sites.music.columbia.edu/cmc/chiplotle/manual/_static/SerialPlotterCable_Chiplotle.pdf

```
  1: 4
  2: 2
  3: 3
  4: 5 + 6
  5: 7
  6: 20
  7: 8
  8: 20
```
