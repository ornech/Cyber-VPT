import time
import random
from collections import OrderedDict

# Importation de nos briques précédentes
from db_manager import CyberPathDB
from matcher import CyberMatcher

class CyberPathDaemon:
    def __init__(self, max_ram_size=5):
        """
        Initialise le démon.
        max_ram_size : Limite de la RAM (réglée très bas pour voir l'éviction en direct)
        """
        self.max_ram_size = max_ram_size
        self.ram_cache = OrderedDict() # Notre file LRU
        
        print("[DAEMON] Démarrage des services...")
        self.db = CyberPathDB()
        self.matcher = CyberMatcher()
        print(f"[DAEMON] RAM maximale configurée pour {self.max_ram_size} entités actives.\n")

    def simulate_incoming_log(self):
        """Simule l'arrivée d'un vecteur depuis notre Vectorizer."""
        # On simule 3 IPs différentes pour remplir le cache
        ips = ["192.168.1.10", "192.168.1.20", "192.168.1.30", "10.0.0.5", "10.0.0.6", "10.0.0.7"]
        ip = random.choice(ips)
        
        # 1 fois sur 10, on simule une attaque T1059 (notre vecteur expert)
        if random.random() > 0.9:
            vector = [0.8, 0.9, 0.7, 1.0, 0.6] # Vecteur d'attaque (T1059)
            print(f"   [!] LOG SUSPECT REÇU DE {ip}")
        else:
            # Vecteur de trafic normal (bruit de fond)
            vector = [random.uniform(0.1, 0.3), random.uniform(0.1, 0.4), 
                      random.uniform(0.1, 0.5), random.uniform(0.1, 0.3), random.uniform(0.1, 0.2)]
            print(f"   [>] Log normal reçu de {ip}")
            
        return ip, vector

    def process_log(self, ip, vector):
        """Gère le cycle de vie du log : RAM, Analyse, Éviction."""
        
        # 1. GESTION DU LRU (RAM)
        if ip in self.ram_cache:
            # L'IP est connue, on la remonte tout en haut de la pile (récente)
            self.ram_cache.move_to_end(ip)
        
        self.ram_cache[ip] = vector
        
        # 2. VÉRIFICATION DU DÉBORDEMENT DE RAM
        if len(self.ram_cache) > self.max_ram_size:
            # On expulse le plus ancien (last=False supprime le premier élément inséré)
            oldest_ip, oldest_vector = self.ram_cache.popitem(last=False)
            print(f"   [LRU] RAM Pleine ! Éviction de {oldest_ip} vers MariaDB (Old List).")
            
            # Enregistrement en base de données
            uid_bin = self.db.register_entity(oldest_ip)
            self.db.insert_vector(uid_bin, oldest_vector)

        # 3. ANALYSE PRÉDICTIVE 
        # Un seuil à 0.15 signifie que l'alerte ne se déclenche QUE si le vecteur 
        # utilisateur est quasiment un clone (à 85% identique) du vecteur MITRE.
        alerts, _ = self.matcher.predict_attack(vector, threshold=0.15)
        
        if alerts:
            print(f"\n   🚨 ALERTE CRITIQUE SUR {ip} 🚨")
            for alert in alerts:
                print(f"   -> Signature reconnue : {alert['tid']} ({alert['name']}) | Dist: {alert['distance']}")
            print("   --------------------------------------------------\n")

    def run(self):
        """Boucle principale du Démon."""
        try:
            print("=== CYBER-PATH ENGINE RUNNING (Ctrl+C pour stopper) ===")
            while True:
                ip, vector = self.simulate_incoming_log()
                self.process_log(ip, vector)
                
                # On affiche l'état de la RAM pour le côté pédagogique
                active_ips = list(self.ram_cache.keys())
                print(f"   [RAM STATUT] Occupée : {len(active_ips)}/{self.max_ram_size} | Actives : {active_ips}")
                
                time.sleep(1.5) # Pause pour lire le terminal
                
        except KeyboardInterrupt:
            print("\n[DAEMON] Arrêt demandé par l'utilisateur.")
        finally:
            self.db.close()
            print("[DAEMON] Connexion MariaDB fermée proprement. Au revoir.")

if __name__ == "__main__":
    daemon = CyberPathDaemon(max_ram_size=4) # Limite à 4 pour forcer l'éviction rapide
    daemon.run()