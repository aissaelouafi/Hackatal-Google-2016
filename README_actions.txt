HackaTAL - Tache de détection d'évènements
==========================================

Description de la tâche:
------------------------

La tâche consiste à détecter les événements dans les matchs de l'euro 2016 à partir de tweets collectés pour chacun des matchs.
Ces événements détectés peuvent ensuite servir à générer automatiquement les "fils live de commentaires" que l'on retrouve sur les sites sportifs.

La liste des événements à détecter sont les buts, les cartons, les changements, le début et fin de la première période, le début et fin de la seconde période, les penaltys, les tirs au but (ceci inclut tout type de tirs au buts comme les coups de pied, les têtes, etc).

Pour certains types d’événements des informations complémentaires sont à fournir (nom du buteur, nom du tireur, noms des joueurs sortant et entrant, nom du pays pour lequel le penalty est sifflé)

Le tableau ci-dessous résume les événements à détecter.

Label	Type Evenement	Annotation complémentaire éventuelle (en fonction du type d'événement)
BUT	BUT	Nom du buteur
CJA	CARTON JAUNE	Nom du joueur sanctionné
CRO	CARTON ROUGE	Nom du joueur sanctionné
CGT	CHANGEMENT	Nom du joueur sortant ;  Nom du joueur entrant
D1P	DEBUT 1ERE PERIODE	N/A
D2P	DEBUT 2NDE PERIODE	N/A
F1P	FIN 1ERE PERIODE	N/A
F2P	FIN 2NDE PERIODE	N/A
PEN	PENALTY	Nom du pays pour lequel le penalty est sifflé
TIR	TIR AU BUT	Nom du tireur

  
Format des données
------------------

Les tweets collectés sont au format JSON fourni par l'API Tweeter.
Les annotations ont été produites en se référant aux "fils live de commentaires" du site sport24.lefigaro.fr

Les annotations sont des fichiers textes tabulés au format suivant
HEURE_ABSOLUE (HH:MM)	TYPE_EVENEMENT	[NOM_JOUEUR/NOM_PAYS]

Les deux premiers champs sont obligatoires et le troisième est présent pour les événements de type BUT, CJA, CRO, CGT, PEN, TIR.

Un exemple d’annotation est donné ci-dessous:
TEMPS ABSOLU (HH:MIN)	EVENEMENT	ANNOTATION COMPLEMENTAIRE	
21:01:00	D1P		
21:02:00	TIR	Matuidi	
21:04:00	TIR	Pintilii	
21:05:00	TIR	Stancu	
21:11:00	TIR	Griezmann	
21:12:00	TIR	Giroud	
21:15:00	TIR	Griezmann	
21:28:00	TIR	Pogba	
21:33:00	CJA	Chiriches	
21:37:00	TIR	Griezmann	
21:45:00	TIR	Payet	
21:46:00	CJA	Rat	
21:48:00	TIR	Giroud	
21:48:00	F1P		
22:04:00	D2P		
22:07:00	TIR	Stancu	
22:12:00	TIR	Giroud	
22:16:00	TIR	Pogba	
22:17:00	BUT	Giroud	
22:19:00	TIR	Andone	
22:20:00	CGT	Andone Alibec	 
22:23:00	PEN	Roumanie	
22:24:00	BUT	Stancu	
22:25:00	CGT	Griezmann ; Coman	
22:28:00	CJA	Giroud	
22:31:00	CGT	Stanciu ; Chipciu	
22:36:00	CGT	Pogba ; Martial	
22:37:00	CJA	Popa	
22:39:00	TIR	Hoban	
22:40:00	TIR	Martial	
22:41:00	CGT	Popa ; Torje	
22:48:00	BUT	Payet	
22:53:00	F2P		 

Données d’entraînement/développement
------------------------------------

Les données d’entraînement/développement sont constituées des 24 matchs de poule de la 1ere et 2eme journée de l'EURO 2016.
Les matchs sont répartis dans les différents groupes de la compétition (groupes A à F)
Chaque dossier Groupe_X est subdivisé en 3 sous-dossiers ar, fr, en, qui contiennent chacun respectivement les tweets collectés pendant la période du match en arabe, français et anglais.

Dans le dossier fr, se trouvent en plus du JSON, les "fils live" des matchs au format html collectés sur le site sport24.lefigaro.fr ainsi que les annotations extraites du fil live.

La nomenclature des données JSON collectées sur Twitter est la suivante:
	<PAYS1>_<PAYS2>_<YYYY>_<MM>_<DD>_<HH>h_<lang>.json

Les "fils de matchs" présents dans le dossier fr suivent la même nomenclature avec une extension html, à savoir:
	<PAYS1>_<PAYS2>_<YYYY>_<MM>_<DD>_<HH>h_fr.html

Les annotations suivent la même nomenclature avec une extension tsv:
	 <PAYS1>_<PAYS2>_<YYYY>_<MM>_<DD>_<HH>h_fr.tsv


A titre d'exemple, le contenu du dossier Groupe_A est donné ci-dessous:

|-- Groupe_A
|   |-- ar
|   |   |-- Albanie_Suisse_2016-06-11_15h_ar.json
|   |   |-- France_Albanie_2016-06-15_21h_ar.json
|   |   |-- France_Roumanie_2016-06-10_21h_ar.json
|   |   `-- Roumanie_Suisse_2016-06-15_18h_ar.json
|   |-- en
|   |   |-- Albanie_Suisse_2016-06-11_15h_en.json
|   |   |-- France_Albanie_2016-06-15_21h_en.json
|   |   |-- France_Roumanie_2016-06-10_21h_en.json
|   |   `-- Roumanie_Suisse_2016-06-15_18h_en.json
|   `-- fr
|       |-- Albanie_Suisse_2016-06-11_15h_fr.html
|       |-- Albanie_Suisse_2016-06-11_15h_fr.json
|       |-- Albanie_Suisse_2016-06-11_15h_fr.tsv
|       |-- France_Albanie_2016-06-15_21h_fr.html
|       |-- France_Albanie_2016-06-15_21h_fr.json
|       |-- France_Albanie_2016-06-15_21h_fr.tsv
|       |-- France_Roumanie_2016-06-10_21h_fr.html
|       |-- France_Roumanie_2016-06-10_21h_fr.json
|       |-- France_Roumanie_2016-06-10_21h_fr.tsv
|       |-- Roumanie_Suisse_2016-06-15_18h_fr.html
|       |-- Roumanie_Suisse_2016-06-15_18h_fr.json
|       `-- Roumanie_Suisse_2016-06-15_18h_fr.tsv


Format de soumissions
---------------------
Les équpes doivent soumettre leur résultats sous format d'une archive suivant le nommage suivant:
	<NOM_EQUIPE>_<ID_SYSTEME>.tgz
ou
	ID_SYSTEM = SYS1 | SYS2 | ...
        NOM_EQUIPE = TEAM_1 | TEAM_2 | ...

L'archive doit contenir un fichier d'événements détectés par match au même format que celui décrit dans la section "Format des données".

La nomenclature des fichiers hypothèses produits par un système est la suivante: 
	<PAYS1>_<PAYS2>_<YYYY>_<MM>_<DD>_<HH>h_<ID_SYSTEM>_<NOM_EQUIPE>.tsv

ou 	
	ID_SYSTEM = SYS1 | SYS2 | ... 
	NOM_EQUIPE = TEAM_1 | TEAM_2 | ...	

Évaluation des résultats
------------------------
La Précision, le Rappel et la F-mesure seront calculés automatiquement en comparant les événements détectés dans l’hypothèse à ceux dans la référence




Bon HackaTAL !

Questions/Remarques
-------------------
djamel.mostefa@systrangroup.com

