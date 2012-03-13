# -*- coding: utf8 -*-
from plateau import *
from test_joueurs import *
from redis import *

REDIS = redis.StrictRedis()


class TestBateaux(TestJoueur):
   
    def setUp(self):
        super(TestBateaux,self).setUp()
        self.j1 = Joueur(1)
        self.j2 = Joueur(2)
        self.tg = Plateau.getPlateau().ter(1)
        self.td = Plateau.getPlateau().ter(2)

    def test_construire_bateaux(self):

        p = Plateau.getPlateau()
        j1 = self.j1
        j2 = self.j2

        i1 = p.it(32)#
        i2 = p.it(65)#
        i3 = p.it(72)#

        a1 = p.it(12).lien(p.it(2))# Arrete maritime non reliée à la cote
        a2 = p.it(22).lien(p.it(32))# Arrete maritime reliée à une colonie
        a3 = p.it(33).lien(p.it(32))# Arrete cotière reliée à une colonie
        a4 = p.it(65).lien(p.it(66))# Arrete reliée à une colonie adverse
        a5 = p.it(84).lien(p.it(94))# Arrete terrestre
        a6 = p.it(72).lien(p.it(73))# Arrete terrestre reliée à une colonie
        a7 = p.it(35).lien(p.it(45))# Arrete maritime reliée à la terre mais pas a une colonie


        j1.setCartes(self.tg,Tarifs.BATEAU_TRANSPORT)
        self.assertFalse(Jeu.peut_construire_bateau(j1,a1)) # Aucun lien


        Colonie(1,i1).save()
        self.assertTrue(Jeu.peut_construire_bateau(j1,a2)) # ok
        self.assertTrue(Jeu.peut_construire_bateau(j1,a3)) # ok

        Colonie(2,i2).save()
        self.assertFalse(Jeu.peut_construire_bateau(j1,a4)) # relie mais a un adversaire

        Colonie(1,i3).save()
        self.assertFalse(Jeu.peut_construire_bateau(j1,a5)) # terrestre
        self.assertFalse(Jeu.peut_construire_bateau(j1,a6)) # relie mais terrestre
        self.assertFalse(Jeu.peut_construire_bateau(j1,a7)) # a cote de la côte mais pas d'une colonie
        
        j1.setCartes(self.tg,Cartes.RIEN)
        self.assertFalse(Jeu.peut_construire_bateau(j1,a2)) # Pas assez de ressources
        j1.setCartes(self.tg,Tarifs.BATEAU_TRANSPORT)


