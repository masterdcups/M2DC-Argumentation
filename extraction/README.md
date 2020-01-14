# Extraction

## Usage

Le contenu de ce dossier permet d'extraire le graphe d'argumentation de :

 - Wikidebats

Pour cela, ouvrez un terminal unix dans ce dossier et tapez :

	# Wikidebats
	./wd_extract.sh
	
Cela produit deux fichiers *wd_nodes.csv* et *wd_edges.csv* représentant le graphe. Ils peuvent être importés avec *Neo4j* ou *Gephi* par exemple (*cf.* bas de page).

## Description

### Modèle(s)

On considère que les débats, arguments, sous-arguments, objections, etc. sont tous des arguments au sens large.

Le graphe d'argumentation est un graphe étiqueté :

 - Les sommets ont un *label* (le texte de l'argument) et une *url* (pour les besoins de l'extraction : celle de la page sur WikiDebats)
 - Les arcs représentent les relations de soutien (*resp.* d'attaque) ont un poids égal à 1 (*resp. -1).

### Procédure

Sur WikiDebats, les arguments ont une page dédiée (sauf les arguments terminaux). Ainsi les liens HTML de WikiDebats couvrent les arcs du graphe.

 1. On télécharge et simplifie les pages du site, de façon à ne garder que la structure du graphe.
 2. On parse cette collection de fichiers pour reconstruire le graphe
 
 Le script *wd_extract.sh* effectue ce travail

#### Données brutes (WikiDebats)

On a trois cas :

1. Les débats sont les puits du graphe, ils ont une page dédiée, accessible depuis la *sitemap*.
2. Les arguments et sous-arguments étayés sont les sommets intermédiaires, ils ont une page dédiée accessible depuis la page de l'argument soutenu/attaqué.
3. Les arguments terminaux (feuilles) sont les sources du graphe, ils n'ont pas de page dédiée et sont représentés uniquement dans la page de l'argument soutenu/attaqué.

Avec XSLT, on transforme chaque page en un fichier *xxx.csv* contenant les lignes *a1;b1;c1*, *a2;b2;c2*, etc. Cela signifie que l'argument d'url *xxx* à pour parents les arguments d'identifiant *ai*, de label *bi* avec un poids *ci*.

Le traitement est effectué en boucle jusqu'à ce qu'il ne produise plus de nouveaux fichiers : toutes les pages sont alors téléchargées et converties.


## Interrogation et visualisation

### Neo4j

Après avoir copié les fichiers *wd_nodes.csv* et *wd_edges.csv* dans le dossier *import* de la base, il faut exécuter les ordres d'insertion suivants :

	// Create nodes
	LOAD CSV WITH HEADERS FROM "file:///wd_nodes.csv" AS row
	  CREATE (:Argument {url: row.url, label: row.label, n: toInteger(row.n), origin: "wd"})
	  
	// Create indexes
	CREATE INDEX ON :Argument(n)
	CREATE INDEX ON :Argument(origin)
	
	// Create 'Support' edges
	LOAD CSV WITH HEADERS FROM "file:///wd_edges.csv" AS row
	  WITH row WHERE toInteger(row.weight) > 0
	  MATCH (n1:Argument {n: toInteger(row.n1), origin:"wd"}),
	    (n2:Argument {n: toInteger(row.n2), origin: "wd"})
	  WITH row, n1, n2
	  CREATE (n1)-[:Support {w: toInteger(row.weight)}]->(n2)

	// Create 'Attack' edges
	LOAD CSV WITH HEADERS FROM "file:///wd_edges.csv" AS row
	  WITH row WHERE toInteger(row.weight) < 0
	  MATCH (n1:Argument {n: toInteger(row.n1), origin:"wd"}),
	    (n2:Argument {n: toInteger(row.n2), origin:"wd"})
	  WITH row, n1, n2
	  CREATE (n1)-[:Attack {w: toInteger(row.weight)}]->(n2)

Une fois cela fait, nous pouvons interroger la base et visualiser le résultat des requêtes dans le navigateur :


	// Get debate list (nodes without outgoing edges)
	MATCH (a:Argument {origin:"wd"}) WHERE NOT (a)-[]->(:Argument) 
		  RETURN a.n, a.label

	//a.n	a.label
	//17	"Faut-il supprimer les notes à l'école ?"
	//158	"Faut-il préserver les Murs à pêches de Montreuil ?"
	//159	""
	//160	"Le réchauffement climatique est-il dû à l'activité humaine ?"
	//161	"Faut-il arrêter de manger des animaux ?"
	//162	"Faut-il instaurer un revenu de base ?"
	//163	"Faut-il instaurer un salaire à vie ?"
	//[...]

	// Get the #192 debate
	MATCH (a:Argument)-[*]->(b:Argument {n: 192, origin: "wd"})
	  RETURN a, b
	  
![Neo4j viz](images/n4j_example.svg  "Neo4j visualization")

Le système de requêtage permet aussi de détecter des problèmes dans le graphe d'argumentation.

	// Cycles
	MATCH (n)-[*]->(m) WHERE n = m RETURN n, m

![Cycles](images/n4j_cycles.svg  "Cycles in the argumentation graph")

### Gephi

Gephi permet la visualisation de la totalité du graphe.

![Gephi viz](images/gephi_example.png  "Gephi visualization")
Spatialisation (OpenOrd + Yifan Hu proportionnel) du graphe non pondéré (tous les arcs sont de poids égal à 1)

