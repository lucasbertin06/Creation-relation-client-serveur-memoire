import sys, random
from remotememory import RemoteMemory
from controledmemory import ControledMemory

# paramètres (modifiables en ligne de commande)
write_rate = 0.1 # 10% d'écritures
sigma = 3 # écart-type de la distribution normale
num_accesses = 1000 # nombre d'accès à la mémoire
debug = False # afficher les messages de debug
alloc_actif = True # ajout de l'option
pagesize = 16 # taille page en octets (doit diviser segsize)
cachesize = 256 # taille cache local en octets (doit etre multiple de pagesize)

# lecture des arguments de la ligne de commande
try:
    if "--write_rate" in sys.argv:
        write_rate = float(sys.argv[sys.argv.index("--write_rate") + 1])
    if "--sigma" in sys.argv:
        sigma = float(sys.argv[sys.argv.index("--sigma") + 1])
    if "--num_accesses" in sys.argv:
        num_accesses = int(sys.argv[sys.argv.index("--num_accesses") + 1])
    if "--debug" in sys.argv:
        debug = True
    if "--not-alloc" in sys.argv: # ajout de l'option
        alloc_actif = False
    if "--pagesize" in sys.argv:
        pagesize = int(sys.argv[sys.argv.index("--pagesize") + 1]) # +1 pour avoir la valeur associé
    if "--cachesize" in sys.argv:
        cachesize = int(sys.argv[sys.argv.index("--cachesize") + 1]) # ici aussi 
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    segname = sys.argv[3]
    segsize = int(sys.argv[4])

except:
    print("Usage: python client.py <host> <port> <segname> <segsize> OPTIONS\nOPTIONS:\n  --write_rate <float>  taux d'écriture (défaut: 0.1)\n  --sigma <float>       écart-type de la distribution normale (défaut: 3)\n  --num_accesses <int>  nombre d'accès à la mémoire (défaut: 1000)\n  --debug               afficher les messages de debug\n  --not-alloc           ne pas allouer/libérer le segment\n  --pagesize <int>      taille d'une page en octets (défaut: 16)\n  --cachesize <int>     taille du cache en octets (défaut: 256)", file=sys.stderr)
    sys.exit(1)

index = 0

# création de la mémoire contrôlée
with ControledMemory(RemoteMemory(host, port, segname, segsize, debug, alloc = alloc_actif, pagesize = pagesize, cachesize = cachesize)) as mem:
    # boucle de lecture/écriture
    for i in range(num_accesses):
        index = int(random.gauss(index, sigma)) % segsize
        if random.random() < write_rate:
            mem[index] = random.randint(0, 255)            
        else:
            _ = mem[index]