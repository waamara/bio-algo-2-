import time
from collections import deque
import sys
sys.stdout.reconfigure(encoding='utf-8') # pour afficher les étoiles 

# ─────────────────────────────────────────────
#  NOEUD DU TRIE
# ─────────────────────────────────────────────
class NoeudTrie:
    def __init__(self):
        self.enfants = {}        # transitions : caractere -> noeud
        self.suppléance = None   # lien de suppléance (failure link)
        self.sortie = []         # motifs terminant à ce noeud
        self.id = 0              # identifiant du noeud (pour affichage)


# ─────────────────────────────────────────────
#  CONSTRUCTION DU TRIE
# ─────────────────────────────────────────────
def construire_trie(motifs):
    """
    Construit le Trie à partir de la liste de motifs.
    Retourne la racine du Trie.
    """
    racine = NoeudTrie()
    racine.id = 0
    compteur = [1]  # compteur global d'IDs

    for motif in motifs:
        noeud = racine
        for char in motif:
            if char not in noeud.enfants:
                nouveau = NoeudTrie()
                nouveau.id = compteur[0]
                compteur[0] += 1
                noeud.enfants[char] = nouveau
            noeud = noeud.enfants[char]
        noeud.sortie.append(motif)  # ce noeud est une fin de motif

    return racine


# ─────────────────────────────────────────────
#  AFFICHAGE DU TRIE
# ─────────────────────────────────────────────
def afficher_trie(racine):
    """
    Affiche la structure du Trie (automate des préfixes).
    """
    print("\n" + "="*55)
    print("   AUTOMATE DES PREFIXES (TRIE)")
    print("="*55)
    print(f"{'Noeud':<8} {'Caractere':<12} {'Enfant':<8} {'Sortie'}")
    print("-"*55)

    file = deque([(racine, "root")])
    visites = set()

    while file:
        noeud, label = file.popleft()
        if noeud.id in visites:
            continue
        visites.add(noeud.id)

        sortie_str = str(noeud.sortie) if noeud.sortie else "-"
        if not noeud.enfants:
            print(f"  {noeud.id:<6} {'(feuille)':<12} {'-':<8} {sortie_str}")
        for char, enfant in noeud.enfants.items():
            print(f"  {noeud.id:<6} {char:<12} {enfant.id:<8} {sortie_str if noeud.sortie else '-'}")
            file.append((enfant, char))

    print("="*55)


# ─────────────────────────────────────────────
#  FONCTION DE SUPPLÉANCE (FAILURE FUNCTION)
# ─────────────────────────────────────────────
def construire_suppléance(racine):
    """
    Construit les liens de suppléance par BFS.
    Le lien de suppléance d'un noeud pointe vers le
    plus long suffixe propre qui est aussi un préfixe
    d'un motif.
    """
    file = deque()
    racine.suppléance = racine

    # Niveau 1 : les enfants directs de la racine pointent vers la racine
    for char, enfant in racine.enfants.items():
        enfant.suppléance = racine
        file.append(enfant)

    # BFS pour les niveaux suivants
    while file:
        noeud = file.popleft()
        for char, enfant in noeud.enfants.items():
            # Trouver le lien de suppléance de l'enfant
            sup = noeud.suppléance
            while sup != racine and char not in sup.enfants:
                sup = sup.suppléance
            if char in sup.enfants and sup.enfants[char] != enfant:
                enfant.suppléance = sup.enfants[char]
            else:
                enfant.suppléance = racine
            # Hériter les sorties du lien de suppléance
            enfant.sortie = enfant.sortie + enfant.suppléance.sortie
            file.append(enfant)


# ─────────────────────────────────────────────
#  AFFICHAGE DE LA FONCTION DE SUPPLÉANCE
# ─────────────────────────────────────────────
def afficher_suppléance(racine):
    """
    Affiche la fonction de suppléance de chaque noeud.
    """
    print("\n" + "="*55)
    print("   FONCTION DE SUPPLÉANCE (FAILURE FUNCTION)")
    print("="*55)
    print(f"{'Noeud':<10} {'Suppléance vers'}")
    print("-"*55)

    file = deque([racine])
    visites = set()

    while file:
        noeud = file.popleft()
        if noeud.id in visites:
            continue
        visites.add(noeud.id)
        sup_id = noeud.suppléance.id if noeud.suppléance else "-"
        print(f"  {noeud.id:<10} {sup_id}")
        for enfant in noeud.enfants.values():
            file.append(enfant)

    print("="*55)