#        j1.enRuine = True
#        self.assertFalse(Jeu.peut_construire_bateau(j1,a67)) # Joueur en ruine 
#        j1.enRuine = False

        i = len(j1.getBateauxTransport())
        Jeu.construire_bateau(j1,a2)
        self.assertEqual(len(j1.getBateauxTransport()),i+1)
        self.assertEqual(j1.getCartes(self.tg),Cartes.RIEN)

    
    def test_deplacer_bateaux(self):
        
        j1 = self.j1
        j2 = self.j2
        
        p = Plateau.getPlateau()

        a0 = p.it(52).lien(p.it(62))
        a1 = p.it(1).lien(p.it(2))
        a2 = p.it(102).lien(p.it(112))
        a3 = p.it(41).lien(p.it(42))
        a4 = p.it(101).lien(p.it(102))
        a5 = p.it(52).lien(p.it(53))
        a6 = p.it(52).lien(p.it(42))
        a7 = p.it(61).lien(p.it(62))
        a8 = p.it(112).lien(p.it(2))

        b1 = Bateau(1,1,a0, Cartes.RIEN,Bateau.BateauType.TRANSPORT, False)
        b12 = Bateau(2,1,a1, Cartes.RIEN,Bateau.BateauType.TRANSPORT, False)
        b2 = Bateau(3,2,a2, Cartes.RIEN,Bateau.BateauType.TRANSPORT, False)

        b1.save()
        b12.save()
        b2.save()

        self.assertFalse(Jeu.peut_deplacer_bateau(j1,b1,a3)) # Trop loin
        self.assertFalse(Jeu.peut_deplacer_bateau(j1,b2,a4)) # Bateau adverse
        self.assertFalse(Jeu.peut_deplacer_bateau(j1,b1,a5)) # En pleine terre
        self.assertTrue(Jeu.peut_deplacer_bateau(j1,b1,a6)) # ok cotier
        self.assertTrue(Jeu.peut_deplacer_bateau(j1,b1,a7)) # ok
        self.assertFalse(Jeu.peut_deplacer_bateau(j1,b12,a8)) # Pirate
        
        a9 = p.it(56).lien(p.it(57))
        a10 = p.it(27).lien(p.it(37))
        a11 = p.it(57).lien(p.it(67))
        a12 = p.it(67).lien(p.it(77))
        a13 = p.it(37).lien(p.it(47))
        a14 = p.it(47).lien(p.it(57))
        a15 = p.it(57).lien(p.it(67))

        b13 = Bateau(4,1,a9, Cartes.RIEN,Bateau.BateauType.CARGO, False)
        b14 = Bateau(5,1,a10, Cartes.RIEN,Bateau.BateauType.VOILIER, False)
        b13.save()
        b14.save()

        self.assertTrue(Jeu.peut_deplacer_bateau(j1,b13,a11)) # ok
        self.assertFalse(Jeu.peut_deplacer_bateau(j1,b13,a12)) # Trop loin
        self.assertTrue(Jeu.peut_deplacer_bateau(j1,b14,a13)) # ok, déplacement de 1 arrete
        self.assertTrue(Jeu.peut_deplacer_bateau(j1,b14,a14)) # ok, déplacement de  2 arretes
        self.assertFalse(Jeu.peut_deplacer_bateau(j1,b14,a15)) # Trop loin
        
        b15 = Bateau(6,1,a7, Cartes.RIEN,Bateau.BateauType.VOILIER, False)
        b16 = Bateau(6,2,a6, Cartes.RIEN,Bateau.BateauType.CARGO, False)
        b15.save()
        b16.save()
        self.assertTrue(Jeu.peut_deplacer_bateau(j1,b1,a7)) # ok, déplacement sur un emplacement occupé par un autre bateau.
        self.assertTrue(Jeu.peut_deplacer_bateau(j1,b1,a6)) # ok, déplacement sur un emplacement occupé par un autre bateau.

        

#        j1.enRuine = True
#        self.assertFalse(Jeu.peut_deplacer_bateau(j1,a46,a57))
#        # Joueur en ruine
#        j1.enRuine = False
        
        Jeu.deplacer_bateau(j1,b1,a7)
        self.assertFalse(Jeu.peut_deplacer_bateau(j1,b1,a0)) # a deja bouge

        b13 = Bateau.getBateau(1)
        self.assertFalse(Jeu.peut_deplacer_bateau(j1,b13,a0)) # a deja bouge

