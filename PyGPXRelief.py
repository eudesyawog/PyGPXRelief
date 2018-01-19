# -*- coding: utf-8 -*-
"""
NOM  : Bibliothèque PyGPXRelief

ROLE : Modélise une ou plusieurs traces GPX provenant d'un récepteur GPS
       pour en générer le Relief par interpolation : Modèle Numérique de Terrain (MNT) & Affichage 2D et 3D.
       Le MNT généré est présenté au format ASCII ou GeoTiff au choix et les affichages 2D et 3D peuvent être
       sauvagardés en format image (JPEG).
       Possibilité d'afficher certaines caractéristiques d'une trace GPX (Altitude Min Max, Duree et Vitesse moyenne du parcours,
       Nombre de points, Longueur 2D et 3D du parcours)

EMPLOI : Bibliothèque de 3 classes : Point, Segment, Relief
         Classe Point : Définition d'un objet Point par ses caractéristiques Longitude, Latitude, Elevation, Heure de relevé
         Classe Segment : Liste d'objets Points ; Propose les services d'affichage des caractéristiques d'une trace GPX
         Classe Relief : Ensemble de Segments ; Propose les services de génération d'un MNT et d'affichage 3D du relief 
                         à partir d'un dossier de trace(s) GPX
         Voir Fichier Test : PyGPXRelief_test.py à la racine de ce fichier
       
AUTEURS  : GBODJO Yawogan Jean Eudes (gyawog@yahoo.fr) && FATOU Sylla (syllakine42@yahoo.fr)
           UT2J/INP-ENSAT Master 2 Geomatique SIGMA
           
VERSION : 0.1 (06/11/2017)
"""

# Import des librairies utilisées dans la Bibliothèque PyGPXRelief

from math import sqrt, pi, cos
import gpxpy
import glob
import os
import scipy as sp
from scipy.interpolate import griddata
#from osgeo import gdal, osr, gdal_array
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D
import random

# Variables Constantes utilisées

RAYON_TERRE = float(6371000) # rayon moyen de la Terre en mètres

# Définition des differentes classes de la bibliothèque

class Point(object) :
    """
    ROLE : Définir un point avec ses coordonnées géographiques (Longitude, Latitude, Altitude) et son heure de relevé
           Et Calculer les distances 2D et 3D par rapport à un autre point
    ATTRIBUTS : 
        __longitude : float
        __latitude : float
        __elevation :float
        __heure :  str
    SERVICES :
        def __init__(outSelf,inLon,inLat,inAlt,inHeure):
        def __str__(inSelf): #return str
        def __repr__(inSelf): #return str 
        def longitude (inSelf): #return float
        def latitude (inSelf): #return float
        def elevation (inSelf): #return float
        def distance2D (inSelf): #return float
        def distance3D (inSelf): #return float  
    """
    
    def __init__(outSelf,inLon,inLat,inAlt,inHeure):
        """
        Initialisation de la classe Point avec :
        ENTREES : 
            inLon : float #longitude
            inLat : float #latitude
            inAlt : float #elevation
            inHeure : str #heure
        """
        object.__init__(outSelf) # appel du constructeur de la classe Object
        # définition des attributs Longitude, Latitude, Elevation et Heure du Point
        outSelf.__longitude=float(inLon)
        outSelf.__latitude=float(inLat)
        outSelf.__elevation=float(inAlt)
        outSelf.__heure=str(inHeure)
        
    def __str__(inSelf): #return str
        """
        FONCTION renvoyant la chaîne d'affichage standard de la classe Point
        composée de sa Longitude, Latitude, son Elevation et l'Heure de relevé
        """
        return "Longitude : " + str(inSelf.__longitude) + "\n Latitude : " + str(inSelf.__latitude)+\
               "\n Elevation : " + str(inSelf.__elevation)+ "\n Heure de relevé : " + str(inSelf.__heure)
    
    def __repr__(inSelf): #return str 
        
        """
        Représentation interne de la classe Point
        Chaîne pour affichage de débogage
        """
        return str(inSelf.__dict__)
    
    def longitude (inSelf): #return float
        """
        Retourne la longitude du point
        """
        return inSelf.__longitude
    
    def latitude (inSelf): #return float
        """
        Retourne la latitude du point
        """
        return inSelf.__latitude
    
    def elevation (inSelf): #return float
        """
        Retourne l'elevation du point
        """
        return inSelf.__elevation
    
    def heure (inSelf): #return str
        """
        Retourne l'heure de relevé du point 
        """
        return inSelf.__heure
    
    def distance2D (inSelf, inAutrePoint) : #return float
        """
        Calcule la distance 2D entre 2 points
        ENTREE:
            inAutrePoint : Objet de type Point caractérisé par sa Longitude, Latitude, son Elevation et 
                           l'Heure de relevé
        """
        
        lonAutrePoint=inAutrePoint.longitude() #récupération de la longitude du second point
        latAutrePoint=inAutrePoint.latitude() #récupération de la latitude du second point
        
        # Calcul de la distance 2D entre les 2 points 
        # Le rayon d'un méridien est toujours égal au rayon terrestre
        deltaY = (inSelf.__latitude-latAutrePoint)/180*pi*RAYON_TERRE # conversion °=>rd=>mètre
        # Le rayon d'un parallèle dépend de sa latitude (poles=>0, équateur=>maxi)
        latMoyenne = ((inSelf.__latitude+latAutrePoint)/2)/180*pi
        deltaX = (inSelf.__longitude-lonAutrePoint)/180*pi*RAYON_TERRE*cos(latMoyenne)
        # Distance 2D
        dist2D = sqrt(pow(deltaX,2)+pow(deltaY,2))
        
        return dist2D
    
    def distance3D (inSelf, inAutrePoint) : # return float
        """
        Calcule la distance 3D entre 2 points
        ENTREE:
            inAutrePoint : Objet de type Point caractérisé par sa Longitude, Latitude, son Elevation et 
                           l'Heure de relevé
        """
        altAutrePoint=inAutrePoint.elevation() # récupération de l'altitude du second point
        #Ecart d'altitude
        deltaZ = (inSelf.__elevation-altAutrePoint) # Calcul de l'écart d'altitude entre les 2 points
        # Distance 3D
        dist3D=sqrt(pow(inSelf.distance2D(inAutrePoint),2)+pow(deltaZ,2)) # Appel à la fonction distance2D pour le 
                                                      # calcul des écarts aux carrés entre longitudes et latitudes
        return dist3D

