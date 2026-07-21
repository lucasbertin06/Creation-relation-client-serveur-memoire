import socket

MAXBYTES = 1024

class RemoteMemory:
    def __init__(self, host, port, segname, size, debug=False, alloc=True, pagesize=16, cachesize=256):
        self.host = host
        self.port = port
        self.segname = segname
        self.size = size
        self.with_debug = debug
        self.alloc = alloc

        # Init cache

        self.pagesize = pagesize
        self.cachesize = cachesize
        self.maxpages = cachesize // pagesize # nb de page d'en le cache
        self.cache = {} # contient donnée d'un byte array et le "bit de saleté"

        if alloc:
            self.request(f"PUT {self.segname} {self.size} {self.pagesize}") # on rajoute self.pagesize

    def __enter__(self):
        return self

    def request(self, request):
        self.debug(f"Creating socket")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug(f"Connecting to remote memory at {self.host}:{self.port}")
        self.socket.connect((self.host, self.port))
        self.debug(f"Connected")
        self.debug(f"Sending request: '{request}'")
        self.socket.sendall(request.encode())

        responses = self.socket.recv(MAXBYTES).decode().strip().splitlines()
        
        for response in responses:
            response = response.strip()
            if response.startswith("[debug]"):
                if self.with_debug:
                    self.debug(f"[from server] {response[8:]}")
                else:
                    continue
            else:
                self.debug(f"Received response: '{response}'")
                self.socket.close()
                if response.startswith("error"):
                    raise ValueError(f"error from remote memory: {response}")
                return response

    def debug(self, message):
        if self.with_debug: # Ajout dans le code sinon tout le temps actif
            print(f"[debug] {message}")

# Le but ici va de, dans le cas ou le cache est plein, supprimer une page au hasard, pour laisser la place a la nouvelle (pas optimal mais aucunes solutions autre que ca trouvées)

    def charge_page(self, page_num) : 
        page_chargee = self.request(f"GET {self.segname} {page_num}")
        self.cache[page_num] = {'data': bytearray.fromhex(page_chargee), 'dirty' : False}

    def enleve_page(self) :
        page_num = next(iter(self.cache)) # je prends une clé du dico de maniere "aléatoire" pour faire de la place si cache complet
        page = self.cache.pop(page_num)
        if page['dirty'] :
            self.request(f"POST {self.segname} {page_num} {page['data'].hex()}")

    def charge_page_absente(self, page_num) : # Pour charger page si abscente et enleve page si cache plein 
        if page_num not in self.cache :
            if len(self.cache) >= self.maxpages :
                self.enleve_page()
            self.charge_page(page_num)

    def __getitem__(self, index):
        page_num = index // self.pagesize
        pos_octet = index % self.pagesize
        self.charge_page_absente(page_num) # charge la page si abscnete du cache
        return self.cache[page_num]['data'][pos_octet]

    def __setitem__(self, index, value):
        page_num = index // self.pagesize
        pos_octet = index % self.pagesize
        self.charge_page_absente(page_num) # pareil que pour getitem
        self.cache[page_num]['data'][pos_octet] = value
        self.cache[page_num]['dirty'] = True # page modifiée mais pas sur serveur

    def __exit__(self, exc_type, exc_value, traceback): 
        if self.alloc :
            self.request(f"DELETE {self.segname}")

    def __len__(self):
        return self.size
    
    def free(self):
        if self.alloc:
            self.request(f"DELETE {self.segname}")