import os, sys, signal, time, socket

if len(sys.argv) < 2 or len(sys.argv) > 3:  # Verif nb arguments
    print("Usage: python mem_server_frontend.py memsize", file = sys.stderr)
    sys.exit(1)

if len(sys.argv) == 3 and sys.argv[2] != "--debug":
    print("Usage: python mem_server_frontend.py memsize", file = sys.stderr)
    sys.exit(1)

try:  # Verif si argument int
    size_mem = int(sys.argv[1])
except:
    print("Usage: python mem_server_frontend.py memsize", file = sys.stderr)
    sys.exit(1)

segments_table = {}

debug = False

if "--debug" in sys.argv:
    debug = True


def debug_print():
    if debug:
        print(f"[debug] segments_table = {segments_table}", file = sys.stderr)


while True:
    try:
        instruction = input()  # Peut changer avec os.read
        mot = instruction.split()

        if len(mot) == 0:  # Eviter erreur si ligne vide
            continue

        cmd = mot[0]  # Car .split() creer tableau

        if cmd == "PUT":
            if len(mot) != 4 : # Desormais, on prend pagesize en arg : PUT seganme segsize pagesize
                print("error", file=sys.stderr)
                continue

            segname = mot[1]

            try:
                segsize = int(mot[2])
                pagesize = int(mot[3]) 
            except:
                print("error", file = sys.stderr)
                continue

            if segname in segments_table:
                print(f"error: segment {segname} already exists", file = sys.stderr)
                continue

            if segsize <= 0 or pagesize <= 0 : # ajout condition sinon sur pagesize
                print("error", file = sys.stderr)
                continue

            if segsize % pagesize != 0 : # enoncé dit "pagesize (qui devra diviser segsize)"
                print(f"error : segsize {segsize} must be a multiple of pagesize {pagesize}", file = sys.stderr)
                continue

            liste_segment = [0]

            for name in segments_table:
                base = segments_table[name]["base"]
                size = segments_table[name]["size"]
                liste_segment.append(base + size)  # Recuperer adresse de fin

            segment_libre = False

            for a in liste_segment:
                if a + segsize > size_mem:  # verif depassement memoire
                    continue

                debut_segment = a

                # Verification intersection :
                chevauchement = False

                for name in segments_table:
                    b = segments_table[name]["base"]
                    s = segments_table[name]["size"]

                    if debut_segment < b + s and b < debut_segment + segsize:
                        chevauchement = True
                        break

                if not chevauchement:
                    segment_libre = True
                    break

            if segment_libre:
                segments_table[segname] = {
                    "base": debut_segment,
                    "size": segsize,
                    "pagesize": pagesize # Ajout
                }
                debug_print()
                print("ok", file = sys.stderr)
            else:
                debug_print()
                print(f"error: not enough memory to create segment {segname} of size {segsize}", file = sys.stderr)

        elif cmd == "DELETE":
            if len(mot) != 2:
                print("Il faut 2 arguments exactement !", file = sys.stderr)
                continue

            segname = mot[1]

            if segname in segments_table:
                del segments_table[segname]
                debug_print()
                print("ok", file = sys.stderr)
            else:
                print(f"error: segment {segname} does not exist", file = sys.stderr)

        elif cmd == "GET":
            if len(mot) != 3:  # Ici, GET garde meme nombre arg mais : GET segname pagenum
                print("error", file = sys.stderr)
                continue

            segname = mot[1]

            try:  # Verif type argument
                pagenum = int(mot[2])
            except:
                print("error", file = sys.stderr)
                continue

            if segname not in segments_table:
                print(f"error: segment {segname} does not exist", file = sys.stderr)
                continue

            base = segments_table[segname]["base"]
            size = segments_table[segname]["size"]
            pagesize = segments_table[segname]["pagesize"]
            num_page = size // pagesize

            if 0 <= pagenum < num_page:
                page_adresse_absolue = base + pagenum * pagesize # parce que pagenum * pagesize c'est le decalage jusqua la page demandée et base c'est juste l'addr abs du debut de seg
                print(f"GET {page_adresse_absolue} {pagesize}")
            else:
                print(f"error: page {pagenum} out of bounds, {segname} size is {num_page} pages", file = sys.stderr)
                continue

        elif cmd == "POST":
            if len(mot) != 4:  # Ex : POST segname pagenum hex -> Nouvelle ecriture
                print("error", file = sys.stderr)
                continue

            segname = mot[1]

            try:
                pagenum = int(mot[2])
                hex = mot[3]
                bytearray.fromhex(hex) # utilisation methode fromhex conseillé 
            except:
                print("error", file = sys.stderr)
                continue

            if segname not in segments_table:
                print(f"error: segment {segname} does not exist", file = sys.stderr)
                continue

            base = segments_table[segname]["base"]
            size = segments_table[segname]["size"]
            pagesize = segments_table[segname]["pagesize"]
            num_page = size // pagesize

            if pagenum < 0 or pagenum >= num_page:
                print(f"error: page {pagenum} out of bounds, {segname} has {num_page} pages", file = sys.stderr) 
                continue

            else:
                page_adresse_absolue = base + pagenum * pagesize
                print(f"POST {page_adresse_absolue} {hex}") 

        else:  # Juste si Instruction pas GET ou POST ou DELETE ou PUT
            print("error", file = sys.stderr)
            continue

    except EOFError:
        break