# ─────────────────────────────────────────────
#  AFFICHAGE DE LA FONCTION DE SORTIE
# ─────────────────────────────────────────────
def afficher_sortie(racine):
    """
    Affiche la fonction de sortie de chaque noeud.
    """
    print("\n" + "="*55)
    print("   FONCTION DE SORTIE (OUTPUT FUNCTION)")
    print("="*55)
    print(f"{'Noeud':<10} {'Motifs trouvés'}")
    print("-"*55)

    file = deque([racine])
    visites = set()

    while file:
        noeud = file.popleft()
        if noeud.id in visites:
            continue
        visites.add(noeud.id)
        sortie_str = str(noeud.sortie) if noeud.sortie else "-"
        print(f"  {noeud.id:<10} {sortie_str}")
        for enfant in noeud.enfants.values():
            file.append(enfant)

    print("="*55)


# ─────────────────────────────────────────────
#  RECHERCHE AHO-CORASICK
# ─────────────────────────────────────────────
def recherche_aho_corasick(texte, motifs, afficher_chemin=True):
    """
    Recherche toutes les occurrences des motifs dans le texte.
    Retourne : (occurrences, nb_comparaisons, temps_execution)
    """
    # Construction
    racine = construire_trie(motifs)
    construire_suppléance(racine)

    # Affichage des structures
    if afficher_chemin:
        afficher_trie(racine)
        afficher_suppléance(racine)
        afficher_sortie(racine)

    # ── Phase de recherche ──
    occurrences = {}  # motif -> liste de positions
    for m in motifs:
        occurrences[m] = []

    nb_comparaisons = 0
    noeud_courant = racine
    chemin = []  # pour affichage

    debut = time.perf_counter()

    for i, char in enumerate(texte):
        nb_comparaisons += 1

        # Suivre les liens de suppléance si pas de transition
        while noeud_courant != racine and char not in noeud_courant.enfants:
            noeud_courant = noeud_courant.suppléance

        if char in noeud_courant.enfants:
            noeud_courant = noeud_courant.enfants[char]
        else:
            noeud_courant = racine

        chemin.append((i, char, noeud_courant.id))

        # Vérifier les sorties
        for motif in noeud_courant.sortie:
            pos = i - len(motif) + 1
            occurrences[motif].append(pos)

    fin = time.perf_counter()
    temps = fin - debut

    # Affichage du chemin de recherche
    if afficher_chemin:
        print("\n" + "="*55)
        print("   CHEMIN DE RECHERCHE")
        print("="*55)
        print(f"Texte  : \"{texte}\"")
        print(f"Motifs : {motifs}")
        print(f"\n{'Pos':<6} {'Char':<8} {'Noeud':<8} {'Occurrences trouvées'}")
        print("-"*55)
        for (pos, char, nid) in chemin:
            trouvees = []
            for motif in motifs:
                if pos - len(motif) + 1 in occurrences[motif]:
                    trouvees.append(f"{motif}@{pos - len(motif) + 1}")
            trouvees_str = ", ".join(trouvees) if trouvees else ""
            print(f"  {pos:<6} {char:<8} {nid:<8} {trouvees_str}")
        print("="*55)

        print("\n" + "="*55)
        print("   RESULTATS")
        print("="*55)
        for motif, positions in occurrences.items():
            if positions:
                print(f"  Motif \"{motif}\" trouvé aux positions : {positions}")
            else:
                print(f"  Motif \"{motif}\" : non trouvé")
        print(f"\n  Nombre de comparaisons : {nb_comparaisons}")
        print(f"  Temps d'exécution      : {temps*1000:.4f} ms")
        print("="*55)

    return occurrences, nb_comparaisons, temps


