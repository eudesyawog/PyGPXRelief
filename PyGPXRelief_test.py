# -*- coding: utf-8 -*-
"""
NOM  : Bibliothèque PyGPXRelief

ROLE : 
    Fichier Test des différentes fonctions de la bibliothèque :
        
    - Lecture d'un fichier GPX et affichage de quelques caractéristiques sur son contenu (nombre de points, longueur 2D et 3D, altitudes minimale 
      et maximale, dénivelé ascendant, dénivelé descendant, durée et vitesse moyenne)
    
    - Lecture d'un dossier de fichier(s) GPX pour générer une grille Raster d'altitudes en format GeoTiff ou ASCII et l'afficher en 2D 
      et 3D avec possibilité de le sauvegarder en format image JPEG.
      
    - Pour les besoins de ce test, un dossier de traces GPX nommé "traces" se trouve à la racine de ce fichier.
      
AUTEURS  : GBODJO Yawogan Jean Eudes (gyawog@yahoo.fr) && FATOU Sylla (syllakine42@yahoo.fr)
           UT2J/INP-ENSAT Master 2 Geomatique SIGMA
           
VERSION : 0.1 (06/11/2017)
"""

# Import des classes Segment et Relief de la bibliothèque PyGPXRelief
 
from PyGPXRelief import Segment, Relief

# PROCEDURE DE TEST des différentes fonctions de a bibliothèque PyGPXRelief

reponse=input("Entrez 'c' pour lire un fichier GPX et en afficher quelques caracteristiques ou 'r' pour lire un dossier"\
              +"de fichier(s) GPX, generer un MNT et l'afficher en 2D et 3D: ")   

# L'utilisateur choisit d'afficher les caractéristiques d'un fichier GPX     
if reponse=='c':
    reponse=input("Veuillez entrer le chemin d'acces a votre fichier GPX: ")
    inNomFichierGPX=reponse # Récupération du chemin du fichier GPX
    reponse=input("Veuillez entrer le nom de votre trace GPX ou Entrez 'e' pour le nom par defaut Randonnee: ")
    if reponse=='e':
        objetSegment=Segment() # Création d'un objet Segment avec le nom par défaut Randonnee
    else :
        Nom=reponse
        objetSegment=Segment(Nom) # Création d'un objet Segment avec le nom choisi par l'utilisateur
    objetSegment.lire_fichier_GPX(inNomFichierGPX) # Lecture du fichier GPX
    reponse=input("Vous avez le choix entre afficher l'ensemble des caracteristiques (Entrez 'e') ou afficher la caracteristique de "\
                  +"votre choix (Entrez 'c'): ")
    if reponse == 'e': # Afficher l'ensemble des caractéristiques du fichier GPX
        print ("Nom de la trace : {}".format(objetSegment.nom()))
        print ("Nombre de points : {}".format(objetSegment.nbre_points()))
        print ("Longueur 2D : {} km".format(objetSegment.longueur2D()))
        print ("Longueur 3D : {} km".format(objetSegment.longueur3D()))
        print ("Altitude minimale : {} m".format(objetSegment.altMini()))
        print ("Altitude maximale : {} m".format(objetSegment.altMaxi()))
        print (u"Dénivelé ascendant : {} m".format(objetSegment.denivele_ascendant()))
        print (u"Dénivelé descendant : {} m".format(objetSegment.denivele_descendant()))
        print (u"Durée du parcours : {}".format(objetSegment.duree()))
        print ("Vitesse moyenne du parcours : {} km/h".format(objetSegment.vitesse_moyenne()))
    
    elif reponse == 'c': # Afficher une caractéristique au choix
        reponse=input(u"Entrez le numero correspondant a la caracteristique qui vous interesse : '1'pour le nombre de points, "\
                      +u"'2'pour la longueur 2D, '3'pour la longueur 3D, '4'pour l'altitude minimale"\
                      +u"'5'pour l'altitude maximale, '6'pour le denivele ascendant, '7'pour le denivele descendant, "\
                      +u"'8'pour la duree du parcours et '9'pour la vitesse moyenne du parcours:")
        if reponse=='1':
            print ("Nombre de points : {}".format(objetSegment.nbre_points()))
        elif reponse=='2':
            print ("Longueur 2D : {} m".format(objetSegment.longueur2D()))
        elif reponse=='3':
            print ("Longueur 3D : {} m" .format(objetSegment.longueur3D()))
        elif reponse=='4':
            print ("Altitude minimale : {} m" .format(objetSegment.altMini()))
        elif reponse=='5':
            print ("Altitude maximale : {} m" .format(objetSegment.altMaxi()))
        elif reponse=='6':
             print (u"Dénivelé ascendant : {} m" .format(objetSegment.denivele_ascendant()))
        elif reponse=='7':
            print (u"Dénivelé descendant : {} m" .format(objetSegment.denivele_descendant()))
        elif reponse=='8':
            print (u"Durée du parcours : {}" .format(objetSegment.duree()))
        elif reponse=='9':
            print ("Vitesse moyenne du parcours : {}" .format(objetSegment.vitesse_moyenne()))

