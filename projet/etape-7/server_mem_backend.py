import os, sys, signal, time

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
        instruction = input()
        mot = instruction.split()

        if len(mot) == 0 :
            continue

        cmd = mot[0] # Car .split() creer tableau
        
        if cmd == "POST" :
            if len(mot) != 3 : # Ex : POST base hex / nouveaux parametres 
                print("Il faut 3 arguments !")
                continue # ou continue (DEMANDER EN TP)

            try :
                base = int(mot[1])
                page_hex = bytearray.fromhex(mot[2]) # page entiere en hex
            except :
                print("error")
                continue

            if base < 0 or base + len(page_hex) > size_mem :
                print(f"error: POST out of bounds (base={base}, len={len(page_hex)}")
                continue

            memory[base:base + len(page_hex)] = page_hex
            print("ok")

        elif cmd == "GET" :
            if len(mot) != 3 : # Ex : GET base pagesize
                print("Il faut 3 arguments !")
                continue

            try : # Verif type argument
                base = int(mot[1])     
                pagesize = int(mot[2]) # taille page
            except :
                print("L'argument doit etre de type int !")
                continue

            if base < 0 or base + pagesize > size_mem :
                print(f"error: GET out of bounds (base={base}, pagesize={pagesize})")
                continue
 
            print(memory[base:base + pagesize].hex())  # retourne page en hex
            
        else : # Juste si Instruction pas GET ou POST
            print("Instruction non reconnue !")
            continue


    except EOFError :
        print("bye")
        break