# test les echanges entre terre et bateau, et les evolutions de bateau
# Ces tests sont faits au même endroit car ces deux évènements sont possibles dans les mêmes conditions

    def test_echanger_evoluer_bateau(self):
        j1 = self.j1
        j2 = self.j2
        tg = self.tg
        j1.addTerre(tg)
        j2.addTerre(tg)
        cartes = CartesGeneral(3,3,3,3,3,1,0,0,1,2)
        j1.setCartes(tg,cartes)
        j2.setCartes(tg,CartesGeneral(5,5,5,5,5,5,5,5,5,5))

        p = Plateau.getPlateau()
        
        i1 = p.it(52)
        i2 = p.it(103)

        a1 = p.it(52).lien(p.it(42))
        a2 = p.it(51).lien(p.it(41))
        a3 = p.it(103).lien(p.it(113))
        a4 = p.it(32).lien(p.it(33))
        a5 = p.it(13).lien(p.it(23))
        a6 = p.it(100).lien(p.it(90))
        a7 = p.it(52).lien(p.it(42))


        c = CartesGeneral(1,2,0,0,1,1,1,0,0,0)
        b1 = Bateau(1,1,a1,c,Bateau.BateauType.TRANSPORT,False)
        b2 = Bateau(2,1,a2,c,Bateau.BateauType.TRANSPORT,False)
        b3 = Bateau(3,1,a3,c,Bateau.BateauType.TRANSPORT,False)
        b4 = Bateau(4,1,a4,c,Bateau.BateauType.TRANSPORT,False)
        b5 = Bateau(5,1,a5,c,Bateau.BateauType.TRANSPORT,False)
        b6 = Bateau(6,1,a6,c,Bateau.BateauType.TRANSPORT,False)
        b7 = Bateau(7,2,a7,c,Bateau.BateauType.TRANSPORT,False)

        b1.save()
        b2.save()
        b3.save()
        b4.save()
        b5.save()
        b6.save()
        b7.save()


        c1 = Colonie(1,i1)
        c2 = Colonie(2,i2)

        c1.save()
        c2.save()
        
        self.assertTrue(Jeu.peut_evoluer_bateau(j1,b1)) # OK touche une colonie
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b2)) # En pleine mer
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b3)) # Colonie ennemie
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b4)) # Relie à la terre mais pas en position echange
        self.assertTrue(Jeu.peut_evoluer_bateau(j1,b5)) # Ok touche un port
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b6)) # Port mais sur une terre non colonisee
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b7)) # Relié à une colonie mais pas un bateau allie
        j1.setCartes(tg,Cartes.RIEN)
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b1)) # Relié a une colonie mais Pas assez ressource
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b5)) # 
        j1.setCartes(tg,cartes) 

        cecht = CartesGeneral(0,0,0,0,0,0,0,0,0,1) 
        cechb = CartesGeneral(0,0,0,0,1,1,0,0,0,0) 
        cechttoomuch1 = CartesGeneral(2,0,0,0,0,0,0,0,0,1) 
        cechttoomuch2 = CartesGeneral(0,0,0,0,0,0,0,1,0,0) 
        cechbtoomuch = CartesGeneral(2,0,0,0,0,0,0,0,0,0) 
        cechtneg = CartesGeneral(0,0,0,0,0,0,0,0,-1,1) 
        cechbneg = CartesGeneral(0,0,0,0,1,1,0,-1,0,0) 
        cechtdouble = CartesGeneral(0,0,0,0,0,0,0,0,0,0.5) 
        cechbdouble = CartesGeneral(0,0,0,0,1,0.5,0,0,0,0) 
        
#        j1.enRuine = True
#        self.assertFalse(Jeu.peut_echanger_bateau(j1,ab1,cecht,cechb))
#        # Joueur en ruine
#        j1.enRuine = False
        
        self.assertTrue(Jeu.peut_echanger_bateau(j1,b1,cecht,cechb)) # OK touche une colonie
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b2,cecht,cechb)) # En pleine mer
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b3,cecht,cechb)) # Colonie ennemie
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b4,cecht,cechb)) # Relie a rien
        self.assertTrue(Jeu.peut_echanger_bateau(j1,b5,cecht,cechb)) # Ok touche un port
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b6,cecht,cechb)) # Port mais sur une terre non colonisee
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b7,cecht,cechb)) # Pas un bateau allie
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechttoomuch1,cechb)) # Trop de ressources demandees, le bateau est plein
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechttoomuch2,cechb)) # Trop de ressources demandees la colonie n'a pas tout ca
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cecht,cechbtoomuch)) # Trop de ressources demandees, le bateau n'a pas tout ca
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechtneg,cechb)) # Echange negatif
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cecht,cechbneg)) # Echange negatif
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechtdouble,cechb)) # Echange non entier
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cecht,cechbdouble)) # Echange non entier


