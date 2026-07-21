import os, sys, signal, time

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
            if len(mot) != 3:
                print("error", file=sys.stderr)
                continue

            segname = mot[1]

            try:
                segsize = int(mot[2])
            except:
                print("error", file = sys.stderr)
                continue

            if segname in segments_table:
                print(f"error: segment {segname} already exists", file = sys.stderr)
                continue

            if segsize <= 0:
                print("error", file = sys.stderr)
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

                    if debut_segment < b + s and b < debut_segment + segsize: # addr fin seg existant et addr fin nv seg
                        chevauchement = True
                        break

                if not chevauchement:
                    segment_libre = True
                    break

            if segment_libre:
                segments_table[segname] = {
                    "base": debut_segment,
                    "size": segsize
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
            if len(mot) != 3:  # Ex : GET seg0 10
                print("error", file = sys.stderr)
                continue

            segname = mot[1]

            try:  # Verif type argument
                i = int(mot[2])
            except:
                print("error", file = sys.stderr)
                continue

            if segname not in segments_table:
                print(f"error: segment {segname} does not exist", file = sys.stderr)
                continue

            base = segments_table[segname]["base"]
            size = segments_table[segname]["size"]

            if 0 <= i < size:
                adresse_absolue = base + i
                print(f"GET {adresse_absolue}")
            else:
                print(f"error: index {i} out of bounds, {segname} size is {size}", file = sys.stderr)
                continue

        elif cmd == "POST": # POST seg0 10 76 -> indique que la valeur 76 a été mise à l'adresse absolue 110 dans segment seg0
            if len(mot) != 4:  # Ex : POST seg0 10 76
                print("error", file = sys.stderr)
                continue

            segname = mot[1]

            try:
                i = int(mot[2])
                o = int(mot[3])
            except:
                print("error", file = sys.stderr)
                continue

            if segname not in segments_table:
                print(f"error: segment {segname} does not exist", file = sys.stderr)
                continue

            base = segments_table[segname]["base"]
            size = segments_table[segname]["size"]

            if i < 0 or i >= size:
                print(f"error: index {i} out of bounds, {segname} size is {size}", file = sys.stderr)
                continue

            elif o < 0 or o > 255:
                print(f'error: POST instruction requires a byte as a second argument "{o}" out of byte range (0-255)', file = sys.stderr)
                continue

            else:
                adresse_absolue = base + i
                print(f"POST {adresse_absolue} {o}")

        else:  # Juste si Instruction pas GET ou POST ou DELETE ou PUT
            print("error", file = sys.stderr)
            continue

    except EOFError:
        break