# L'utilisateur décide de générer MNT et l'afficher en 2D et 3D à partir d'un dossier de fichiers GPX
elif reponse=='r':
    
    # Définitions de quelques variables pour tester le choix de l'utilisateur aux différentes saisies
    Nom=None
    TaillePixel=None
    Method=None
    Format=None
    
    # Récupération des paramètres d'initialisation de la classe Relief
    reponse=input("Quel nom souhaitez vous donner au relief que vous allez generer ? "\
                  +"Entrez ('e') si vous souhaitez laisser le nom par defaut Relief_Randonnee: ")
    if reponse!="e": 
        Nom=reponse # Définition d'un nom pour initialiser la classe Relief
    reponse=input("Quel taille de pixel souhaitez vous donner a la grille qui sera generee ? "\
                  +"Entrez ('e') si vous souhaitez laisser la taille de pixel par defaut 0.001 degres (100 m): ")
    if reponse!="e": # Définition d'une taille de Pixel pour initialiser la classe Relief
        TaillePixel=float(reponse)
    
    # Récupération du chemin du dossier GPX
    reponse=input("Veuillez entrer le chemin d'acces a votre dossier GPX: ")
    inNomDossierGPX=reponse 
    
    # Differents tests pour savoir comment intialiser l'objet Relief
    if not Nom is None :
        if not TaillePixel is None :
            objetRelief=Relief(inNom=Nom,inTaillePixel=TaillePixel) # Création d'un objet Relief
        else:
            objetRelief=Relief(inNom=Nom) # Création d'un objet Relief
    else:
        if not TaillePixel is None :
            objetRelief=Relief(inTaillePixel=TaillePixel) # Création d'un objet Relief
        else:
            objetRelief=Relief() # Création d'un objet Relief
    
    # Lecture du dossier de fichiers GPX
    objetRelief.lire_dossier_GPX(inNomDossierGPX) 
    reponse=input("Tout est pret pour generer votre modele numerique d'elevation. Veuillez indiquer une methode d'interpolation. "\
                  +"Vous avez le choix entre la methode du Plus Proche voisin ('nearest') et la methode d'interpolation lineaire ('linear')"\
                  +" Ou Entrez ('e') pour la methode du plus proche voisin: ")
    
    # Génération de la grille Raster des élévations
    if reponse!="e":
        Method=reponse #Définition de la méthode d'interpolation des altitudes
    
    reponse=input("Dans quel format souhaitez vous generer votre grille raster 'GeoTiff' ou 'ASCII' ? Ou Appuyez sur"\
                  +"Entrez ('e') pour le GeoTiff: ")
    if reponse!="e":
        Format=reponse # Définition du format de sortie de la grille Raster des élévations
        
    # Differents tests pour savoir comment generer la grille Raster
    if not Method is None:
        if not Format is None:
            objetRelief.generer_mnt(inMethod=Method,inFormat=Format)
        else:
            objetRelief.generer_mnt(inMethod=Method)
    else:
        if not Format is None:
            objetRelief.generer_mnt(inFormat=Format)
        else:
            objetRelief.generer_mnt()
    
    reponse=input("Votre grille raster d'elevation a ete genere au format specifie dans le dossier contenant ce fichier "\
                  +"Affichons le a present mais avant souhaiter vous ne pas sauvegarder en image l'affichage de votre grille? "\
                  +"Si tel est le cas entrez 'n' sinon Entrez ('e') : ")
    
    # Affichage du relief en 2D et 3D 
    if reponse=="n":
        inSave=False # Pas de sauvegarde en fichier Image
        objetRelief.afficher_relief(inSave=False)
    elif reponse=="e":
        objetRelief.afficher_relief() # Sauvegarde en fichier Image
        print (u"Votre affichage a bien été sauvegardé dans le dossier contenant ce fichier. A bientôt")