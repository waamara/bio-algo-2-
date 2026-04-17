"""
=======================================================
 Algorithme Aho-Corasick [AC] - Recherche Multiple de Motifs
=======================================================
 Auteur : Etudiant B
 Module : BioALGO - M1 BioInfo - USTHB 2025-2026
-------------------------------------------------------
 Fonctionnalités :
   - Construction du Trie (automate des préfixes)
   - Fonction de suppléance (failure function)
   - Fonction de sortie (output function)
   - Recherche avec affichage du chemin et des occurrences
   - Tests de performance
=======================================================
"""

import time
from collections import deque


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