# ─────────────────────────────────────────────
#  TESTS DE PERFORMANCE
# ─────────────────────────────────────────────
def tests_performance():
    """
    Tests de performance en faisant varier la taille du texte
    et le nombre de motifs.
    """
    import random
    import string

    print("\n" + "="*65)
    print("   TESTS DE PERFORMANCE - AHO-CORASICK")
    print("="*65)
    print(f"{'Taille Texte':<15} {'Nb Motifs':<12} {'Taille Motifs':<15} {'Comparaisons':<15} {'Temps (ms)'}")
    print("-"*65)

    alphabet = "ACGT"  # alphabet ADN

    configs = [
        (100,   3,  4),
        (500,   5,  4),
        (1000,  5,  5),
        (5000,  8,  5),
        (10000, 10, 6),
        (50000, 10, 6),
    ]

    resultats = []

    for taille_texte, nb_motifs, taille_motif in configs:
        texte = ''.join(random.choices(alphabet, k=taille_texte))
        motifs = [''.join(random.choices(alphabet, k=taille_motif)) for _ in range(nb_motifs)]

        _, nb_comp, temps = recherche_aho_corasick(texte, motifs, afficher_chemin=False)

        print(f"  {taille_texte:<13} {nb_motifs:<12} {taille_motif:<15} {nb_comp:<15} {temps*1000:.4f}")
        resultats.append((taille_texte, nb_motifs, taille_motif, nb_comp, temps*1000))

    print("="*65)
    return resultats


# ─────────────────────────────────────────────
#  PROGRAMME PRINCIPAL
# ─────────────────────────────────────────────
if __name__ == "__main__":

    print("\n" + "★"*55)
    print("   ALGORITHME AHO-CORASICK [AC]")
    print("   Recherche Multiple de Motifs")
    print("★"*55)

    # ── Exemple 1 : ADN ──
    print("\n\n>>> EXEMPLE 1 : Séquence ADN")
    texte1  = "AATCGAATCGAATGCATCGAATGC"
    motifs1 = ["AATCG", "ATCG", "AATG"]
    recherche_aho_corasick(texte1, motifs1)

    # ── Exemple 2 : Texte simple ──
    print("\n\n>>> EXEMPLE 2 : Texte simple")
    texte2  = "AABAACAADAABAABA"
    motifs2 = ["AABA", "AAD", "AAC"]
    recherche_aho_corasick(texte2, motifs2)

    # ── Tests de performance ──
    print("\n\n>>> TESTS DE PERFORMANCE")
    tests_performance()



"""
=======================================================
 Algorithme Wu-Manber [WM] - Recherche Multiple de Motifs
=======================================================
 Auteur : Etudiant B
 Module : BioALGO - M1 BioInfo - USTHB 2025-2026
-------------------------------------------------------
 Fonctionnalites :
   - Description du principe et choix de B
   - Construction des tables SHIFT, HASH, PREFIX
   - Recherche avec affichage detaille
   - Tests de performance et comparaison avec AC
=======================================================
"""
 
import time
from collections import defaultdict
 
 
def construire_tables(motifs, B):
    lmin = min(len(m) for m in motifs)
    default_shift = lmin - B + 1
    SHIFT = {}
 
    for motif in motifs:
        for i in range(lmin - B + 1):
            bloc = motif[i: i + B]
            val = lmin - B - i
            if val < 0:
                val = 0
            old = SHIFT.get(bloc, default_shift)
            SHIFT[bloc] = min(old, val)
 
    HASH = defaultdict(list)
    for motif in motifs:
        suffixe = motif[lmin - B: lmin]
        HASH[suffixe].append(motif)
 
    PREFIX = defaultdict(list)
    for motif in motifs:
        pref = motif[:B]
        PREFIX[pref].append(motif)
 
    return SHIFT, HASH, PREFIX, lmin, default_shift
 
 
