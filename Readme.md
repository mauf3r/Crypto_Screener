# TradingView Crypto Screener

Dieses Jupyter Notebook fragt eine vorgegebene Liste von Handelspaaren von einer Börse (im Block *Settings* einstellen) ab, und erstellt eine Liste mit den lohnensten Paaren, um einen neuen Bot zu erstellen.

## Idee
TradingView stellt im Screener mehrere Handelssignale zur Verfügung. Hier wird das *Technical Rating* (TR) verwendet.

Was man in der normalen Screener-Ansicht nicht sehen kann: das Signal wird für verschiedene Intervalle angeboten. Es werden alle relevanten Werte von TradingView abgefragt. Das verwendete Signal berechnet sich wie folgt:

 **Bedingung**

 Vola (1D) > 1% `Volatility|1D > 1`

 & TR (1D): *Strong Buy* `Recommended.All > 0.5`
 
 & TR (1W): *Strong Buy* `Recommended.All|1W > 0.5`
 
 & TR (1M): *Buy* `Recommended.All|1M > 0.1`

 **Signal:**

 `MySignal = Volatility|1D * Recommended.All * Recommended.All|1W * Recommended.All|1M > 0.1`

 ## Anleitung

 vor dem ersten Ausführen des Codes:
 
 ein neue virtuelle Umgebung erzeugen:

 ```
 virtualenv env
 source env/bin/activate
 ```

und dann die nötigen Libraries installieren:

 `pip install -r requirements.txt`
