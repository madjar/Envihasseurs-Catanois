# *-* coding: iso-8859-1 *-*
from plateau import *
from cartes import *

class Colonie:
    '''Suprise totale, cette classe repr�sente les pions de type colonies et ville. Cette classe ne se pr�occupe pas des r�gles du jeu (pas de v�rifications avant de faire les actions).'''

    def __init__(self,j,int):
        '''Pose sur le terrain une colonie du joueur j � l'emplacement int.'''
        self.joueur = j
        self.position = int
        int.colonie = self
        self.isVille = False
        j.colonies.append(self)
        self.deblayeurs = []
        self.deblayeurs24 = []


    def changer_proprietaire(self,j):
        ''' Modifie le propri�taire d'un batiment, si c'est une ville, elle redevient une colonie. Elle perd tous ses d�blayeurs.'''
        if self.isVille:
            self.joueur.villes.remove(self)
        else:
            self.joueur.colonies.remove(self)
        self.joueur = j
        j.colonies.append(self)
        self.deblayeurs = []
        self.deblayeurs24 = []
        self.isVille = False
 
    def evolue(self):
        ''' Transforme la colonie en ville'''
        self.isVille = True
        self.joueur.colonies.remove(self)
        self.joueur.villes.append(self)
    
    def isCotier(self):
        ''' Renvoie vrai si la colonie est au bord de la mer.'''
        return self.position.isCotier()

    def ressources(self):
        ''' Renvoie dans un tableau l'ensemble des ressources au format (num�ro de pastille, ensemble des ressources acquises si ce num�ro tombe, or acquis si ce num�ro tombe).
         Par exemple, si la colonie est entour�e par un hexagone Bois de pastille 4, un Argile de pastille 5 et un Or de pastille 5, la m�thode renverra
         [(4,Cartes.BOIS,0), (5,Cartes.ARGILE,1)]'''
        t = []
        for i in range(10):
           u = self.ressources_from_past(i+3)
           if u != 0:
               t.append((i+3,u[0],u[1]))
        return t

    def ressources_from_past(self,past):
        ''' Renvoie un 2 upplet contenant les ressources et le nombre de p�pites d'or acquies si le nombre past tombe.'''
        t = []
        bois = 0
        argile = 0
        ble = 0
        mouton = 0
        caillou = 0
        aur = 0
        if self.isVille:
            i = 2
        else:
            i = 1
        for h in self.position.hexagones:
            if(h.voleur == 0 and h.past == past):
                if (h.etat == HexaType.BOIS):
                    bois += i
                elif h.etat == HexaType.ARGILE:
                    argile += i
                elif h.etat == HexaType.BLE:
                    ble += i
                elif h.etat == HexaType.OR:
                    aur += i
                elif h.etat == HexaType.CAILLOU:
                    caillou += i
                elif h.etat == HexaType.MOUTON:
                    mouton += i
        if (bois != 0 or argile != 0 or ble != 0 or aur != 0 or caillou != 0 or mouton != 0):
            return (CartesRessources(argile,ble,bois,caillou,mouton),aur)
        else:
            return 0

class Route:
    ''' Tout autant une surprise, cette classe est identifi�e au pion de type route.'''

    def __init__(self,j,a):
        ''' Pose une route appartenant au joueur j sur l'arr�te a.'''
        self.joueur = j
        self.position = a
        a.route = self
        j.routes.append(self)

    def changer_proprietaire(self,j):
        ''' Change le propri�taire de la route en j'''
        self.joueur.routes.remove(self)
        self.joueur = j
        j.routes.append(self)

    def voisins_routables(self,l):
        ''' Renvoie l'ensemble des voisins de la route qui sont aussi des routes du meme joueur, et qui ne sont pas dans l, ou qui ne font pas faire un demi tour (par exemple sur un emplacement dhexagone, on a une �toile � 3 branches, si la derni�re route de l est une de ces branche, que self en est une autre, alors la troisieme branche n'est pas un voisin routable'''
        a = self.position
        j = self.joueur
        ar = []
        for n in a.neighb():
            if(n.route != 0 and n.route.joueur == j):
                i = n.lien(a)
                if (i.colonie == 0 or i.colonie.joueur == j) and not(n.route in l) and (len(l) == 0 or l[len(l)-1].position.lien(n) == 0):
                    ar.append(n.route)
        return ar

   
    def est_extremite(self):
        ''' V�rifie si la route est une extr�mit� du r�seau du joueur.'''
        i1 = self.position.int1 
        i2 = self.position.int2
        if (i1.colonie != 0 and i1.colonie.joueur != self.joueur) or (i2.colonie != 0 and i2.colonie.joueur != self.joueur):
            return True
        ir1 = i1.neighb()
        b = True
        for i in ir1:
            if i2 != i:
                a = i.lien(i1)
                b = b and (a.route == 0 or a.route.joueur != self.joueur)
        if b:
            return True
        b = True
        ir2 = i2.neighb()
        for i in ir2:
            if i1 != i:
                a = i.lien(i2)
                b = b and (a.route == 0 or a.route.joueur != self.joueur)
        return b

    def rlplfr(self):
        ''' Renvoie la route la plus longue qui commence en self.'''
        return self.rlplfrwb([])

    def rlplfrwb(self,beginning):
        ''' Renvoie la route la plus longue commen�ant par beginning, passant par self'''
        beg2 = beginning + [self]
        vr = self.voisins_routables(beginning)
        i = 0
        for r in vr:
            i = max(i,r.rlplfrwb(beg2))
        return i + 1
        

