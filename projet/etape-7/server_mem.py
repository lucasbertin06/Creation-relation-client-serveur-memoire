import os, sys, signal, time, socket

if len(sys.argv) < 3:
    print("Usage: python server_mem.py memsize port [--debug] [--periodic-log logfile]", file=sys.stderr)
    sys.exit(1)

try:
    size_mem_str = sys.argv[1] # On garde en string pour l'execvp plus tard
    port = int(sys.argv[2])      
except:
    print("Usage: python server_mem.py memsize port [--debug] [--periodic-log logfile]", file=sys.stderr)
    sys.exit(1)

debug = False
periodic_log = False
logfile = None

if "--debug" in sys.argv:
    debug = True

if "--periodic-log" in sys.argv:
    index = sys.argv.index("--periodic-log")
    if index + 1 < len(sys.argv):
        periodic_log = True
        logfile = sys.argv[index + 1]

# Tubes

r_F, w_F = os.pipe()    # Pipe 1 : Parent -> Frontend
r_B, w_B = os.pipe()    # Pipe 2 : Frontend -> Backend
r_Rep, w_Rep = os.pipe() # Pipe 3 : Rep (Front+Back) -> Parent

# FORK BACKEND 

pid_backend = os.fork()

if pid_backend == 0:
    os.dup2(r_B, 0)      # Le Backend lit dans le pipe qui vient du Frontend
    os.dup2(w_Rep, 1)    # Le Backend écrit ses résultats (stdout) dans le pipe de réponses
    
    for fd in (r_F, w_F, r_B, w_B, r_Rep, w_Rep):
        os.close(fd)

    if periodic_log:
        fd_log = os.open(logfile, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        os.dup2(fd_log, 2)
        os.close(fd_log)
        os.execvp("python3", ["python3", "-u", "server_mem_backend.py", size_mem_str, "--periodic-log"]) # MODIF pour etape 6 "-u"
    else:
        os.execvp("python3", ["python3", "-u", "server_mem_backend.py", size_mem_str])
    sys.exit(1)

# FORK FRONTEND 

pid_frontend = os.fork()

if pid_frontend == 0:
    os.dup2(r_F, 0)      # Le Frontend lit les ordres du Parent
    os.dup2(w_B, 1)      # Le Frontend écrit les ordres traduits (stdout) vers le Backend
    os.dup2(w_Rep, 2)    # Le Frontend écrit ses ok/error (stderr) vers le Parent
    
    for fd in (r_F, w_F, r_B, w_B, r_Rep, w_Rep):
        os.close(fd)

    if debug:
        os.execvp("python3", ["python3", "-u", "server_mem_frontend.py", size_mem_str, "--debug"]) # Ajout -u pour etape 6 pour ne pas laisser print dans buffer
    else:
        os.execvp("python3", ["python3", "-u", "server_mem_frontend.py", size_mem_str])
    sys.exit(1)

# serveur

os.close(r_F)
os.close(r_B)
os.close(w_B)
os.close(w_Rep)

frontend_stdin = os.fdopen(w_F, 'w')   
reponses = os.fdopen(r_Rep, 'r')   

# Socket TCP 

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind(('', port))
server_sock.listen(5)

while True:
    client_socket, addr_client = server_sock.accept()
    
    client_data = client_socket.recv(1024).decode("utf-8").strip() 

    if client_data :
        frontend_stdin.write(client_data + "\n")
        frontend_stdin.flush()       

        response_total = "" # lire TOUT puis prendre unique bonne reponse

        while True :
            response = reponses.readline()
            response_total += response

            if not response.startswith("[debug]") :
                break

        client_socket.sendall(response_total.encode())

    client_socket.close()