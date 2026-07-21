import os, sys

# python3 server_mem.py 1000 12345 –debug –periodic-log mem.log

if len(sys.argv) < 3:
    print("Usage: python server_mem.py memsize port [--debug] [--periodic-log logfile]", file = sys.stderr)
    sys.exit(1)

try:
    size_mem = int(sys.argv[1])
    port = int(sys.argv[2])
except:
    print("Usage: python server_mem.py memsize port [--debug] [--periodic-log logfile]", file=sys.stderr)
    sys.exit(1)

debug = False
periodic_log = False  # Sert juste a regarder si les options sont activés dans la cmd

if "--debug" in sys.argv:
    debug = True

logfile = None

if "--periodic-log" in sys.argv:
    index = sys.argv.index("--periodic-log") # permet de trouver la position d’un elem dans une liste.

    # Verif qu'il y a bien un fichier apres
    if index + 1 >= len(sys.argv):
        print("Usage: python server_mem.py memsize port [--debug] [--periodic-log logfile]", file=sys.stderr)
        sys.exit(1)

    periodic_log = True
    logfile = sys.argv[index + 1]

# Partie tube

r_SF, w_SF = os.pipe()
r_FB, w_FB = os.pipe()

# PARTIE FRONTEND

pid_frontend = os.fork()

if pid_frontend == 0 :
    os.dup2(r_SF, 0)
    os.dup2(w_FB, 1)
    os.close(r_SF)
    os.close(w_SF)
    os.close(r_FB)
    os.close(w_FB)

    if debug:
        os.execvp("python3", ["python3","server_mem_frontend.py", str(size_mem), "--debug"])
    else:
        os.execvp("python3", ["python3","server_mem_frontend.py", str(size_mem)])

    # Si exec echoue
    print("Erreur exec frontend", file = sys.stderr)
    sys.exit(1)
     
# PARTIE BACKEND

pid_backend = os.fork()

if pid_backend == 0 :
    os.dup2(r_FB, 0)
    os.close(r_SF)
    os.close(w_SF)
    os.close(r_FB)
    os.close(w_FB)

    if periodic_log :
        fd_log = os.open(logfile, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        os.dup2(fd_log, 2)
        os.close(fd_log)

        os.execvp("python3", ["python3", "server_mem_backend.py", str(size_mem), "--periodic-log"])
    else:
        os.execvp("python3", ["python3", "server_mem_backend.py", str(size_mem)])

    print("Erreur backend", file = sys.stderr)

os.close(r_SF)
os.close(r_FB)
os.close(w_FB)

tube_vers_frontend = os.fdopen(w_SF, 'w')

for ligne in sys.stdin:
    tube_vers_frontend.write(ligne)
    tube_vers_frontend.flush()

tube_vers_frontend.close()

os.waitpid(pid_backend, 0) # PERE ATTEND FILS
os.waitpid(pid_frontend, 0)