def afficher_tables(motifs, B, SHIFT, HASH, PREFIX, lmin, default_shift):
    print("\n" + "="*60)
    print("   PARAMETRES WU-MANBER")
    print("="*60)
    print(f"  Motifs          : {motifs}")
    print(f"  B (taille bloc) : {B}")
    print(f"  lmin            : {lmin}")
    print(f"  Decalage defaut : {default_shift}")
    print("="*60)
 
    print("\n" + "="*60)
    print("   TABLE SHIFT")
    print("="*60)
    print(f"  {'Bloc':<15} {'Valeur SHIFT'}")
    print("-"*60)
    for bloc, val in sorted(SHIFT.items()):
        print(f"  {bloc:<15} {val}")
    print(f"  {'(autres)':<15} {default_shift}  (defaut)")
    print("="*60)
 
    print("\n" + "="*60)
    print("   TABLE HASH (suffixe[lmin-B..lmin-1] -> motifs)")
    print("="*60)
    print(f"  {'Suffixe':<20} {'Motifs associes'}")
    print("-"*60)
    for bloc, mots in HASH.items():
        print(f"  {bloc:<20} {mots}")
    print("="*60)
 
    print("\n" + "="*60)
    print("   TABLE PREFIX (prefixe[0..B-1] -> motifs)")
    print("="*60)
    print(f"  {'Prefixe':<20} {'Motifs associes'}")
    print("-"*60)
    for pref, mots in PREFIX.items():
        print(f"  {pref:<20} {mots}")
    print("="*60)
 
 
def recherche_wu_manber(texte, motifs, B=2, afficher=True):
    n = len(texte)
    lmin = min(len(m) for m in motifs)
    if lmin < B:
        B = lmin
 
    SHIFT, HASH, PREFIX, lmin, default_shift = construire_tables(motifs, B)
 
    if afficher:
        afficher_tables(motifs, B, SHIFT, HASH, PREFIX, lmin, default_shift)
 
    occurrences = {m: [] for m in motifs}
    nb_comparaisons = 0
    pos = lmin - 1
 
    if afficher:
        print("\n" + "="*60)
        print("   PHASE DE RECHERCHE")
        print("="*60)
        print(f"  Texte  : \"{texte}\"")
        print(f"  Motifs : {motifs}")
        print(f"\n  {'Pos':<6} {'Bloc':<10} {'SHIFT':<8} {'Action'}")
        print("-"*60)
 
    debut = time.perf_counter()
 
    while pos < n:
        if pos - B + 1 < 0:
            pos += 1
            continue
 
        bloc = texte[pos - B + 1: pos + 1]
        nb_comparaisons += 1
        shift_val = SHIFT.get(bloc, default_shift)
        action = ""
 
        if shift_val == 0:
            debut_fen = pos - lmin + 1
            if debut_fen >= 0:
                suffixe_ref = texte[debut_fen + lmin - B: debut_fen + lmin]
                candidats = HASH.get(suffixe_ref, [])
                action = f"SHIFT=0, {len(candidats)} candidat(s)"
 
                for motif in candidats:
                    start = debut_fen
                    if start >= 0 and start + len(motif) <= n:
                        nb_comparaisons += len(motif)
                        pref = texte[start: start + B]
                        if pref in PREFIX:
                            if texte[start: start + len(motif)] == motif:
                                if start not in occurrences[motif]:
                                    occurrences[motif].append(start)
                                    action += f" -> \"{motif}\"@{start}"
                                    if afficher:
                                        print(f"  >>> Occurrence de \"{motif}\" a la position {start}")
            else:
                action = "fenetre hors limites"
            pos += 1
        else:
            action = f"Decalage de {shift_val}"
            pos += shift_val
 
        if afficher:
            print(f"  {pos:<6} {bloc:<10} {shift_val:<8} {action}")
 
    fin = time.perf_counter()
    temps = fin - debut
 
    if afficher:
        print("="*60)
        print("\n" + "="*60)
        print("   RESULTATS")
        print("="*60)
        for motif, positions in occurrences.items():
            if positions:
                print(f"  Motif \"{motif}\" trouve aux positions : {sorted(positions)}")
            else:
                print(f"  Motif \"{motif}\" : non trouve")
        print(f"\n  Nombre de comparaisons : {nb_comparaisons}")
        print(f"  Temps d'execution      : {temps*1000:.4f} ms")
        print("="*60)

    return occurrences, nb_comparaisons, temps