#        j1.enRuine = True
#        self.assertFalse(Jeu.peut_evoluer_bateau(j1,ab1))
#        # Joueur en ruine
#        j1.enRuine = False
        
        j1.setCartes(tg,cartes)
        Jeu.echanger_bateau(j1,b1,cecht,cechb)
        self.assertEqual(j1.getCartes(tg),cartes - cecht + cechb)
        self.assertEqual(b1.cargaison,c + cecht - cechb)
        b8 = Bateau.getBateau(1)
        self.assertEqual(b8.cargaison,c + cecht - cechb)
        j1.recevoir(tg,cecht - cechb)
        b1.append(cechb - cecht)

        j1.setCartes(tg,Tarifs.CARGO)
        Jeu.evoluer_bateau(j1,b1)
        self.assertEqual(j1.getCartes(tg),Cartes.RIEN)
        self.assertEqual(b1.etat, Bateau.BateauType.CARGO)
        b8 = Bateau.getBateau(1)
        self.assertEqual(b8.etat, Bateau.BateauType.CARGO)

        j1.setCartes(tg,cartes)


        b2.evolue()
        b3.evolue()
        b4.evolue()
        b5.evolue()
        b6.evolue()
        b7.evolue()
        
        b1.save()
        b2.save()
        b3.save()
        b4.save()
        b5.save()
        b6.save()
        b7.save()

        self.assertTrue(Jeu.peut_evoluer_bateau(j1,b1)) # OK touche une colonie
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b2)) # En pleine mer
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b3)) # Colonie ennemie
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b4)) # Relie a rien
        self.assertTrue(Jeu.peut_evoluer_bateau(j1,b5)) # Ok touche un port
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b6)) # Port mais sur une terre non colonisee
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b7)) # Pas un bateau allie
        j1.setCartes(tg,Cartes.RIEN)
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b1)) # Pas assez ressource
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b5)) # 
        j1.setCartes(tg,cartes) 

        cecht = CartesGeneral(2,2,0,0,0,0,0,0,0,1) 
        cechb = CartesGeneral(0,0,0,0,1,1,0,0,0,0) 
        cechttoomuch1 = CartesGeneral(2,2,2,2,0,0,0,0,0,1) 
        cechttoomuch2 = CartesGeneral(0,0,0,0,0,0,0,1,0,0) 
        cechbtoomuch = CartesGeneral(2,0,0,0,0,0,0,0,0,0) 
        
#        j1.enRuine = True
#        self.assertFalse(Jeu.peut_echanger_bateau(j1,ab1,cecht,cechb))
#        # Joueur en ruine
#        j1.enRuine = False
        
        self.assertTrue(Jeu.peut_echanger_bateau(j1,b1,cecht,cechb)) # OK touche une colonie
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b2,cecht,cechb)) # En pleine mer
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b3,cecht,cechb)) # Colonie ennemie
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b4,cecht,cechb)) # Relie a rien
        self.assertTrue(Jeu.peut_echanger_bateau(j1,b5,cecht,cechb)) # Ok touche un port
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b6,cecht,cechb)) # Port mais sur une terre non colonisee
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b7,cecht,cechb)) # Pas un bateau allie
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechttoomuch1,cechb)) # Trop de ressources demandees, le bateau est plein
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechttoomuch2,cechb)) # Trop de ressources demandees la colonie n'a pas tout ca
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cecht,cechbtoomuch)) # Trop de ressources demandees, le bateau n'a pas tout ca
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechtneg,cechb)) # Echange negatif
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cecht,cechbneg)) # Echange negatif
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechtdouble,cechb)) # Echange non entier
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cecht,cechbdouble)) # Echange non entier


#        j1.enRuine = True
#        self.assertFalse(Jeu.peut_evoluer_bateau(j1,ab1))
#        # Joueur en ruine
#        j1.enRuine = False
        
        j1.setCartes(tg,cartes)
        Jeu.echanger_bateau(j1,b1,cecht,cechb)
        self.assertEqual(j1.getCartes(tg),cartes - cecht + cechb)
        self.assertEqual(b1.cargaison,c + cecht - cechb)
        b8 = Bateau.getBateau(1)
        self.assertEqual(b8.cargaison,c + cecht - cechb)
        j1.recevoir(tg,cecht - cechb)
        b1.append(cechb - cecht)

        j1.setCartes(tg,Tarifs.VOILIER)
        Jeu.evoluer_bateau(j1,b1)
        self.assertEqual(j1.getCartes(tg),Cartes.RIEN)
        self.assertEqual(b1.etat, Bateau.BateauType.VOILIER)
        b8 = Bateau.getBateau(1)
        self.assertEqual(b8.etat, Bateau.BateauType.VOILIER)
        
        b2.evolue()
        b3.evolue()
        b4.evolue()
        b5.evolue()
        b6.evolue()
        b7.evolue()

        b1.save()
        b2.save()
        b3.save()
        b4.save()
        b5.save()
        b6.save()
        b7.save()
        j1.setCartes(tg,cartes)

        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b1)) # Un voilier ne peut evoluer
        self.assertFalse(Jeu.peut_evoluer_bateau(j1,b5)) # 

        cecht = CartesGeneral(2,2,0,0,0,0,0,0,0,1) 
        cechb = CartesGeneral(0,0,0,0,1,1,0,0,0,0) 
        cechttoomuch1 = CartesGeneral(2,2,2,2,0,0,0,0,0,1) 
        cechttoomuch2 = CartesGeneral(0,0,0,0,0,0,0,1,0,0) 
        cechbtoomuch = CartesGeneral(2,0,0,0,0,0,0,0,0,0) 
        