class Segment(list):
    """
    ROLE : Définir un segment qui est l'équivalent d'une liste de plusieurs Points.
           Dans la liste, le Point est un tuple (Longitude, Latitude, Elevation, Heure)
    ATTRIBUTS :
        __nom : str
        __longueur2D : float
        __longueur3D : float
        __altMini : float
        __altMaxi : float
        __denivele_ascendant : float
        __denivele_descendant : float
        __duree : float
    SERVICES :
        def __init__(outSelf,inNom='Randonnée')
        def __str__() : str
        def __repr__ : str
        def lire_fichier_GPX(ioSelf,inNomFichierGPX) 
        def ajouter_point(ioSelf, inPoint)
        def nom(inSelf) : str
        def nbre_points(inSelf) : int
        def longueur2D(inSelf) : float
        def longueur3D(inSelf) : float
        def altMini(inSelf) : float
        def altMaxi(inSelf) : float
        def denivele_ascendant(inSelf) : float
        def denivele_descendant(inSelf) : float
        def duree(inSelf) : float
        def vitesse_moyenne(inSelf) : float
    """
    
    def __init__(outSelf,inNom='Randonnée'):
        """
        Initialisation de la Classe Segment avec l'ENTREE inNom (Randonnée par défaut) : nom du segment
        """
        list.__init__(outSelf) # initialisation de la classe list dont hérite la classe Segment
        outSelf.__nom=str(inNom) # ajout d'un attribut pour le Nom du Segment

    def __str__(inSelf): # return str
        """
        FONCTION renvoyant la chaîne d'affichage standard de la Classe Segment
        """
        return "Segment : " + inSelf.__nom
    
    def __repr__(inSelf): # return str
        """
        chaîne d'affichage de débogage
        """
        return str(inSelf.__dict__)
    
    def lire_fichier_GPX(ioSelf,inNomFichierGPX):
        """
        PROCEDURE permettant de lire un fichier GPX à partir de la bibliothèque gpxpy
        et le Chargement des Points (Longitude, Latitude, Elevation, Heure) dans l'objet de type Segment
        
        ENTREE:
            inNomFichierGPX : str # Chemin d'accès au fichier GPX à lire
        """
        gpx_file = open(inNomFichierGPX, 'r') # Ouverture du fichier GPX en mode Lecture 'read'
        gpx = gpxpy.parse(gpx_file) # analyse du fichier GPX et récupération de son contenu dans la variable gpx
        
        # Triple Boucle permettant l'accès aux Tracks puis segments puis points du fichier GPX
        for rangTrack in range(len(gpx.tracks)): # Parcours des Tracks
            for rangSeg in range(len(gpx.tracks[rangTrack].segments)): # Parcours des Segments du Track
                # Pour chaque Track et Segment de ce Track, on récupère la liste des Points
                lstTrackPoints=gpx.tracks[rangTrack].segments[rangSeg].points
                # Et pour chaque point dans cette liste, on ajoute à l'Objet Segment sa Longitude, Latitude,son Elevation 
                # et l'heure de relevé
                for point in lstTrackPoints : # Parcours de la liste des Points pour chaque segment 
                    # Définition d'un objet de type Point qu'on va ajouter à l'objet Segment
                    # Les attributs de l'objet Point défini sont récupérés sur le point du fichier GPX lu
                    objetPoint=Point(point.longitude,point.latitude,point.elevation,point.time.strftime("%H:%M:%S"))# L'Heure est sous forme d'objet Datetime et nécessite une 
                                                    # conversion en str par la méthode strftime de la classe datetime.datetime
                    ioSelf.append(objetPoint) 
        # Gestion du cas des Waypoints
        # Boucle permettant l'accès aux waypoints eventuels contenus dans le fichier GPX
        for rang,waypoint in enumerate(gpx.waypoints): # Parcours de la liste des Waypoints
            # Pour chaque waypoint dans cette liste, on ajoute à l'Objet Segment sa Longitude, Latitude,son Elevation 
            # et l'heure de relevé
            objetPoint=Point(waypoint.longitude,waypoint.latitude,waypoint.elevation,waypoint.time.strftime("%H:%M:%S"))
            ioSelf.append(objetPoint) # L'Heure est sous forme d'objet Datetime et nécessite une 
                                                    # conversion en str par la méthode strftime de la classe datetime.datetime
            
        gpx_file.close() #fermeture du fichier GPX
    
    def ajouter_point(ioSelf,inPoint):
        """
        PROCEDURE permettant d'Ajouter un point à l'objet Segment
        ENTREE:
            inPoint : Objet de type Point caractérisé par sa Longitude, Latitude, son Elevation et 
            l'Heure de relevé
        """
        ioSelf.append(inPoint)
        
    
    def nom(inSelf): # return str
        """
        Retourne le nom de l'objet Segment (par défaut Randonnée)
        """
        return inSelf.__nom
    
    def nbre_points(inSelf): #return int
        """
        Retourne le nombre de points contenus de l'objet Segment (longueur)
        """
        return len(inSelf)
    
    def longueur2D(inSelf): # return float
        """
        Calcul la Somme des distances 2D 2 à 2 entre les points de l'objet Segment 
        """
        inSelf.__longueur2D=0. # initialisation de la variable longueur2D à 0
        # Boucle sur l'objet Segment qui récupère à chaque fois 2 points successifs 
        for rangPoint in range(1,len(inSelf)): # parcours des points de l'objet Segment
            # récupération des attributs du point rangPoint-1 et définition d'un objet Point correspondant
            # indices : 0 Longitude, 1 Latitude, 2 Elevation, 3 Heure
            pointInitial=inSelf[rangPoint-1]
            # récupération des attributs du point suivant (rangPoint) et définition d'un objet Point correspondant
            pointSuivant=inSelf[rangPoint]
            # Calcul de la longueur 2D = ancienne valeur + distance 2D entre 2 objets Points définis
            inSelf.__longueur2D+=pointInitial.distance2D(pointSuivant)
        
        return round(inSelf.__longueur2D*0.001,2) # conversion en km et arrondissement à 2 chiffres après la virgule
    
    def longueur3D(inSelf): # return float
        """
        Calcul la Somme des distances 3D 2 à 2 entre les points de l'objet Segment 
        """
        inSelf.__longueur3D=0. # initialisation de la variable longueur3D à 0
        for rangPoint in range(1,len(inSelf)): # parcours des points de l'objet Segment
            # récupération des attributs du point rangPoint-1 et définition d'un objet Point correspondant
            # indices : 0 Longitude, 1 Latitude, 2 Elevation, 3 Heure
            pointInitial=inSelf[rangPoint-1]
            # récupération des attributs du point suivant (rangPoint) et définition d'un objet Point correspondant
            pointSuivant=inSelf[rangPoint]
            # Calcul de la longueur 3D  = ancienne valeur + distance 3D entre les 2 objets Points définis
            inSelf.__longueur3D+=pointInitial.distance3D(pointSuivant)
        
        return round(inSelf.__longueur3D*0.001,2) # conversion en km et arrondissement à 2 chiffres après la virgule
    
    def altMini(inSelf): # return float
        """
        Retourne l'altitude Minimale de l'Objet Segment
        """
        # indice 2 : Altitude
        inSelf.__altMini=inSelf[0].elevation() # initialisation de l'attribut altMini avec l'altitude du premier point de l'objet Segment
        for rangPoint in range(len(inSelf)): # parcours des points de l'objet Segment
            if inSelf[rangPoint].elevation() < inSelf.__altMini: # recherche d'une valeur d'altitude inférieure à celle de départ
                inSelf.__altMini=inSelf[rangPoint].elevation() # si une valeur inférieure à celle de départ est trouvée on l'affecte à 
                                                      # l'attribut altMini  
        return round(inSelf.__altMini,2)
    
    def altMaxi(inSelf): # return float
        """
        Retourne l'altitude Maximale de l'Objet Segment
        """
        # indice 2 : Altitude
        inSelf.__altMaxi=inSelf[0].elevation() # initialisation de l'attribut altMini avec l'altitude du premier point de l'objet Segment
        for rangPoint in range(len(inSelf)): # parcours des points de l'objet Segment
            if inSelf[rangPoint].elevation()  > inSelf.__altMaxi: # recherche d'une valeur d'altitude supérieure à celle de départ
                inSelf.__altMaxi=inSelf[rangPoint].elevation() # si une valeur supérieure à celle de départ est trouvée on l'affecte à 
                                                      # l'attribut altMaxi      
        return round(inSelf.__altMaxi,2)
    
    def denivele_ascendant(inSelf): # return float
        """
        Calcule le denivelé ascendant (somme des écarts d'altitudes positives)
        """
        inSelf.__denivele_ascendant=0. # initialisation de l'attribut denivele_ascendant à 0
        for rangPoint in range(1,len(inSelf)): # parcours des points de l'objet Segment
            # calcul de la différence d'altitude entre 2 points successifs de l'objet Segment
            # si positive, on l'ajoute à l'ancienne valeur de l'attribut denivele_ascendant
            # indice 2 : Altitude
            if inSelf[rangPoint].elevation() -inSelf[rangPoint-1].elevation()  > 0 : 
                inSelf.__denivele_ascendant+=inSelf[rangPoint].elevation() -inSelf[rangPoint-1].elevation() 
        
        return round(inSelf.__denivele_ascendant,2)
        
    
    def denivele_descendant(inSelf): # return float
        """
        Calcule le denivelé descendant (somme des écarts d'altitudes négatives)
        """
        inSelf.__denivele_descendant=0. # initialisation de l'attribut denivele_descendant à 0
        for rangPoint in range(1,len(inSelf)): # parcours des points de l'objet Segment
            # calcul de la différence d'altitude entre 2 points successifs de l'objet Segment
            # si négative, on l'ajoute à l'ancienne valeur de l'attribut denivele_ascendant
            # indice 2 : Altitude
            if inSelf[rangPoint].elevation() -inSelf[rangPoint-1].elevation()  < 0 :
                inSelf.__denivele_descendant+=inSelf[rangPoint].elevation() -inSelf[rangPoint-1].elevation() 
        
        return round(inSelf.__denivele_descendant,2)
        
    def duree(inSelf): # return str
        """
        Calcule la durée de cheminement d'un segment 
        Heure point final - Heure point initial
        """
        # indice 3 : Heure
        # Heure de debut (Point initial d'indice 0)
        debutRandonnee=_instant_en_secondes(inSelf[0].heure()) # Conversion en secondes avec la fonction  _instant_en_secondes
        # Heure de fin (Point final d'indice -1)
        finRandonnee=_instant_en_secondes(inSelf[-1].heure()) # Conversion en secondes avec la fonction  _instant_en_secondes
        # Calcul de la durée
        inSelf.__duree=finRandonnee-debutRandonnee 
        
        return _instant_en_chaine(inSelf.__duree) # affichage en chaine de caractères heures:minutes:secondes
    
    def vitesse_moyenne(inSelf): # return float
        """
        Calcule la vitesse moyenne du parcours d'un segment
        vitesse_moyenne=distance2D/duree
        """
        return round((inSelf.__longueur2D*0.001)/(inSelf.__duree/3600),2) # vitesse moyenne en km/h (*0.001/3600)
                                                                          # arrondissement à 2 chiffres après virgule