def tests_performance_wm():
    import random
    print("\n" + "="*70)
    print("   TESTS DE PERFORMANCE - WU-MANBER")
    print("="*70)
    print(f"  {'Taille Texte':<15} {'Nb Motifs':<12} {'Taille Motifs':<15} {'Comparaisons':<15} {'Temps (ms)'}")
    print("-"*70)
    alphabet = "ACGT"
    configs = [(100,3,4),(500,5,4),(1000,5,5),(5000,8,5),(10000,10,6),(50000,10,6)]
    resultats = []
    for taille_texte, nb_motifs, taille_motif in configs:
        texte  = ''.join(random.choices(alphabet, k=taille_texte))
        motifs = [''.join(random.choices(alphabet, k=taille_motif)) for _ in range(nb_motifs)]
        _, nb_comp, temps = recherche_wu_manber(texte, motifs, B=2, afficher=False)
        print(f"  {taille_texte:<15} {nb_motifs:<12} {taille_motif:<15} {nb_comp:<15} {temps*1000:.4f}")
        resultats.append((taille_texte, nb_motifs, taille_motif, nb_comp, temps*1000))
    print("="*70)
    return resultats
 
 
def comparaison_wm_ac():
    import random
    print("\n" + "="*78)
    print("   COMPARAISON WU-MANBER [WM] vs AHO-CORASICK [AC]")
    print("="*78)
    print(f"  {'Taille Texte':<14} {'Nb Motifs':<11} {'Comp WM':<12} {'Temps WM(ms)':<15} {'Comp AC':<12} {'Temps AC(ms)'}")
    print("-"*78)
    alphabet = "ACGT"
    configs = [(100,3,4),(500,5,4),(1000,5,5),(5000,8,5),(10000,10,6),(50000,10,6)]
    for taille_texte, nb_motifs, taille_motif in configs:
        texte  = ''.join(random.choices(alphabet, k=taille_texte))
        motifs = [''.join(random.choices(alphabet, k=taille_motif)) for _ in range(nb_motifs)]
        _, comp_wm, t_wm = recherche_wu_manber(texte, motifs, B=2, afficher=False)
        _, comp_ac, t_ac = recherche_aho_corasick(texte, motifs, afficher_chemin=False)
        print(f"  {taille_texte:<14} {nb_motifs:<11} {comp_wm:<12} {t_wm*1000:<15.4f} {comp_ac:<12} {t_ac*1000:.4f}")
    print("="*78)
 
 
if __name__ == "__main__":
    print("\n" + "*"*60)
    print("   ALGORITHME WU-MANBER [WM]")
    print("   Recherche Multiple de Motifs")
    print("*"*60)
 
    print("\n\n>>> EXEMPLE 1 : Sequence ADN (B=2)")
    texte1  = "AATCGAATCGAATGCATCGAATGC"
    motifs1 = ["AATCG", "ATCG", "AATG"]
    recherche_wu_manber(texte1, motifs1, B=2)

    print("\n\n>>> EXEMPLE 2 : Texte simple (B=2)")
    texte2  = "AABAACAADAABAABA"
    motifs2 = ["AABA", "AAD", "AAC"]
    recherche_wu_manber(texte2, motifs2, B=2)
 
    print("\n\n>>> TESTS DE PERFORMANCE WU-MANBER")
    tests_performance_wm()
 
    print("\n\n>>> COMPARAISON WM vs AC")
    comparaison_wm_ac()



    """
=======================================================
 Analyse Comparative & Courbes - BioALGO
=======================================================
 Auteur : Etudiant B
 Module : BioALGO - M1 BioInfo - USTHB 2025-2026
-------------------------------------------------------
 Genere les courbes de :
   1. Temps d'execution AC (taille texte variable)
   2. Temps d'execution WM (taille texte variable)
   3. Comparaison AC vs WM (temps)
   4. Comparaison AC vs WM (comparaisons)
   5. Influence du nombre de motifs sur AC
   6. Influence du nombre de motifs sur WM
=======================================================
"""
 
import random
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
 
sys.path.insert(0, '/home/claude')
from aho_corasick import recherche_aho_corasick
from wu_manber import recherche_wu_manber
 
random.seed(42)
alphabet = "ACGT"
 
# ─────────────────────────────────────────────
#  DONNEES DE TEST
# ─────────────────────────────────────────────
tailles_texte = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]
nb_motifs_fixe = 5
taille_motif_fixe = 5
 
# Test 1 : variation taille texte
temps_ac_txt, temps_wm_txt = [], []
comp_ac_txt,  comp_wm_txt  = [], []
 