#        j1.enRuine = True
#        self.assertFalse(Jeu.peut_echanger_bateau(j1,ab1,cecht,cechb))
#        # Joueur en ruine
#        j1.enRuine = False
        
        self.assertTrue(Jeu.peut_echanger_bateau(j1,b1,cecht,cechb)) # OK touche une colonie
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b2,cecht,cechb)) # En pleine mer
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b3,cecht,cechb)) # Colonie ennemie
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b4,cecht,cechb)) # Relie a rien
        self.assertTrue(Jeu.peut_echanger_bateau(j1,b5,cecht,cechb)) # Ok touche un port
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b6,cecht,cechb)) # Port mais sur une terre non colonisee
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b7,cecht,cechb)) # Pas un bateau allie
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechttoomuch1,cechb)) # Trop de ressources demandees, le bateau est plein
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechttoomuch2,cechb)) # Trop de ressources demandees la colonie n'a pas tout ca
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cecht,cechbtoomuch)) # Trop de ressources demandees, le bateau n'a pas tout ca
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechtneg,cechb)) # Echange negatif
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cecht,cechbneg)) # Echange negatif
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cechtdouble,cechb)) # Echange non entier
        self.assertFalse(Jeu.peut_echanger_bateau(j1,b1,cecht,cechbdouble)) # Echange non entier

        j1.setCartes(tg,cartes)
        Jeu.echanger_bateau(j1,b1,cecht,cechb)
        self.assertEqual(j1.getCartes(tg),cartes - cecht + cechb)
        self.assertEqual(b1.cargaison,c + cecht - cechb)
        b8 = Bateau.getBateau(1)
        self.assertEqual(b8.cargaison,c + cecht - cechb)
        j1.recevoir(tg,cecht - cechb)
        b1.append(cechb - cecht)
        

