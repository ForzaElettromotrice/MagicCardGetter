# MagicCardGetter

Questo progetto è stato creato semplicemente per prendersi le versioni italiane delle carte di magic.

Per usare lo script basta caricare nella stessa cartella del file stampacarte.py un file cards.txt al cui interno
sono elencate riga per riga le carte (con il nome inglese) che si vogliono cercare.
Ogni riga deve essere del formato `<quantità> <nome carta> (<codice set>) <numero carta> [flag opzionali]` usato dalla
maggior parte dei siti delle liste di carte.

Poi basta eseguire il programma e le carte saranno nella cartella `out_images` che verrà creata.
Se non viene trovata la versione italiana non verrà scaricata nessuna immagine