print("Collecte des donnees (taille texte)...")
for n in tailles_texte:
    texte  = ''.join(random.choices(alphabet, k=n))
    motifs = [''.join(random.choices(alphabet, k=taille_motif_fixe)) for _ in range(nb_motifs_fixe)]
 
    _, c_ac, t_ac = recherche_aho_corasick(texte, motifs, afficher_chemin=False)
    _, c_wm, t_wm = recherche_wu_manber(texte, motifs, B=2, afficher=False)
 
    temps_ac_txt.append(t_ac * 1000)
    temps_wm_txt.append(t_wm * 1000)
    comp_ac_txt.append(c_ac)
    comp_wm_txt.append(c_wm)
    print(f"  n={n:>6} | AC: {t_ac*1000:.4f}ms ({c_ac} comp) | WM: {t_wm*1000:.4f}ms ({c_wm} comp)")
 
# Test 2 : variation nombre de motifs
nb_motifs_list = [2, 5, 8, 10, 15, 20]
taille_texte_fixe = 10000
 
temps_ac_mot, temps_wm_mot = [], []
comp_ac_mot,  comp_wm_mot  = [], []
 
print("\nCollecte des donnees (nb motifs)...")
for k in nb_motifs_list:
    texte  = ''.join(random.choices(alphabet, k=taille_texte_fixe))
    motifs = [''.join(random.choices(alphabet, k=taille_motif_fixe)) for _ in range(k)]
 
    _, c_ac, t_ac = recherche_aho_corasick(texte, motifs, afficher_chemin=False)
    _, c_wm, t_wm = recherche_wu_manber(texte, motifs, B=2, afficher=False)
 
    temps_ac_mot.append(t_ac * 1000)
    temps_wm_mot.append(t_wm * 1000)
    comp_ac_mot.append(c_ac)
    comp_wm_mot.append(c_wm)
    print(f"  k={k:>3} motifs | AC: {t_ac*1000:.4f}ms ({c_ac} comp) | WM: {t_wm*1000:.4f}ms ({c_wm} comp)")
 
 
# ─────────────────────────────────────────────
#  FIGURE 1 : AC vs WM - Taille du texte
# ─────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Analyse Comparative : Aho-Corasick [AC] vs Wu-Manber [WM]",
             fontsize=15, fontweight='bold', y=0.98)
 
colors = {'AC': '#2196F3', 'WM': '#FF5722'}
markers = {'AC': 'o', 'WM': 's'}
 
# ── Graphe 1 : Temps vs Taille texte ──
ax = axes[0, 0]
ax.plot(tailles_texte, temps_ac_txt, color=colors['AC'], marker=markers['AC'],
        linewidth=2, markersize=6, label='Aho-Corasick [AC]')
ax.plot(tailles_texte, temps_wm_txt, color=colors['WM'], marker=markers['WM'],
        linewidth=2, markersize=6, label='Wu-Manber [WM]')
ax.set_title("Temps d'execution vs Taille du texte", fontweight='bold')
ax.set_xlabel("Taille du texte (n)")
ax.set_ylabel("Temps (ms)")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_facecolor('#f9f9f9')
 
# ── Graphe 2 : Comparaisons vs Taille texte ──
ax = axes[0, 1]
ax.plot(tailles_texte, comp_ac_txt, color=colors['AC'], marker=markers['AC'],
        linewidth=2, markersize=6, label='Aho-Corasick [AC]')
ax.plot(tailles_texte, comp_wm_txt, color=colors['WM'], marker=markers['WM'],
        linewidth=2, markersize=6, label='Wu-Manber [WM]')
ax.set_title("Nombre de comparaisons vs Taille du texte", fontweight='bold')
ax.set_xlabel("Taille du texte (n)")
ax.set_ylabel("Nombre de comparaisons")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_facecolor('#f9f9f9')
 
# ── Graphe 3 : Temps vs Nombre de motifs ──
ax = axes[1, 0]
ax.plot(nb_motifs_list, temps_ac_mot, color=colors['AC'], marker=markers['AC'],
        linewidth=2, markersize=6, label='Aho-Corasick [AC]')
ax.plot(nb_motifs_list, temps_wm_mot, color=colors['WM'], marker=markers['WM'],
        linewidth=2, markersize=6, label='Wu-Manber [WM]')
ax.set_title("Temps d'execution vs Nombre de motifs", fontweight='bold')
ax.set_xlabel("Nombre de motifs (k)")
ax.set_ylabel("Temps (ms)")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_facecolor('#f9f9f9')
 