# Les joueurs colonisent d'autres terres

    def teest_coloniser(self):
        j1 = self.j1
        j2 = self.j2
        tg = self.tg
        td = self.td
        j1.terres = [tg]
        j2.terres = [tg,td]
        c = Cartes.RIEN
        j1.mains = [c]
        j1.aur = [0]
        j1.chevalliers = [0]
        j1.routes_les_plus_longues = [0]
        j1.deplacement_voleur = [False]
        j1.points = [0]
        j2.mains = [c,c]
        j2.aur = [0,0]
        j2.chevalliers = [0,0]
        j2.routes_les_plus_longues = [0,0]
        j2.deplacement_voleur = [False,False]
        j2.points = [0,0]
          
        # Colonisation avec un bateau, l'emplacement de la colonie et la partie de la cargaison a transferer
        # Le bateau n'est pas sur une cote
        # Le bateau est pas au joueur
        # La colonie n'est pas sur l'hexagone cotier ou un de ses voisins
        # La terre est deja colonisee
        # La position de la colonie est occupee a 0 ou 1 case pret par une colonie ou ville d'un autre joueur
        # La cargaison n'est pas suffisante
        # La cargaison transferee est plus grande que le reste        
        # Le transfert n'est physiquement pas valide
        # Une fois la colonisation faite, tester les ressources et la cargaison, la nouvelle terre, la nouvelle main et la nouvelle qtt d'or du colon

        i47 = self.it[47] # Point de colonisation
        i60 = self.it[60] # Colonisation trop lointaine
        i57 = self.it[57] # Pour le bateau
        i46 = self.it[46] # Pour le bateau (2)
        ab1 = i47.lien(i57)
        ab12 = i57.lien(i46)
        i48 = self.it[48] # Pour aller plus loin
        i58 = self.it[58] # Pour aller plus loin
        i38 = self.it[38] # Pour mettre une colonie de j2
        i93 = self.it[93] # Bteau du joueur 2
        i104 = self.it[104] # Bateau du joueur 2
        ab2 = i93.lien(i104)
        
        b1 = Bateau(j1,ab1)
        b2 = Bateau(j2,ab2)

        carg1 = CartesRessources(1,1,1,0,1) # Juste assez pour coloniser
        carg2 = CartesGeneral(3,1,3,0,1,1,0,0,1,0) # Juste assez pour coloniser et transferer
        carg3 = CartesRessources(1,1,0,0,1) # Cargaison pas suffisante
        transf1toomuch = Cartes.BLE # Plus de ressource dans le bateau
        transf1neg = Cartes.BLE * -1 # Transfert nefatif
        transf2 = CartesGeneral(1,0,2,0,0,1,0,0,0,0) # Juste assez pour coloniser et transferer
        transf2double = Cartes.BOIS * 0.5 # Transfert non entier

        b1.cargaison = carg1
        self.assertTrue(Jeu.peut_coloniser(j1,ab1,i47,Cartes.RIEN))
        self.assertTrue(Jeu.peut_coloniser(j1,ab1,i48,Cartes.RIEN))
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i60,Cartes.RIEN)) # Trop loin
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i57,Cartes.RIEN)) # Dans l'eau
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i47,transf1toomuch)) # Transfert trop eleve
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i47,transf1neg)) # Transfert negatif
        

        b1.cargaison = carg3
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i47,Cartes.RIEN)) # Pas assez de cargaison
        
        b2.cargaison = carg1
        self.assertFalse(Jeu.peut_coloniser(j1,ab2,i93,Cartes.RIEN)) # Pas le bon bateau

        b1.cargaison = carg2
        self.assertTrue(Jeu.peut_coloniser(j1,ab1,i47,transf2))
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i47,transf2double)) # Transfert non entier

        j1.terres = [tg,td]
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i47,transf2)) # La terre est deja colonisee
        
        j1.terres = [tg]
        c = Colonie(j2,i47)    
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i47,transf2)) # Il y a une colonie a cet emplacement
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i58,transf2)) # Il y a une colonie voisine
        self.assertTrue(Jeu.peut_coloniser(j1,ab1,i48,transf2))
        
        j1.enRuine = True
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i48,transf2))
        # Joueur en ruine
        j1.enRuine = False

        b1.deplacer(ab12)
        self.assertFalse(Jeu.peut_coloniser(j1,ab12,i48,transf2)) # Le bateau n'est pas cotier
        self.assertFalse(Jeu.peut_coloniser(j1,ab1,i48,transf2)) # Pas de bateau
        b1.deplacer(ab1)
        Jeu.coloniser(j1,ab1,i48,transf2)
        

        self.assertNotEqual(j1.getTerreIndex(td),-1)
        self.assertEqual(j1.getCartes(td),transf2)
        self.assertEqual(j1.getOr(td),0)
        self.assertEqual(j1.get_deplacement_voleur(td),False)
        self.assertEqual(j1.get_chevalliers(td),0)
        self.assertEqual(j1.get_route_la_plus_longue(td),0)
        self.assertEqual(j1.getPoints(td),1) 
        self.assertEqual(j1.get_carte_armee_la_plus_grande(td),False) 
        self.assertEqual(j1.get_carte_route_la_plus_longue(td),False) 
        j2.cartes_routes_les_plus_longues = [False,False]
        self.assertEqual(b1.cargaison,carg2 - transf2 - Tarifs.COLONIE )
        self.assertEqual(len(j1.colonies),1)
        self.assertEqual(len(j1.routes),0)