class Relief(object):
    """
    ROLE : Génère un Modèle Numérique de Terrain Raster en format (ASII ou TIF) et 
           Affiche en 2D et 3D le Relief d'une zone géographique par interpolation 
           de points (longitude, latitude, elevation) provenant de traces GPX de cette zone.
    
    ATTRIBUTS :
        __nom : str 
        __taille_pixel : float
        __coordonnees_points : scipy array (Tableau de n lignes et 3 colonnes correspoondant aux longitudes, latitudes et altitudes 
                               des points provenant de traces GPX
        __altitudes_interpolees : scipy array (Tableau des altitudes interpolées)
        __longitudes_croisements : scipy array (Longitudes aux croisements de la grille d'interpolation)
        __latitudes_croisements : scipy array (Latitudes aux croisements de la grille d'interpolation)
    
    SERVICES :
        __init__(outSelf,inNom='Relief_Randonnee',inTaillePixel=0.001) 
        __str__(inSelf) : str
        __repr__(inSelf) : str
        lire_dossier_GPX(outSelf,inNomDossierGPX)
        generer_mnt(outSelf,inMethod,inFormat) 
        afficher_relief(inSelf,inSave)
    
    """
    def __init__(outSelf,inNom='Relief_Randonnee',inTaillePixel=0.001):
        """
        Initialisation de la classe Relief 
        ENTREES : 
            inNom : (par défaut Relief_Randonnée) nom à attribuer à la grille Raster (MNT) à générer et 
                    l'affichage 3D qui sera éventuellement sauvegardée.
            inTaillePixel : Taille des cellules de la grille Raster (MNT) qui sera générée par interpolation. 
                            Par défaut 0.001°(100m)
        """
        object.__init__(outSelf) # Initialisation de la classe object dont hérite la classe Relief
        outSelf.__nom=str(inNom) # Ajout d'un attribut nom pour la Classe Relief
        outSelf.__taille_pixel=float(inTaillePixel)
        
    def __str__(inSelf): # return str
        """
        Chaîne d'affichage standard de la classe Relief
        """
        return inSelf.__nom
    
    def __repr__(inSelf): # return str
        """
        Chaîne d'affichage de débogage
        """
        return str(inSelf.__dict__)
    
    def lire_dossier_GPX(outSelf,inNomDossierGPX):
        """
        PROCEDURE permettant de lire un par un, des fichiers GPX contenus dans un dossier 
        (à partir de la bibliothèque gpxpy) et de charger les points qu'ils contiennent 
        dans l'attribut __coordonnees_points de type tableau (scipy.array)
        
        ENTREE:
            inNomDossierGPX : # str Chemin d'accès à un répertoire contenant un ou plusieurs fichiers GPX
        """ 
        # liste des fichiers GPX contenus dans le dossier d'entrée
        lstFichiers=glob.glob(inNomDossierGPX+'/*gpx')  # Appel à la bibliothèque glob
        # Initialisation de quelques variables de type list
        coord_x=list() # Liste qui va contenir l'ensemble des longitudes des points
        coord_y=list() # Liste qui va contenir l'ensemble des latitudes des points
        coord_z=list() # Liste qui va contenir l'ensemble des altitudes des points
        
        # Boucle parcourant la liste des fichiers GPX
        for fichier in lstFichiers:
            # Pour chaque fichier on définit un objet de type Segment 
            # et on fait appel à sa méthode lire_fichier_GPX
            segment=Segment()
            segment.lire_fichier_GPX(fichier)
            # Puis on stocke les coordonnées (x,y,z) des points contenus dans cet objet dans les listes correspondantes 
            # (coord_x coord_y, coord_z) avec à chaque fois une extension (extend) de leur contenu et non un ajout (append)
            coord_x.extend([point.longitude() for point in segment]) # Boucle interne sur le segment pour récupérer à chaque point sa longitude
            coord_y.extend([point.latitude() for point in segment]) # Boucle interne sur le segment pour récupérer à chaque point sa latitude
            coord_z.extend([point.elevation() for point in segment]) # Boucle interne sur le segment pour récupérer à chaque point son altitude
            
        # Création d'un attribut de type tableau (scipy.array) de type float à 3 colonnes et d'un nombre de lignes équivalent 
        # à longueur des listes de coordonnées
        outSelf.__coordonnees_points=sp.empty((len(coord_x),3),dtype=float)
        # Remplissage du tableau avec les listes
        outSelf.__coordonnees_points[:,0]=coord_x # les longitudes en indice 0
        outSelf.__coordonnees_points[:,1]=coord_y # les latitudes en indice 1
        outSelf.__coordonnees_points[:,2]=coord_z # les altitudes en indice 2
    
    def generer_mnt(ioSelf,inMethod='nearest',inFormat='GeoTiff'):
        """
        PROCEDURE qui permet d'interpoler les altitudes des points stockés dans l'atrribut __coordonnees_points
        pour créer une grille raster en GeoTiff ou ASCII exploitable sous logiciel SIG. Elle fait appel à la méthode 
        griddata de 
        
        ENTREES :
            inMethod = Méthode d'interpolation. Par défaut la méthode du plus proche voisiin ('nearest'); 
                       Autre option l'interpolation linéaire ('linear')
            inFormat = Format de création de la grille raster (MNT). Par défaut du GeoTiff ('GeoTiff'). Autre option ASCII ('ASCII')
        """
        # Création de la grille d'interpolation de données
        # 1-Calcul des coordonnées (longitudes et latitudes) aux croisements de la grille (de pas l'attribut __taille_pixel)
        xi=sp.arange(min(ioSelf.__coordonnees_points[:,0]),max(ioSelf.__coordonnees_points[:,0]),ioSelf.__taille_pixel) # Calcul des longitudes
        yi=sp.arange(min(ioSelf.__coordonnees_points[:,1]),max(ioSelf.__coordonnees_points[:,1]),ioSelf.__taille_pixel) # Calcul des latitudes
        # 2-Création de la grille proprement dite avec les coordonnées correspondantes
        ioSelf.__longitudes_croisements,ioSelf.__latitudes_croisements = sp.meshgrid(xi,yi) # Récupération des coordonnées de la grille en tant qu'attributs de la classe Relief
        
        # Récupération de listes de longitudes (indice 0), latitudes (indice 1) et altitudes (indice 2) requises pour l'interpolation
        x=ioSelf.__coordonnees_points[:,0] # Longitudes
        y=ioSelf.__coordonnees_points[:,1] # Latitudes
        z=ioSelf.__coordonnees_points[:,2] # Altitudes
        
        # Taille de la grille raster en nombre de lignes et colonnes
        nbCol=ioSelf.__longitudes_croisements.shape[1] # nombre de colonnes
        nbLignes=ioSelf.__latitudes_croisements.shape[0] # nombre de lignes

        # Interpolation des altitudes
        grilleInterpolee= griddata((x,y),z,(ioSelf.__longitudes_croisements,ioSelf.__latitudes_croisements),method=inMethod) # création d'un tableau des altitudes interpolées
        
        # Redisposition du tableau des altitudes interpolées qui est créé à l'envers 
        # la 1ère ligne est écrite à la position de la dernière ligne
        ioSelf.__altitudes_interpolees=sp.empty((nbLignes,nbCol)) # création d'un tableau scipy vide de même taille que la grille 
                                                              # interpolée et comme attribut de la classe Relief
        # Boucle qui parcours le tableau de la grille interpolée et réécrit dans le tableau vide créé 
        # les lignes dans leur vraie position (nbignes-1-numligne) #-1 parce que le indices du tableau commençent par 0
        for numLigne in range(nbLignes):
                ioSelf.__altitudes_interpolees[numLigne,:]=grilleInterpolee[nbLignes-1-numLigne,:]                                                                          
        
        # =============================================================================
        #         Création du fichier physique de la grille raster interpolée 
        #                avec le format sélectionné (inFormat)
        # =============================================================================
        
        # Récupération du dossier dans lequel se trouve le fichier python pour y stocker le fichier physique
        dossierCourant=os.getcwd()
        
        # Instructions conditionnelles selon le format (inFormat) choisi
        
        # Instructions pour le format GeoTiff
        if inFormat=='GeoTiff':
            # Définition du nom du fichier GeoTiff à écrire
            nomSortieFichier=os.path.join(dossierCourant,ioSelf.__nom+'.tif') # Le fichier a le même nom que celui donné à la classe Relief
            # Appel à la bibliothèque Gdal pour l'écriture du fichier GeoTiff
            # 1- Appel au Driver GeoTiff de la bibliothèque Gdal
            driver=gdal.GetDriverByName("GTiff") 
            # 2- Récupération du type de donnees du tableau réécrit des altitudes interpolées
            typeDonneesGrille=gdal_array.NumericTypeCodeToGDALTypeCode(ioSelf.__altitudes_interpolees.dtype)  
            # 3- Création de la nouvelle couche GeoTiff avec ses attributs (nom, nbCol, nbLignes, nombre de bandes (1) et type de données)
            dataset=driver.Create(nomSortieFichier,nbCol,nbLignes,1,typeDonneesGrille) 
            # 4- Ajout des informations de transformation géométrique (longitude et Latitude du point Haut Gauche, largeur du pixel orienté E-O et N-S, Paramètres de rotation (0))
            dataset.SetGeoTransform((min(x),ioSelf.__taille_pixel,0,max(y),0,-ioSelf.__taille_pixel)) 
            # 5- Ajout des informations de projection
            # Appel à la bibliothèque osr pour récupérer un SRS définie en l'ocurrence le système WGS84
            wgs84=osr.SpatialReference() 
            wgs84.SetWellKnownGeogCS("WGS84")
            dataset.SetProjection(wgs84.ExportToWkt())
            # 6- Ecriture des altitudes inteprolées dans le fichier GeoTiff créé
            dataset.GetRasterBand(1).WriteArray(ioSelf.__altitudes_interpolees)
            # 7- Fermeture du fichier
            dataset=None
        
        # Instructions pour le format ASCII
        elif inFormat=='ASCII' :
            # Définition du nom du fichier GeoTiff à écrire
            nomSortie=os.path.join(dossierCourant,ioSelf.__nom+'.asc') # Le fichier a le même nom que celui donné à la classe Relief
            # 1- Création du fichier en ériture avec une extenion .asc
            fichASC = open(nomSortie, "w")
            # 2- Définition de l'entête du fichier ASCII
            # Basé sur le type de format ASCII lu par ArcGIS (http://resources.esri.com/help/9.3/arcgisdesktop/com/gp_toolref/spatial_analyst_tools/esri_ascii_raster_format.htm) 
            ASC_ENTETE = 'ncols %s \n' %nbCol \
                        +'nrows %s \n' %nbLignes \
                        +'xllcorner %s \n' %min(x) \
                        +'yllcorner %s \n' %min(y) \
                        +'cellsize %s \n' %ioSelf.__taille_pixel
                        
            # 3- Ecriture de l'entête dans le fichier
            fichASC.write(ASC_ENTETE)
           
            # 4- Ecriture du corps du fichier ASCII
            # Altitudes interpolées séparées par un espace et disposées ligne par ligne
            for numLigne in range(nbLignes): # Parcours des lignes du tableau des altitudes interpolées
                for numCol in range(nbCol): # Parcours des colonnes du tableau des altitudes interpolées
                    valeurAltitude=ioSelf.__altitudes_interpolees[numLigne,numCol] # Récupération de la valeur d'altitude pour une ligne et une colonne donnée
                    # Ecriture de la valeur d'altitude avec un espace dans le fichier ASCII jusqu'à la dernière colonne de la ligne
                    if numCol < nbLignes-1 :
                        fichASC.write(str(valeurAltitude)+" ")
                    # Ecriture de la valeur d'altitude dans le fichier ASCII avec un espace et un saut de ligne s'il s'agit de la 
                    # dernière colonne de la ligne
                    elif numCol == nbLignes-1 :
                        fichASC.write(str(valeurAltitude)+" ")
                        fichASC.write("\n")
            # 5- Fermeture du fichier ASCII
            fichASC.close()
        
    def afficher_relief(inSelf,inSave=True):
        """
        PROCEDURE permettant d'afficher en 2D et 3D avec la bibliothèque Matplotlib la grille raster résultante de l'interpolation 
        des altitudes des points stockés dans l'atrribut __coordonnees_points. 
        
        ENTREE 
            inSave : Variable booléenne. Si sa valeur est True (par défaut) les affichages 2D et 3D de la grille raster sont 
                     sauvegardées en fichiers physiques au format JPEG à la racine de ce fichier.
        """
        
        # Récupération de listes longitudes (indice 0), latitudes (indice 1) et altitudes requises pour les tracés avec Matplotlib
        x=inSelf.__coordonnees_points[:,0] # Longitudes
        y=inSelf.__coordonnees_points[:,1] # Latitudes
        z=inSelf.__coordonnees_points[:,2] # Altitudes
        
        # =============================================================================
        #         Affichage 2D & 3D
        # =============================================================================
        
        # Définition d'une liste de 11 palettes de couleur de Matplotlib 
        # pour le choix de la palette de couleur à attribuer aux affichages 2D et 3D
        lstPalettes=["viridis","gray","magma","BuPu","inferno","GnBu","plasma","winter","RdYlGn","Spectral","cool"]
        numPalette=random.randint(0,10) # Ce numéro aléatoire compris entre 0 et 10 va permettre de changer la palette de couleur 
                                        # à chaque exécution de cette méthode (afficher_relief)
        
        # Changement de la police par défaut (et de sa Taille) des figures avec Maptplotlib
        plt.rcParams["font.family"] = "Arial"
        plt.rcParams["font.size"] = 12
        
        # Création d'une nouvelle figure
        fig=plt.figure() 
        
        # Affichage 2D
        plt.subplot(121) # Création d'une grille de 1 ligne et 2 colonnes; l'affichage 2D sera représentée à la 1ère colonne
        plt.xlabel('Longitudes',fontweight='bold',labelpad=10,fontsize=10) # Personnalisation de l'axe des X (longitudes)     
        plt.ylabel('Latitudes',fontweight='bold',labelpad=10,fontsize=10)  # Personnalisation de l'axe des Y (latitudes)
        plt.title('Affichage 2D de %s'%inSelf.__nom,fontweight='bold',fontsize=10) # Titre du tracé
        plt.xlim(min(x),max(x)) # Définition des limites horizontales du tracé (axe X)
        plt.ylim(min(y),max(y)) # Définition des limites verticales du tracé (axe Y)
        plt.plot(x,y,'k.',markersize=0.8) # Tracé des points de coordonnées (x,y) marqués en noir avec une taille de 0,8
        # Ajout de la grille des altitudes interpolées au tracé des points
        plt.imshow(inSelf.__altitudes_interpolees,extent=(min(x),max(x),min(y),max(y)),cmap=lstPalettes[numPalette])
        plt.colorbar() # Affichage de la palette de couleur utilisée
        
        # Affichage 3D
        affichage3D = fig.add_subplot(122, projection='3d') # laffichage 3D sera représentée à la 2ème colonne de la grille créée
        affichage3D.set_title('Affichage 3D de %s'%inSelf.__nom,fontweight='bold',fontsize=10) # Titre du tracé
        affichage3D.set_xlabel('Longitudes',fontweight='bold',labelpad=10,fontsize=10) # Personnalisation de l'axe des X (longitudes)
        affichage3D.set_ylabel('Latitudes',fontweight='bold',labelpad=10,fontsize=10) # Personnalisation de l'axe des Y (latitudes)
        affichage3D.set_zlabel('Elevations',fontweight='bold',labelpad=10,fontsize=10)# Personnalisation de l'axe des Z (altitudes)
        affichage3D.set_xlim3d(min(x),max(x)) # Définition des limites horizontales du tracé (axe X)
        affichage3D.set_ylim3d(min(y),max(y)) # Définition des limites verticales du tracé (axe Y)
        # Affichage de la grille des altitudes interpolees en 3D
        
            # 1-Redisposition du tableau d'interpolation des altitudes pour s'accorder aux coordonnées de la grille d'interpolation
        nbLignes=inSelf.__altitudes_interpolees.shape[0] # Récupération du nombre de lignes
        nbCol=inSelf.__altitudes_interpolees.shape[1] # Récupération du nombre de colonnes
        grilleInterpolee=sp.empty((nbLignes,nbCol)) # création d'un tableau scipy vide de même taille que la tableau des altitudes inteprolées 
        # Boucle qui parcours le tableau des altitudes interpolées et réécrit dans le tableau vide créé 
        # les lignes à l'envers (nbignes-1-numligne) #-1 parce que le indices du tableau commençent par 0
        for numLigne in range(nbLignes):
                grilleInterpolee[numLigne,:]=inSelf.__altitudes_interpolees[nbLignes-1-numLigne,:] 
        
            # 2-Affichage de la grille des altitudes 3D tel qu'interpolées au départ
        affichage3D.plot_surface(inSelf.__longitudes_croisements,inSelf.__latitudes_croisements,grilleInterpolee, 
                        cmap=lstPalettes[numPalette])
        # Ajout des points de coordonnées (x,y,z) à l'affichage 3D
        affichage3D.scatter(x, y, z, c='k', marker='o',s=0.8)
        
        # Sauvegarde des affichages 2D et 3D en fichier image si le paramètre inSave est True
        if inSave==True:
            # 1- Récupération du dossier dans lequel se trouve le fichier python pour y stocker éventuellement le fichier image
            dossierCourant=os.getcwd()
            # 2- Définition du Nom du fichier image
            nomFigure=os.path.join(dossierCourant,inSelf.__nom+'.jpg')# Le fichier a le même nom que celui donné à la classe Relief
            # 3- Sauvegarde des affichages en fichier image
            plt.savefig(nomFigure,dpi=300)