# ── Graphe 4 : Comparaisons vs Nombre de motifs ──
ax = axes[1, 1]
ax.plot(nb_motifs_list, comp_ac_mot, color=colors['AC'], marker=markers['AC'],
        linewidth=2, markersize=6, label='Aho-Corasick [AC]')
ax.plot(nb_motifs_list, comp_wm_mot, color=colors['WM'], marker=markers['WM'],
        linewidth=2, markersize=6, label='Wu-Manber [WM]')
ax.set_title("Nombre de comparaisons vs Nombre de motifs", fontweight='bold')
ax.set_xlabel("Nombre de motifs (k)")
ax.set_ylabel("Nombre de comparaisons")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_facecolor('#f9f9f9')
 
plt.tight_layout()
plt.savefig('/home/claude/courbes_AC_vs_WM.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nCourbe 1 sauvegardee : courbes_AC_vs_WM.png")
 
 
# ─────────────────────────────────────────────
#  FIGURE 2 : AC seul - complexite theorique
# ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Aho-Corasick [AC] - Analyse de la complexite",
             fontsize=14, fontweight='bold')
 
import math
n_vals = tailles_texte
theorique_ac = [n * nb_motifs_fixe * taille_motif_fixe / 1000 for n in n_vals]  # O(n + m*k) normalise
 
ax = axes[0]
ax.plot(n_vals, temps_ac_txt, color='#2196F3', marker='o', linewidth=2,
        markersize=7, label='AC mesure')
ax.set_title("Temps AC (mesure)", fontweight='bold')
ax.set_xlabel("Taille du texte (n)")
ax.set_ylabel("Temps (ms)")
ax.grid(True, alpha=0.3)
ax.set_facecolor('#f9f9f9')
ax.legend()
 
ax = axes[1]
ax.plot(n_vals, comp_ac_txt, color='#2196F3', marker='o', linewidth=2,
        markersize=7, label='AC comparaisons reelles')
ax.plot(n_vals, n_vals, color='#9C27B0', marker='^', linewidth=2,
        markersize=7, linestyle='--', label='O(n) theorique')
ax.set_title("Comparaisons AC vs O(n) theorique", fontweight='bold')
ax.set_xlabel("Taille du texte (n)")
ax.set_ylabel("Nombre de comparaisons")
ax.grid(True, alpha=0.3)
ax.set_facecolor('#f9f9f9')
ax.legend()
 
plt.tight_layout()
plt.savefig('/home/claude/courbes_AC_complexite.png', dpi=150, bbox_inches='tight')
plt.close()
print("Courbe 2 sauvegardee : courbes_AC_complexite.png")
 
 
# ─────────────────────────────────────────────
#  FIGURE 3 : Tableau de donnees visuel
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 5))
ax.axis('off')
 
colonnes = ['Taille Texte', 'Nb Motifs', 'Taille Motif',
            'Comp AC', 'Temps AC (ms)', 'Comp WM', 'Temps WM (ms)']
lignes = []
for i, n in enumerate(tailles_texte):
    lignes.append([
        str(n),
        str(nb_motifs_fixe),
        str(taille_motif_fixe),
        str(comp_ac_txt[i]),
        f"{temps_ac_txt[i]:.4f}",
        str(comp_wm_txt[i]),
        f"{temps_wm_txt[i]:.4f}"
    ])
 
table = ax.table(cellText=lignes, colLabels=colonnes,
                 loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.8)
 
# Colorier l'en-tete
for j in range(len(colonnes)):
    table[0, j].set_facecolor('#1565C0')
    table[0, j].set_text_props(color='white', fontweight='bold')
 
# Colorier les lignes alternees
for i in range(1, len(lignes) + 1):
    for j in range(len(colonnes)):
        if i % 2 == 0:
            table[i, j].set_facecolor('#E3F2FD')
 
ax.set_title("Tableau des resultats : AC vs WM (taille texte variable)",
             fontsize=13, fontweight='bold', pad=20)
 
plt.tight_layout()
plt.savefig('/home/claude/tableau_resultats.png', dpi=150, bbox_inches='tight')
plt.close()
print("Courbe 3 sauvegardee : tableau_resultats.png")
 
print("\nToutes les figures ont ete generees avec succes!")