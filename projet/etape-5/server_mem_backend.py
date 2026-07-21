import os, sys, signal, time, socket

if len(sys.argv) < 2 or len(sys.argv) > 3  : # Verif nb arguments
    print("Usage: python server_mem_backend.py memsize")
    sys.exit(1)

if len(sys.argv) == 3 and sys.argv[2] != "--periodic-log":
    print("Usage: python server_mem_backend.py memsize")
    sys.exit(1)

try : # Verif si argument int
    size_mem = int(sys.argv[1])
except :
    print("Usage: python server_mem_backend.py memsize")
    sys.exit(1)

memory = bytearray([32] * size_mem)

if "--periodic-log" in sys.argv :
    def handler(signum, frame) :
        print(memory, file = sys.stderr)
        signal.alarm(1)

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1) # Lance le premier singal.alarm pour le repeter ensuite

while True :
    try :
        instruction = os.read(0, 1024).decode("utf-8")
        mot = instruction.split()

        if len(mot) == 0 :
            continue

        cmd = mot[0] # Car .split() creer tableau
       
        if cmd == "POST" :
            if len(mot) != 3 : # Ex : POST 10 76
                print("Il faut 3 arguments !", file = sys.stderr)
                continue # ou continue (DEMANDER EN TP)

            try :
                i = int(mot[1])
                o = int(mot[2])
            except :
                print("Les arguments doivent etre de type int !", file = sys.stderr)
                continue

            if i < 0 or i >= size_mem :
                print(f"error: index {i} out of bounds", file = sys.stderr)
                continue
           
            elif o < 0 or o > 255 :
                print(f"error: POST instruction requires a byte as a second argument '{mot[2]}' out of byte range (0-255)", file = sys.stderr)
                continue
           
            else :
                memory[i] = o # POST remplace l'octet 32 postion mot[1] par l'octet mot[2]
                print("ok")
                continue
       
        elif cmd == "GET" :
            if len(mot) != 2 : # Ex : GET 10
                print("Il faut 2 arguments !", file = sys.stderr)
                continue

            try : # Verif type argument
                i = int(mot[1])           # Demander si important d'avoir nommer i que pour GET
            except :
                print("L'argument doit etre de type int !", file = sys.stderr)
                continue

            if 0 <= i < size_mem: # On regarde si on est pas "out of bounds" (DEMANDER POUR EGALITE)
                print(memory[i])
            else :
                print(f"error: index {i} out of bounds", file = sys.stderr)
                continue
           
        else : # Juste si Instruction pas GET ou POST
            print("Instruction non reconnue !", file = sys.stderr)
            continue

    except EOFError :
        print("bye")
        break