class Bateau:
    ''' Classe identifi�e au pion bateau'''

    class BateauType :
        ''' Ensemble des types de bateau qui existent'''
        VOILIER = 'bateauType_voilier'
        CARGO = 'bateauType_cargo'
        TRANSPORT = 'bateauType_transport'

    def __init__(self,j,a):
        ''' Pose un bateau appartenant au joueur j sur l'arr�te a'''
        self.joueur = j
        self.position = a
        a.bateau = self
        self.cargaison = CartesGeneral(0,0,0,0,0,0,0,0,0,0)
        self.etat = Bateau.BateauType.TRANSPORT
        self.cargaisonMax = 6
        self.vitesse = 1
        self.enEpave = False
        j.bateaux_transport.append(self)
        self.aBouge = False
        self.fouilleurs = []
    
    def evolue(self):
        ''' Transforme ce bateau en Cargo si c'est un bateau de transport, ou en voillier si c'est un cargo.'''
        if(self.etat == Bateau.BateauType.TRANSPORT):
             self.etat = Bateau.BateauType.CARGO
             self.cargaisonMax = 10
             self.joueur.bateaux_transport.remove(self)
             self.joueur.cargo.append(self)
        elif self.etat == Bateau.BateauType.CARGO:
             self.etat = Bateau.BateauType.VOILIER
             self.vitesse = 2
             self.joueur.cargo.remove(self)
             self.joueur.voilier.append(self)

    def append(self,cartes):
        ''' Ajoute les cartes � la cargaison du bateau'''
        if (self.cargaison + cartes).size() <= self.cargaisonMax:
            self.cargaison += cartes

    def remove(self,cartes):
        ''' Retire les cartes de la cargaison'''
        if(cartes <= self.cargaison):
           self.cargaison -= cartes

    def deplacer(self,a):
        ''' Pose ce bateau sur l'arr�te a (sans se soucier de savoir s'il a le droit)'''
        self.position.bateau = 0
        self.position = a
        a.bateau = self

    def peut_recevoir_et_payer(self,cr,cp):
        ''' V�rifie si le bateau peut recevoir les cartes cr et donner (en m�me temps) les cartes cp.'''
        return cp <= self.cargaison and (self.cargaison + cr - cp).size() <= self.cargaisonMax

    def positions_colonisables(self):
        ''' Renvoie toutes les positions terrestres situ�es � deux hexagones d'un bateau sur la cote.'''
        hc = []
        for i in [self.position.int1, self.position.int2]:
            for h in i.hexagones:
                if h.etat != HexaType.MER and not h in hc:
                    hc.append(h)


        hf = hc[:]
        for h in hc:
            for hp in h.neighb():
                if hp.etat != HexaType.MER and not hp in hf:
                    hf.append(hp)

        intf = []
        for h in hf:
            for pos in h.ints:
                if not pos in intf:
                    intf.append(pos)
        return intf

    def en_position_echange(self):
        ''' V�rifie que le bateau est sur un emplacement o� il peut �changer avec une terre : un port ou une colonie coti�re'''
        i1 = self.position.int1
        i2 = self.position.int2
        return  ((i1.colonie != 0 and i1.colonie.joueur == self.joueur) or (i2.colonie != 0 and i2.colonie.joueur == self.joueur) or i1.isPort() or i2.isPort()) and self.position.getTerre() in self.joueur.terres 
    
    def est_proche(self,terre):
        ''' Est vrai si le bateau est � un d�placement d'un emplacement cotier'''
        ints = []
        ints += [self.position.int1,self.position.int2]
        ints += self.position.int1.neighb()
        ints += self.position.int2.neighb()
        if(self.etat == Bateau.BateauType.VOILIER):
            for i in ints[:]:
                ints += i.neighb()
        for i in ints:
            if i.isTerrestreOuCotier():
                return True
        return False