# Fonctions privées appelées dans la Classe Segment
def _instant_en_secondes (inInstantEnChaine) : # return ...
    """
    ROLE : renvoie le nombre de secondes écoulées entre 0h0'0" et l'instant
           inInstantEnChaine (par exemple 37214.45 pour "10:20:14.45")
    ENTREE inInstantEnChaine : str # instant exprimé sous la forme 10:20:14.45
    """
    # inInstantEnChaine étant une chaine, on veut isoler les parties hh mm seg
		# en utilisant la fonction split vue au td précédent qui isolait des parties sur 
		# la base du caractère ";". Voir ici le caractère à choisir sur "10:20:14.45"
		# split() renvoie une liste des composants isolés
    lstDatas = inInstantEnChaine.split(":") # on isole les 3 informations
	# récupérer heure, minutes et secondes en numérique
    heure=float(lstDatas[0])
    minutes=float(lstDatas[1])
    secondes=float(lstDatas[2])
    #retourner la durée en secondes
    return heure*3600+minutes*60+secondes
    
def _instant_en_chaine (inInstantEnSecondes) : # return ...
    """
    ROLE : renvoie une chaîne correspondant à l'instant spécifié sous la forme
           "10:20:14" (par exemple pour inInstantEnSecondes = 37214)
    ENTREE inInstantEnSecondes : float # durée écoulée depuis 0h0'0"
    NOTA : on arrondit les secondes à l'entier le plus proche
    """
    heure=int(inInstantEnSecondes//3600)
    minutes=int(inInstantEnSecondes%3600)//60
    secondes=int((inInstantEnSecondes%3600)%60)
    return str(heure) +" heure " + str(minutes) +" minutes "+ str(secondes) +" secondes"