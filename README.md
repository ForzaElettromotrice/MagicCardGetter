# MagicCardGetter

Questo progetto è stato creato semplicemente per prendersi le versioni italiane delle carte di magic.

Per usare lo script basta caricare nella stessa cartella del file main.py un file al cui interno
sono elencate riga per riga le carte (con il nome inglese) che si vogliono cercare.
Ogni riga deve essere del formato `<quantità> <nome carta> (<codice set>) <numero carta> [flag opzionali]` usato dalla
maggior parte dei siti delle liste di carte.

Poi basta eseguire il programma e le carte saranno nella cartella `out_images` che verrà creata.

Nel file `config.toml` si può decidere:

- il percorso del file contenente la lista delle carte
- il percorso della cartella in cui salvare le immagini
- la risoluzione minima delle immagini da scaricare
- la risoluzione delle immagini dopo l'upscale (0 per disabilitare)
- i set da ignorare

Se non viene trovata la versione italiana del set richiesto, o non è della risoluzione richiesta, verrà scaricata la
versione italiana con risoluzione maggiore.
In caso non esista nessuna carta italiana, non verrà scaricata alcuna carta.
