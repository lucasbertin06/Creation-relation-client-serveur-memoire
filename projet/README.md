# Projet : Projet de système d’exploitation 

#### Lucas Bertin 

## AUTO-EVALUATION 

Le projet a été fait dans son intégralité, désormais, je vais présenter chaque étape de maniere succinte et donner le taux de réussite de l'etape selon mes analyses

### Etape 1 / taux de réussite de l'etape = 100 % :

Implementation de "server_mem_backend.py" :  

    1. Mise en place de la gestion d'erreur  
    2. "GET i" : retourne l'octet à l'indice i, ou une erreur si hors bornes  
    3. "POST i o" : remplace l'octet à l'indice i par o, ou erreur si invalide  
    4. Memoire initialisée avec le bytearray  



### Etape 2 / taux de réussite de l'etape = 100 % :

Amelioration de "server_mem_backend.py" : 

    1. Ajout de l'option "--periodic-log" :  
        - Toutes les secondes, la totalité de la mémoire est écrite sur la sortie d'erreur grace au handler qui fonctionne a la reception du signal SIGALRM
        - le handler est activé seuelement lorsque -periodic-log est activé dans la ligne de commande.
        - code testé avec "tail -f mem.log", tout marche ! (testé avec le prof en tp à la premiere séance)

### Etape 3 / taux de réussite de l'etape = 100 % : 

Implementation de "server_mem_frontend.py" :

    1. Maintien d'une table de segment (segments_table) sous forme de dictionnaire  
    2. Mise en place de la commande "PUT segname size" qui alloue un segment en cherchant des espaces libres avec verifications : Erreur si memoire pleine ou nom de segment deja utilisé, recherche de chevauchements.  
    3. "GET segname index" renvoie l'octet à l'indice index du segment segname (traduction de l'index relatif en addresse absolue)
    4. "POST segname index octet" ecrit l'octet octet à l'indice index du segment segname
    5. "DELETE segname" supprime le segment segname de la table
    6. Mise en place d'un debug_print() qui, dans le cas ou l'option "--debug" est activé, affiche la table des segments sur la sortie d'erreur apres chaque requete

### Etape 4 / taux de réussite = 100 % :

Implementation de server_mem.py + amelioration backend/frontend :  

    1. Prend memsize et port en arguments, ainsi que --debug et --periodic-logfile  
    2. Creation de deux tubes : server_mem -> frontend et frontend -> backend (comme demandé par le prof et l'image de l'etape 4)
    3. Lance server_mem_backend et server_mem_frontend comme processus fils avec fork et os.execvp
    4. On redirige les entrées/sorties avec dup2
    5. si "--periodic-log" actif : redirige stderr vers logfile, sinon, passe au frontend
    5. Le parent attend ses fils avec waitpid
    6. Amelioration sur server_mem_backend et server_mem_fronted : ecriture des messages d'erreurs avec os.write pour eviter les erreurs de buffer (demandé par prof de TP)

### Etape 5 / taux de réussite = 100 % :

Evolution de server_mem.py :

    1. On veut desormais accepter des clients avec des sockets TCP, ainsi, le serveur accepte un client, lit son instruction , renvoie la reponse, ferme la connexion
    2. Ajout d'un 3eme pipe pour recuperer les reponses du frontend et backend 
    3. La reponse au client est soit la sortie standard, ou la sortie d'erreur du frontend : GET/POST -> reponse backend sur stdout -> w_Rep -> client
                                                                                             PUT/DELETE/erreurs -> reponse frontend sur stderr -> w_Rep -> client 
    4. Les tests avec telnet sont verifiées et sont sans erreurs : Ex : "telnet localhost 12345"

### Etape 6 / taux de réussite = 100 %:

Mise en place du client sans cache :

#### Etape 6.1 : 

remotememory.py :

    1. Permet la connexion TCP par requête
    2. Code testé comme demandé
    3. Explication dans commentaire.txt des différentes méthodes

#### Etape 6.2 :

Test avec deux clients sur deux segments différents :

    1. Aucunes corruption detectée, les segments sont indépendant, les acces ne sentremelent pas
    2. Comportement conforme

#### Etape 6.3 :

Segements partagés :

    1. Ajout de l'option "--not-alloc" dans client.py pour choisir de ne pas allouer le segment 
    2. Modification dans "__exit__" : DELETE seulement si "alloc =TRUE" puisqu'avant, la suppression etait automatique
    3. Test de deux clients sur le meme segment, corruption detectée car abscence de synchronisation entre les clients

### Etape 7 / taux de reussite = 60 % :

Mise en place du cache :  

    1. Modification de POST et GET pour travailler sur des pages entieres (hex)
    2. Mise en place d'un algorithme FIFO pour gérer les pages à enlever du cache quand ce dernier est plein  
  
  
## Estimation   

Explication :

Je pense avoir globalement réussi de maniere correcte jusqu'à l'etape 6, les tests ont réussis, des aides de personnes exetrieurs m'ont permis d'avoir un code compréhensible et structuré.

Toutefois, à l'etape 7, mes tests pour gérer le gain de temps n'ont pas été réellement concluant, il y a tres peu voir aucunes amélioration au niveau du temps. 
Je pense que le probleme vient surement de l'algorithme utilisé : FIFO, qui n'est pas forcement le plus adéquat dans la situation, dans le cas ou on eneleve du cache une page souvent utilisés.
Apres quelques recherches, je pense que d'autres algorithmes auraient pu mieux convenir.

Et je pense ne pas être à l'abris de quelques erreurs.
