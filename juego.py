import pygame
import pygame_gui
import numpy as np
from algoritmos_evaluacion import A_star, distancia_manhattan, distancia_euclidea
import time
import pickle
import pygame_gui
import os
import tkinter as tk
from tkinter import filedialog

# Algunas variables:

# Tamaño de cada cuadricula
grid_size = 20*2
n = 15 # Tamaño del tablero n x n
cadencia_entre_turnos = 0.05 # segundos 

grid_width, grid_height = n * grid_size, n * grid_size
width = grid_width + 300 # Para tener instrucciones / botones / informacion sobre el juego
height = grid_height
botoien_dist = height // 10

# Colores:
WHITE = (238,238,210)
BLACK = (186,202,68)
GRID_COLOR = (200, 200, 200) # Karratuen arteko kolorea eta pantaila atzeko kolorea
TEXT_COLOR = (0,0,0)
BUTTON_COLOR = (200, 200, 200)
GREEN = (0, 255, 0)
RED =(255,0,0)






class PillaPilla:
    """
    Clase para guardar las partidas. Las diferentes partidas se guardarán aquí y 
    """

    def __init__(self,modo_de_juego,funcion_evaluacion,profundidad_minmax,mapa,funcion_evaluacion_2 = None,profundidad_minmax_2 = None,imax = 100,probabilidad_cambio_de_turno = 0.1,hay_poda = True):
        # Constantes durante la ejecucion: 
        self.funcion_evaluacion = funcion_evaluacion # eval de perseguidor (solo influye si es maquina vs maquina)
        self.profundidad_minmax = profundidad_minmax # Profundidad de las ramas en las que se evaluara el juego
        self.mapa = mapa # Tiene que ser un array de NUMPY
        self.n = len(self.mapa)
        self.modo_de_juego = modo_de_juego # Otras opciones: "perseguido", "maquina vs maquina"
        self.imax = imax
        self.distancia_faltante = float("inf")
        self.probabilidad_cambio_de_turno = probabilidad_cambio_de_turno

        self.iteraciones_minmax = 0
        self.poda = hay_poda

        if self.modo_de_juego != "maquina vs maquina":
            self.funcion_evaluacion_2 = self.funcion_evaluacion
        else:
            self.funcion_evaluacion_2 = funcion_evaluacion_2 # eval de perseguido (solo influye si es maquina vs maquina)
            self.profundidad_minmax_2 = profundidad_minmax_2 # profundidad de evaluacion para perseguido (solo influye en maquina vs maquina)


        # Variables durante la ejecucion:
        self.juego_terminado = False
        self.iteracion = 0
        self.iteracion_perseguidor = 0
        self.iteracion_perseguido = 0
        self.posicion_perseguidor = np.array((0,0)) # Tiene que ser un array de NUMPY
        self.posicion_anterior_perseguidor = np.array((0,0))
        self.posicion_perseguido = np.array((self.n - 1, self.n - 1)) # Tiene que ser un array de NUMPY
        self.posicion_anterior_perseguido = np.array((self.n - 1, self.n - 1))
        self.turno = "perseguidor" # Siempre empieza el perseguidor a jugar
        self.tiempo_ejecucion = 0

    def __repr__(self):
        x0,y0 = self.posicion_perseguidor
        x1,y1 = self.posicion_perseguido
        a = self.mapa[x0][y0]
        b = self.mapa[x1][y1]
        self.mapa[x0][y0] = 2
        self.mapa[x1][y1] = 3
        m = self.mapa.copy()
        self.mapa[x0][y0] = a
        self.mapa[x1][y1] = b
        return m.__repr__()

    def es_posible(self,posicion, quien):
        x,y = posicion
        if quien == "perseguidor":
            return 0 <= x < self.n and 0 <= y < self.n and self.mapa[x][y] != 1 and tuple(self.posicion_anterior_perseguidor) != tuple((x,y))
        else:
            return 0 <= x < self.n and 0 <= y < self.n and self.mapa[x][y] != 1 and tuple(self.posicion_anterior_perseguido) != tuple((x,y))

    def minmax(self, turno_perseguidor, profundidad, f_eval,profundidad_max):
        """
        Sirve para mover a la maquina a la siguiente casilla utilizando el algoritmo 
        minmax y la función de evaluación. Tiene como inputs: 
        - Cuál es el turno de la máquina: (turno_perseguidor = True / False)
        - profundidad: nivel de profundidad recursivo en el que estamos
        """
        self.iteraciones_minmax += 1

        if profundidad == 0 or distancia_manhattan(self) == 1:
            return f_eval(self)
        
        elif turno_perseguidor: # turno_perseguidor == nodo min (tiene que atrapar)
            min = float("inf")
            caminos = [(0,1),(0,-1),(1,0),(-1,0)]
            mejor_posicion = self.posicion_perseguidor
            for dx,dy in caminos:
                if self.es_posible(self.posicion_perseguidor + np.array((dx,dy)),"perseguidor"):
                    turno_anterior = self.posicion_perseguidor
                    turno_anterior_doble = self.posicion_anterior_perseguidor

                    self.posicion_perseguidor = self.posicion_perseguidor + np.array((dx,dy))
                    self.posicion_anterior_perseguidor = turno_anterior

                    valor = self.minmax(turno_perseguidor = False, profundidad=profundidad-1,f_eval = f_eval,profundidad_max= profundidad_max)
                    if valor < min:
                        min = valor
                        if profundidad == profundidad_max:
                            mejor_posicion = self.posicion_perseguidor
                    self.posicion_perseguidor = turno_anterior
                    self.posicion_anterior_perseguidor = turno_anterior_doble

            if profundidad == profundidad_max:
                self.posicion_anterior_perseguidor = self.posicion_perseguidor
                self.posicion_perseguidor = mejor_posicion
                self.turno = "perseguido"    
            else:
                return min
            
        elif not turno_perseguidor: # not turno_perseguidor == nodo max (tiene que huir)
            max = float("-inf")
            caminos = [(0,1),(0,-1),(1,0),(-1,0)]
            mejor_posicion = self.posicion_perseguido
            for dx,dy in caminos:
                if self.es_posible(self.posicion_perseguido + np.array((dx,dy)),"perseguido"):
                    turno_anterior = self.posicion_perseguido
                    turno_anterior_doble = self.posicion_anterior_perseguido

                    self.posicion_perseguido = self.posicion_perseguido + np.array((dx,dy))
                    self.posicion_anterior_perseguido = turno_anterior
                    valor = self.minmax(turno_perseguidor = True, profundidad=profundidad-1,f_eval = f_eval,profundidad_max= profundidad_max)
                    if valor > max:
                        max = valor
                        if profundidad == profundidad_max:
                            mejor_posicion = self.posicion_perseguido
                    self.posicion_perseguido = turno_anterior
                    self.posicion_anterior_perseguido = turno_anterior_doble

            if profundidad == profundidad_max: # Movemos al jugador
                self.posicion_anterior_perseguido = self.posicion_perseguido
                self.posicion_perseguido = mejor_posicion
                self.turno = "perseguidor"
            else:
                return max
            
    def minmax_poda_alfabeta(self, turno_perseguidor, profundidad, f_eval,profundidad_max, alfa = float("-inf"),beta = float("inf")):
        """
        Sirve para mover a la maquina a la siguiente casilla utilizando el algoritmo 
        minmax y la función de evaluación. Tiene como inputs: 
        - Cuál es el turno de la máquina: (turno_perseguidor = True / False)
        - profundidad: nivel de profundidad recursivo en el que estamos
        """
        self.iteraciones_minmax += 1
        
        if profundidad == 0 or distancia_manhattan(self) == 1: #tuple(self.posicion_perseguido) == tuple(self.posicion_perseguidor)):
            return f_eval(self)
        
        elif turno_perseguidor: # turno_perseguidor == nodo min (tiene que atrapar)
            caminos = [(0,1),(0,-1),(1,0),(-1,0)]
            mejor_posicion = self.posicion_perseguidor # en caso de no tener caminos posibles se queda quieto
            for dx,dy in caminos:
                if self.es_posible(self.posicion_perseguidor + np.array((dx,dy)),"perseguidor"):
                    turno_anterior = self.posicion_perseguidor
                    turno_anterior_doble = self.posicion_anterior_perseguidor

                    self.posicion_perseguidor = self.posicion_perseguidor + np.array((dx,dy))
                    self.posicion_anterior_perseguidor = turno_anterior

                    valor = self.minmax_poda_alfabeta(turno_perseguidor = False, profundidad=profundidad-1,f_eval = f_eval,profundidad_max= profundidad_max,alfa = alfa, beta = beta)
                    if valor < beta:
                        beta = valor
                        if profundidad == profundidad_max:
                            mejor_posicion = self.posicion_perseguidor
                    self.posicion_perseguidor = turno_anterior # Para continuar iterando
                    self.posicion_anterior_perseguidor = turno_anterior_doble

                    if alfa >= beta:
                        break # Poda la rama
            
            if profundidad == profundidad_max:
                self.posicion_anterior_perseguidor = self.posicion_perseguidor
                self.posicion_perseguidor = mejor_posicion
                self.turno = "perseguido"    
            else:
                return beta
            
        elif not turno_perseguidor: # not turno_perseguidor == nodo max (tiene que huir)
            caminos = [(0,1),(0,-1),(1,0),(-1,0)]
            mejor_posicion = self.posicion_perseguido
            for dx,dy in caminos:
                if self.es_posible(self.posicion_perseguido + np.array((dx,dy)),"perseguido"):
                    turno_anterior = self.posicion_perseguido
                    turno_anterior_doble = self.posicion_anterior_perseguido

                    self.posicion_perseguido = self.posicion_perseguido + np.array((dx,dy))
                    self.posicion_anterior_perseguido = turno_anterior

                    valor = self.minmax_poda_alfabeta(turno_perseguidor = True, profundidad=profundidad-1,f_eval = f_eval,profundidad_max= profundidad_max, alfa = alfa, beta = beta)
                    if valor > alfa:
                        alfa = valor
                        if profundidad == profundidad_max:
                            mejor_posicion = self.posicion_perseguido

                    self.posicion_perseguido = turno_anterior
                    self.posicion_anterior_perseguido = turno_anterior_doble

                    if beta <= alfa:
                        break # Poda la rama
            if profundidad == profundidad_max:
                self.posicion_anterior_perseguido = self.posicion_perseguido
                self.posicion_perseguido = mejor_posicion
                self.turno = "perseguidor"
            else:
                return alfa

    def guardar_info(self):
        """
        Se guardará la informacion sobre la partida jugada
        """
        self.distancia_faltante = A_star(self)
        
    def ha_terminado(self):
        """
        Aqui se comprobará si el juego ha terminado o no en la posición en la que está.
        """
        mov = [(0,1),(0,-1),(1,0),(-1,0), (0,0)]#, (1,1), (-1,-1), (-1,1), (1,-1)]
        if self.iteracion >= self.imax:
            self.juego_terminado = True
            self.guardar_info()
            return None
        for dx,dy in mov:
            if self.es_posible(self.posicion_perseguidor + np.array([dx,dy]),"perseguidor") and tuple(self.posicion_perseguido) == tuple(self.posicion_perseguidor + np.array([dx,dy])):
                self.juego_terminado = True   
                self.guardar_info() 
                return None        

    def cambio_de_turno(self):
        if self.turno == "perseguidor":
            self.turno = "perseguido"
        else:
            self.turno = "perseguidor"

    def siguiente_movimiento(self):
        """
        Aquí se hará el juego. Es decir, se moveran las posiciones de los jugadores en base al turno
        """
        if self.poda:
            funcion = self.minmax_poda_alfabeta
        else:
            funcion = self.minmax

        if not self.juego_terminado:
            self.iteracion += 1
        # Comprobar si ha germinado el juego:
        if not self.juego_terminado:
            if self.modo_de_juego == "perseguidor":
                if self.turno == "perseguidor" and not self.juego_terminado: # Turno del jugador (se gestiona directamente en pygame)
                    pass
                else:
                    time.sleep(cadencia_entre_turnos)
                    funcion(turno_perseguidor = False,profundidad= self.profundidad_minmax,f_eval=self.funcion_evaluacion,profundidad_max= self.profundidad_minmax)
                    self.iteracion_perseguido += 1
                    self.turno = "perseguidor"



            elif self.modo_de_juego == "perseguido":
                if self.turno == "perseguido" and not self.juego_terminado: # Turno del jugador (se gestiona directamente en pygame)
                    pass
                else:
                    time.sleep(cadencia_entre_turnos)
                    funcion(turno_perseguidor = True,profundidad= self.profundidad_minmax,f_eval=self.funcion_evaluacion,profundidad_max=self.profundidad_minmax)
                    self.iteracion_perseguidor += 1
                    self.turno = "perseguido"



            elif self.modo_de_juego == "maquina vs maquina":
                if self.turno == "perseguido": 
                    time.sleep(cadencia_entre_turnos)
                    # funcion_evaluacion2 es para el perseguido
                    funcion(turno_perseguidor = False,profundidad= self.profundidad_minmax_2,f_eval=self.funcion_evaluacion_2,profundidad_max=self.profundidad_minmax_2) 
                    self.iteracion_perseguido += 1
                    self.turno = "perseguidor"
                else:
                    time.sleep(cadencia_entre_turnos)
                    # funcion_evaluacion es para el perseguidor
                    funcion(turno_perseguidor = True,profundidad= self.profundidad_minmax,f_eval=self.funcion_evaluacion,profundidad_max=self.profundidad_minmax)
                    self.iteracion_perseguidor += 1
                    self.turno = "perseguido"

            # Cambiar aleatoriamente de turno:
            if np.random.binomial(1,self.probabilidad_cambio_de_turno):
                self.turno = "perseguidor"
            self.ha_terminado()
    
    def ejecutar_partida(self):
        """
        Esta funcion esta pensada para jugar maquina contra maquina, a la hora de comparar diferentes algoritmos y profundidades
        """
        t0 = time.time()
        while not self.juego_terminado:
            self.siguiente_movimiento()
        t1 = time.time()
        self.tiempo_ejecucion = t1-t0
        
            




class Botoia:
    def __init__(self, x, y, width, height, color, text, font_size = 24):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, font_size)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

def dibujar_cuadricula(pilla_pilla,screen):
    screen.fill(WHITE)
    for i in range(pilla_pilla.n):
        for j in range(pilla_pilla.n):
            if (i,j) != tuple(pilla_pilla.posicion_perseguidor) and (i,j) != tuple(pilla_pilla.posicion_perseguido): 
                balioa = pilla_pilla.mapa[i][j]
                if balioa == 0: # 0 será que la cuadrícula está vacía
                    pygame.draw.rect(screen, WHITE, (j * grid_size, i * grid_size, grid_size, grid_size))
                elif balioa == 1:
                    pygame.draw.rect(screen, BLACK, (j * grid_size, i * grid_size, grid_size, grid_size))
                pygame.draw.rect(screen, GRID_COLOR, (j * grid_size, i * grid_size, grid_size, grid_size), 1)
            
    (i,j) = pilla_pilla.posicion_perseguidor # Perseguidor de color ROJO
    pygame.draw.rect(screen, RED, (j * grid_size, i * grid_size, grid_size, grid_size))
    pygame.draw.rect(screen, GRID_COLOR, (j * grid_size, i * grid_size, grid_size, grid_size), 1)

    (i,j) = pilla_pilla.posicion_perseguido # Perseguido de color VERDE
    pygame.draw.rect(screen, GREEN, (j * grid_size, i * grid_size, grid_size, grid_size))
    pygame.draw.rect(screen, GRID_COLOR, (j * grid_size, i * grid_size, grid_size, grid_size), 1)
                
def menu():
    # Pygame hasi
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pilla-Pilla")

    # Irudiak:
    irudia = pygame.image.load("imagen_menu.png") 
    irudia = pygame.transform.scale(irudia, (botoien_dist * 4, botoien_dist*4))
    irudia_rect = irudia.get_rect()
    irudia_rect.center = (width // 2, height // 2 - botoien_dist* 1.5)

    # Beharrezko aldagaia
    running = True

    # Textuak idazteko beharrezkoa:
    izenburua = pygame.font.Font(None, 80)

    # Botoia:
    botoia_mapa_sortu = Botoia(width//2-350//2, height - 50 - botoien_dist * 3, 350, 40, BUTTON_COLOR, "Crear mapa del juego")
    botoia_partida_kargatu = Botoia(width//2-350//2, height - 50 - 2*botoien_dist , 350, 40, BUTTON_COLOR, "Jugar")
    botoia_irten = Botoia(width//2-350//2, height - 50, 350, 40, BUTTON_COLOR, "Salir del juego")
    botoia_ajustes = Botoia(width//2-350//2, height - 50 - botoien_dist , 350, 40, BUTTON_COLOR, "Ajustes del juego")

    # Loop orokorra
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Exekutatzeaz bukatzeko
                running = False
                zer_egin = "terminar"
            elif event.type == pygame.MOUSEBUTTONDOWN: # Xaguaren botoiren bat sakatzen bada
                if event.button == 1: # Ezkerreko botoia sakatzen bada
                    if botoia_mapa_sortu.rect.collidepoint(event.pos):
                        running = False
                        zer_egin = "crear mapa"
                    elif botoia_irten.rect.collidepoint(event.pos):
                        running = False
                        zer_egin = "terminar"
                    elif botoia_partida_kargatu.rect.collidepoint(event.pos):
                        running = False
                        zer_egin = "juego"
                    elif botoia_ajustes.rect.collidepoint(event.pos):
                        running = False
                        zer_egin = "ajustes"

        # while buklearen amaieran, pantaila marraztu, textua idatzi eta aktualizatzeko
        screen.fill(WHITE)
        screen.blit(izenburua.render("Pilla - Pilla", True, BLACK),(width//2 - 145, 15))
        botoia_mapa_sortu.draw(screen)
        botoia_irten.draw(screen)
        botoia_ajustes.draw(screen)
        botoia_partida_kargatu.draw(screen)
        screen.blit(irudia, irudia_rect)
        pygame.display.flip()

    return zer_egin

def dibujar_mapa(kuadrikula,screen):
    """
    grid = 28 x 28 tamainiako matrize bat: matrizearen elementuak 0 - 255 tarteko zenbakiak
    izango dira, 28 x 28 pixeleko pantaila baten gris-eskalak izanik
    """
    screen.fill(WHITE)
    n = len(kuadrikula)
    for i in range(n):
        for j in range(n):
            balioa = kuadrikula[i][j]
            if balioa == 1:
                pygame.draw.rect(screen, BLACK, (j * grid_size, i * grid_size, grid_size, grid_size))
                pygame.draw.rect(screen, GRID_COLOR, (j * grid_size, i * grid_size, grid_size, grid_size), 1)
            elif balioa == 0:   
                pygame.draw.rect(screen, WHITE, (j * grid_size, i * grid_size, grid_size, grid_size))
                pygame.draw.rect(screen, GRID_COLOR, (j * grid_size, i * grid_size, grid_size, grid_size), 1)
                
    pygame.draw.rect(screen, RED, (0 * grid_size, 0 * grid_size, grid_size, grid_size))
    pygame.draw.rect(screen, GRID_COLOR, (0 * grid_size, 0 * grid_size, grid_size, grid_size), 1)   

    pygame.draw.rect(screen, GREEN, ((n-1) * grid_size, (n-1) * grid_size, grid_size, grid_size))
    pygame.draw.rect(screen, GRID_COLOR, ((n-1) * grid_size, (n-1) * grid_size, grid_size, grid_size), 1)   
            # karratuaren zenbat betetzen den definitzeko, 0 da "default" balioa eta karratu osoa betetzen du.

def es_mapa_posible(mapa):
    try:
        p = PillaPilla("perseguidor", A_star,5,mapa = mapa)
        A_star(p)
        return True
    except:
        print("No es un mapa correcto!")
        return False

def crear_mapa():
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Pilla-Pilla")

    running = True
    marrazten = False
    garbitzen = False
    mapa_incorrecto = False
    mapa = np.zeros((n,n),dtype=int)
    mapa[0,0] = 3
    mapa[n-1,n-1] = 4

    font = pygame.font.Font(None, 32)
    izenburua = pygame.font.Font(None, 40)
    informazioa = pygame.font.Font(None,30)

    boton_limpiar_cuadricula = Botoia(width - 230, 325, 170, 40, BUTTON_COLOR, "Limpiar cuadricula")
    boton_volver_al_menu = Botoia(width - 230, height - 50, 170, 40, BUTTON_COLOR, "Menu")
    boton_guardar_mapa = Botoia(width - 230, 325 + botoien_dist, 170, 40, BUTTON_COLOR, "Guardar mapa")
    boton_abrir_archivo = Botoia(width - 230, 325 + 2 * botoien_dist, 170, 40, BUTTON_COLOR, "Abrir mapa")

    # Artxiboaren izena idazteko:
    input_rect = pygame.Rect(width - 290, 200, 230, 32)
    text = ''

    while running:
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                running = False
                zer_egin = "terminar"
            elif keys[pygame.K_RETURN]:
                mapa = np.zeros((n,n),dtype=int)
                mapa[0,0] = 3
                mapa[n-1,n-1] = 4
            elif keys[pygame.K_BACKSPACE]:
                text = text[:-1]
            elif event.type == pygame.KEYDOWN:
                text += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # click izquierdo
                    if boton_volver_al_menu.rect.collidepoint(event.pos):
                        zer_egin = "menu"
                        running = False
                    elif boton_limpiar_cuadricula.rect.collidepoint(event.pos):
                        mapa = np.zeros((n,n),dtype=int)
                        mapa[0,0] = 3
                        mapa[n-1,n-1] = 4
                    elif boton_guardar_mapa.rect.collidepoint(event.pos):
                        if es_mapa_posible(mapa) and text.strip() != "":
                            mapa[0,0]= 0
                            mapa[n-1,n-1] = 0
                            pickle.dump(mapa,open(text+".pkl","wb"))
                            mapa_incorrecto = False
                            running = False
                            zer_egin = "menu"
                        else:
                            mapa_incorrecto = True
                    elif boton_abrir_archivo.rect.collidepoint(event.pos):
                        root = tk.Tk()
                        root.withdraw()
                        try:
                            direkt = filedialog.askopenfilename()
                            mapa = pickle.load(open(direkt,"rb"))
                        except:
                            pass

                    marrazten = True
                    x,y = event.pos
                    zutabea = x // grid_size
                    errenkada = y // grid_size
                    if not tuple((errenkada,zutabea)) == (0,0) and not tuple((errenkada,zutabea)) == (n-1,n-1) and 0 <= errenkada < n and 0 <= zutabea < n:
                        mapa[errenkada,zutabea] = 1
                elif event.button == 3:
                    garbitzen = True
                    x,y = event.pos
                    zutabea = x // grid_size
                    errenkada = y // grid_size
                    if not tuple((errenkada,zutabea)) == (0,0) and not tuple((errenkada,zutabea)) == (n-1,n-1) and 0 <= errenkada < n and 0 <= zutabea < n:
                        mapa[errenkada,zutabea] = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    marrazten = False
                elif event.button == 3:
                    garbitzen = False
            elif event.type == pygame.MOUSEMOTION: # Xagua mugitzen bada
                if marrazten:
                    x,y = event.pos
                    zutabea = x // grid_size
                    errenkada = y // grid_size
                    if not tuple((errenkada,zutabea)) == (0,0) and not tuple((errenkada,zutabea)) == (n-1,n-1) and 0 <= errenkada < n and 0 <= zutabea < n:
                        mapa[errenkada,zutabea] = 1
                elif garbitzen:
                    x,y = event.pos
                    zutabea = x // grid_size
                    errenkada = y // grid_size
                    if not tuple((errenkada,zutabea)) == (0,0) and not tuple((errenkada,zutabea)) == (n-1,n-1) and 0 <= errenkada < n and 0 <= zutabea < n :
                        mapa[errenkada,zutabea] = 0
        dibujar_mapa(mapa,screen)

        # texto:
        pygame.draw.rect(screen, BLACK, input_rect, 2)
        text_surface = font.render(text, True, (0,0,0))
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        # Informacion:
        screen.blit(izenburua.render("Dibuja un mapa", True, TEXT_COLOR),(width-295,30))
        screen.blit(informazioa.render("Escribe el nombre del mapa", True, TEXT_COLOR),(width-295,180))
        screen.blit(informazioa.render(".pkl", True, TEXT_COLOR),(width-230 + 180,212))
        if mapa_incorrecto:
            screen.blit(informazioa.render("Mapa incorrecto!", True, RED),(width-295,250))

        

        boton_guardar_mapa.draw(screen)
        boton_limpiar_cuadricula.draw(screen)
        boton_volver_al_menu.draw(screen)
        boton_abrir_archivo.draw(screen)
        
        pygame.display.flip()

    return zer_egin

def juego(pilla_pilla):
    """
    Aquí se visualiza y ejecuta el juego
    """
    # Pygame hasi
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Jugando")

    # Beharrezko hainbat aldagai
    running = True

    # Textuak idazteko beharrezkoa:
    izenburua = pygame.font.Font(None, 40)
    info_turno = pygame.font.Font(None, 30)

    # Botoia:
    botoia_itzuli_menura = Botoia(width - 230, height - 50, 170, 40, BUTTON_COLOR, "Menu")

    boton_arriba = Botoia(grid_width + (width - grid_width) // 2 - 60 // 2, height - 4 * botoien_dist, 60, 60, BUTTON_COLOR, "^")
    boton_abajo = Botoia(grid_width + (width - grid_width) // 2 - 60 // 2, height - 2 * botoien_dist, 60, 60, BUTTON_COLOR, "v")
    boton_izquierda = Botoia(grid_width + (width - grid_width) // 2 - 60 // 2 - botoien_dist , height - 3 * botoien_dist, 60, 60, BUTTON_COLOR, "<")
    boton_derecha = Botoia(grid_width + (width - grid_width) // 2 - 60 // 2 + botoien_dist , height - 3 * botoien_dist, 60, 60, BUTTON_COLOR, ">")

    # Loop orokorra
    while running:
        for event in pygame.event.get():
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT: # Exekutatzeaz bukatzeko
                running = False
                zer_egin = "terminar"
            elif keys[pygame.K_RETURN]: # Enter botoia sakatzerakoan
                pass
            elif keys[pygame.K_UP] and pilla_pilla.turno == pilla_pilla.modo_de_juego and not pilla_pilla.juego_terminado:
                if pilla_pilla.turno == "perseguidor" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguidor + (-1,0),"perseguidor"):
                    pilla_pilla.posicion_anterior_perseguidor = pilla_pilla.posicion_perseguidor
                    pilla_pilla.posicion_perseguidor = pilla_pilla.posicion_perseguidor + np.array((-1,0))
                    pilla_pilla.iteracion_perseguidor += 1
                    pilla_pilla.turno = "perseguido"
                    if np.random.binomial(1,pilla_pilla.probabilidad_cambio_de_turno):
                        pilla_pilla.turno = "perseguidor"
                    pilla_pilla.iteracion += 1
                    pilla_pilla.ha_terminado()
                elif pilla_pilla.turno == "perseguido" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguido + (-1,0),"perseguido"):
                    pilla_pilla.posicion_anterior_perseguido = pilla_pilla.posicion_perseguido
                    pilla_pilla.posicion_perseguido = pilla_pilla.posicion_perseguido + np.array((-1,0))
                    pilla_pilla.iteracion_perseguido += 1
                    pilla_pilla.turno = "perseguidor"
                    pilla_pilla.iteracion += 1
                    pilla_pilla.ha_terminado()
            elif keys[pygame.K_DOWN] and pilla_pilla.turno == pilla_pilla.modo_de_juego and not pilla_pilla.juego_terminado:
                if pilla_pilla.turno == "perseguidor" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguidor + (1,0),"perseguidor"):
                    pilla_pilla.posicion_anterior_perseguidor = pilla_pilla.posicion_perseguidor
                    pilla_pilla.posicion_perseguidor = pilla_pilla.posicion_perseguidor + np.array((1,0))
                    pilla_pilla.iteracion_perseguidor += 1
                    pilla_pilla.turno = "perseguido"
                    if np.random.binomial(1,pilla_pilla.probabilidad_cambio_de_turno):
                        pilla_pilla.turno = "perseguidor"
                    pilla_pilla.iteracion += 1
                    pilla_pilla.ha_terminado()
                elif pilla_pilla.turno == "perseguido" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguido + (1,0),"perseguido"):
                    pilla_pilla.posicion_anterior_perseguido = pilla_pilla.posicion_perseguido
                    pilla_pilla.posicion_perseguido = pilla_pilla.posicion_perseguido + np.array((1,0))
                    pilla_pilla.iteracion_perseguido += 1
                    pilla_pilla.turno = "perseguidor"
                    pilla_pilla.iteracion += 1
                    pilla_pilla.ha_terminado()
            elif keys[pygame.K_RIGHT] and pilla_pilla.turno == pilla_pilla.modo_de_juego and not pilla_pilla.juego_terminado:
                if pilla_pilla.turno == "perseguidor" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguidor + (0,1),"perseguidor"):
                    pilla_pilla.posicion_anterior_perseguidor = pilla_pilla.posicion_perseguidor
                    pilla_pilla.posicion_perseguidor = pilla_pilla.posicion_perseguidor + np.array((0,1))
                    pilla_pilla.iteracion_perseguidor += 1
                    pilla_pilla.turno = "perseguido"
                    if np.random.binomial(1,pilla_pilla.probabilidad_cambio_de_turno):
                        pilla_pilla.turno = "perseguidor"
                    pilla_pilla.iteracion += 1
                    pilla_pilla.ha_terminado()
                elif pilla_pilla.turno == "perseguido" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguido + (0,1),"perseguido"):
                    pilla_pilla.posicion_anterior_perseguido = pilla_pilla.posicion_perseguido
                    pilla_pilla.posicion_perseguido = pilla_pilla.posicion_perseguido + np.array((0,1))
                    pilla_pilla.iteracion_perseguido += 1
                    pilla_pilla.turno = "perseguidor"
                    pilla_pilla.iteracion += 1
                    pilla_pilla.ha_terminado()

            elif  keys[pygame.K_LEFT] and pilla_pilla.turno == pilla_pilla.modo_de_juego and not pilla_pilla.juego_terminado:
                if pilla_pilla.turno == "perseguidor" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguidor + (0,-1),"perseguidor"):
                    pilla_pilla.posicion_anterior_perseguidor = pilla_pilla.posicion_perseguidor
                    pilla_pilla.posicion_perseguidor = pilla_pilla.posicion_perseguidor + np.array((0,-1))
                    pilla_pilla.iteracion_perseguidor += 1
                    pilla_pilla.turno = "perseguido"
                    if np.random.binomial(1,pilla_pilla.probabilidad_cambio_de_turno):
                        pilla_pilla.turno = "perseguidor"
                    pilla_pilla.iteracion += 1
                    pilla_pilla.ha_terminado()
                elif pilla_pilla.turno == "perseguido" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguido + (0,-1),"perseguido"):
                    pilla_pilla.posicion_anterior_perseguido = pilla_pilla.posicion_perseguido
                    pilla_pilla.posicion_perseguido = pilla_pilla.posicion_perseguido + np.array((0,-1))
                    pilla_pilla.iteracion_perseguido += 1
                    pilla_pilla.turno = "perseguidor"
                    pilla_pilla.iteracion += 1
                    pilla_pilla.ha_terminado()

            elif event.type == pygame.MOUSEBUTTONDOWN: # Xaguaren botoiren bat sakatzen bada
                if event.button == 1: # Ezkerreko botoia sakatzen bada
                    if botoia_itzuli_menura.rect.collidepoint(event.pos):
                        running = False
                        zer_egin = "menu"
                    if boton_arriba.rect.collidepoint(event.pos) and pilla_pilla.turno == pilla_pilla.modo_de_juego and not pilla_pilla.juego_terminado:
                        if pilla_pilla.turno == "perseguidor" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguidor + (-1,0),"perseguidor"):
                            pilla_pilla.posicion_anterior_perseguidor = pilla_pilla.posicion_perseguidor
                            pilla_pilla.posicion_perseguidor = pilla_pilla.posicion_perseguidor + np.array((-1,0))
                            pilla_pilla.iteracion_perseguidor += 1
                            pilla_pilla.turno = "perseguido"
                            if np.random.binomial(1,pilla_pilla.probabilidad_cambio_de_turno):
                                pilla_pilla.turno = "perseguidor"
                            pilla_pilla.iteracion += 1
                            pilla_pilla.ha_terminado()
                        elif pilla_pilla.turno == "perseguido" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguido + (-1,0),"perseguido"):
                            pilla_pilla.posicion_anterior_perseguido = pilla_pilla.posicion_perseguido
                            pilla_pilla.posicion_perseguido = pilla_pilla.posicion_perseguido + np.array((-1,0))
                            pilla_pilla.iteracion_perseguido += 1
                            pilla_pilla.turno = "perseguidor"
                            pilla_pilla.iteracion += 1
                            pilla_pilla.ha_terminado()
                    
                    if boton_abajo.rect.collidepoint(event.pos) and pilla_pilla.turno == pilla_pilla.modo_de_juego and not pilla_pilla.juego_terminado:
                        if pilla_pilla.turno == "perseguidor" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguidor + (1,0),"perseguidor"):
                            pilla_pilla.posicion_anterior_perseguidor = pilla_pilla.posicion_perseguidor
                            pilla_pilla.posicion_perseguidor = pilla_pilla.posicion_perseguidor + np.array((1,0))
                            pilla_pilla.iteracion_perseguidor += 1
                            pilla_pilla.turno = "perseguido"
                            if np.random.binomial(1,pilla_pilla.probabilidad_cambio_de_turno):
                                pilla_pilla.turno = "perseguidor"
                            pilla_pilla.iteracion += 1
                            pilla_pilla.ha_terminado()
                        elif pilla_pilla.turno == "perseguido" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguido + (1,0),"perseguido"):
                            pilla_pilla.posicion_anterior_perseguido = pilla_pilla.posicion_perseguido
                            pilla_pilla.posicion_perseguido = pilla_pilla.posicion_perseguido + np.array((1,0))
                            pilla_pilla.iteracion_perseguido += 1
                            pilla_pilla.turno = "perseguidor"
                            pilla_pilla.iteracion += 1
                            pilla_pilla.ha_terminado()
                    
                    if boton_derecha.rect.collidepoint(event.pos) and pilla_pilla.turno == pilla_pilla.modo_de_juego and not pilla_pilla.juego_terminado:
                        if pilla_pilla.turno == "perseguidor" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguidor + (0,1),"perseguidor"):
                            pilla_pilla.posicion_anterior_perseguidor = pilla_pilla.posicion_perseguidor
                            pilla_pilla.posicion_perseguidor = pilla_pilla.posicion_perseguidor + np.array((0,1))
                            pilla_pilla.iteracion_perseguidor += 1
                            pilla_pilla.turno = "perseguido"
                            if np.random.binomial(1,pilla_pilla.probabilidad_cambio_de_turno):
                                pilla_pilla.turno = "perseguidor"
                            pilla_pilla.iteracion += 1
                            pilla_pilla.ha_terminado()
                        elif pilla_pilla.turno == "perseguido" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguido + (0,1),"perseguido"):
                            pilla_pilla.posicion_anterior_perseguido = pilla_pilla.posicion_perseguido
                            pilla_pilla.posicion_perseguido = pilla_pilla.posicion_perseguido + np.array((0,1))
                            pilla_pilla.iteracion_perseguido += 1
                            pilla_pilla.turno = "perseguidor"
                            pilla_pilla.iteracion += 1
                            pilla_pilla.ha_terminado()

                    if boton_izquierda.rect.collidepoint(event.pos) and pilla_pilla.turno == pilla_pilla.modo_de_juego and not pilla_pilla.juego_terminado:
                        if pilla_pilla.turno == "perseguidor" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguidor + (0,-1),"perseguidor"):
                            pilla_pilla.posicion_anterior_perseguidor = pilla_pilla.posicion_perseguidor
                            pilla_pilla.posicion_perseguidor = pilla_pilla.posicion_perseguidor + np.array((0,-1))
                            pilla_pilla.iteracion_perseguidor += 1
                            pilla_pilla.turno = "perseguido"
                            if np.random.binomial(1,pilla_pilla.probabilidad_cambio_de_turno):
                                pilla_pilla.turno = "perseguidor"
                            pilla_pilla.iteracion += 1
                            pilla_pilla.ha_terminado()
                        elif pilla_pilla.turno == "perseguido" and pilla_pilla.es_posible(pilla_pilla.posicion_perseguido + (0,-1),"perseguido"):
                            pilla_pilla.posicion_anterior_perseguido = pilla_pilla.posicion_perseguido
                            pilla_pilla.posicion_perseguido = pilla_pilla.posicion_perseguido + np.array((0,-1))
                            pilla_pilla.iteracion_perseguido += 1
                            pilla_pilla.turno = "perseguidor"
                            pilla_pilla.iteracion += 1
                            pilla_pilla.ha_terminado()
                    

        # while buklearen amaieran, pantaila marraztu, textua idatzi eta aktualizatzeko
        dibujar_cuadricula(pilla_pilla,screen)

        screen.blit(izenburua.render("Jugando" if not pilla_pilla.juego_terminado else "Juego terminado", True, TEXT_COLOR if not pilla_pilla.juego_terminado else RED),(width - 295, 30))
        screen.blit(info_turno.render(f"Es el turno de: {pilla_pilla.turno}",True, RED if pilla_pilla.turno == "perseguidor" else GREEN),(width-295,70))
        screen.blit(info_turno.render(f"Tu eres: {pilla_pilla.modo_de_juego}",True, TEXT_COLOR),(width-295,90))
        screen.blit(info_turno.render(f"Iteracion: {pilla_pilla.iteracion}",True, TEXT_COLOR),(width-295,110))
        if pilla_pilla.juego_terminado:
            screen.blit(info_turno.render(f"Distancia faltante: {pilla_pilla.distancia_faltante}",True, TEXT_COLOR),(width-295,130))
        if not pilla_pilla.distancia_faltante == float("inf"):
            if pilla_pilla.distancia_faltante == 0:
                screen.blit(info_turno.render(f"Pillado!",True, RED),(width-295,150))
            else:
                screen.blit(info_turno.render(f"Escapado!",True, GREEN),(width-295,150))


        botoia_itzuli_menura.draw(screen)
        boton_izquierda.draw(screen)
        boton_abajo.draw(screen)
        boton_derecha.draw(screen)
        boton_arriba.draw(screen)
        pygame.display.flip()
        
        # Actualizar movimiento de la partida
        if pilla_pilla.modo_de_juego != "maquina vs maquina":
            if not pilla_pilla.modo_de_juego == pilla_pilla.turno: # Si no es el turno del jugador (cuando es el turno del jugador se maneja por pygame)
                pilla_pilla.siguiente_movimiento()
        else:
            if not pilla_pilla.juego_terminado:
                pilla_pilla.siguiente_movimiento()
        
        # if not distancia_manhattan(pilla_pilla) == 0:
        #     pilla_pilla.siguiente_movimiento()
        # print(pilla_pilla)
    return zer_egin

def conseguir_nombres_de_mapas():
    direct = os.getcwd()
    archivos = os.listdir(direct)
    lista_de_mapas = []
    for archivo in archivos:
        if archivo[-3:] == "pkl":
            lista_de_mapas.append(archivo)
    return lista_de_mapas

def dibujar_grid_ajustes(kuadrikula,screen):
    """
    grid = 28 x 28 tamainiako matrize bat: matrizearen elementuak 0 - 255 tarteko zenbakiak
    izango dira, 28 x 28 pixeleko pantaila baten gris-eskalak izanik
    """
    n = len(kuadrikula)
    grid_size_new = 20
    width_despl = 550
    height_despl = 150
    for i in range(n):
        for j in range(n):
            balioa = kuadrikula[i][j]
            if balioa == 1:
                pygame.draw.rect(screen, BLACK, (width_despl+j * grid_size_new,height_despl + i * grid_size_new, grid_size_new, grid_size_new))
                pygame.draw.rect(screen, GRID_COLOR, (width_despl+j * grid_size_new,height_despl + i * grid_size_new, grid_size_new, grid_size_new), 1)
            elif balioa == 0:   
                pygame.draw.rect(screen, WHITE, (width_despl+j * grid_size_new, height_despl +i * grid_size_new, grid_size_new, grid_size_new))
                pygame.draw.rect(screen, GRID_COLOR, (width_despl+j * grid_size_new,height_despl + i * grid_size_new, grid_size_new, grid_size_new), 1)
                
    pygame.draw.rect(screen, RED, (width_despl+0 * grid_size_new,height_despl + 0 * grid_size_new, grid_size_new, grid_size_new))
    pygame.draw.rect(screen, GRID_COLOR, (width_despl+0 * grid_size_new,height_despl + 0 * grid_size_new, grid_size_new, grid_size_new), 1)   

    pygame.draw.rect(screen, GREEN, (width_despl+(n-1) * grid_size_new,height_despl + (n-1) * grid_size_new, grid_size_new, grid_size_new))
    pygame.draw.rect(screen, GRID_COLOR, (width_despl+(n-1) * grid_size_new, height_despl +(n-1) * grid_size_new, grid_size_new, grid_size_new), 1)   
            # karratuaren zenbat betetzen den definitzeko, 0 da "default" balioa eta karratu osoa betetzen du.


def seleccionar_ajustes(mapa,modo_de_juego,algoritmo_1,profundidad_minmax,algoritmo_2,profundidad_minmax_2,iteraciones_maximas, probabilidad_cambio_de_turno,hay_poda):
    # pygame
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Jugando")

    # Aldagai erabilgarriak
    running = True
    botoien_distantzia = height//10
    clock = pygame.time.Clock()
    delta_time = clock.tick(60)/ 1000.0
    mapas = conseguir_nombres_de_mapas()
    modos_de_juego = ["perseguidor","perseguido","maquina vs maquina"]
    i_modo_juego = modos_de_juego.index(modo_de_juego)
    i_mapas = mapas.index(mapa)
    mapa_matriz = pickle.load(open(mapas[i_mapas],"rb"))
    algoritmos = ["A estrella", "distancia de manhattan", "distancia euclidea"]
    i_algoritmos_1 = algoritmos.index(algoritmo_1)
    i_algoritmos_2 = algoritmos.index(algoritmo_2)

    # textua
    izenburua = pygame.font.Font(None, 50)
    informacion = pygame.font.Font(None, 30)
    mapa_info = pygame.font.Font(None, 40)

    # Botoiak
    
    botoia_mapaz_aldatu = Botoia(50,70, 190, 40, BUTTON_COLOR, "Cambiar de mapa")
    botoia_jokoz_aldatu = Botoia(50,70 + botoien_distantzia, 190, 40, BUTTON_COLOR, "Cambiar modo de juego")
    botoia_algoritmoz_aldatu_1 = Botoia(50,70 + 2*botoien_distantzia, 190, 40, BUTTON_COLOR, "Cambiar algoritmo")
    botoia_algoritmoz_aldatu_2 = Botoia(50,70 + 4*botoien_distantzia, 190, 40, BUTTON_COLOR, "Cambiar algoritmo 2")
    botoia_minmax_aldatu = Botoia(50,70 + 8*botoien_distantzia, 190, 40, BUTTON_COLOR, "Poda on/off")
    
    botoia_itzuli_menura = Botoia(700, height - 50, 190, 40, BUTTON_COLOR, "Menu")

    # Scroll barrak
    manager = pygame_gui.UIManager((width, height))
    slider_1 = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((50 + 15,10 + 70 + 3* botoien_distantzia + 10), (300, 20)),
        start_value=profundidad_minmax,  # Valor inicial del deslizador
        value_range=(1, 25),  # Rango de valores del deslizador
        manager=manager)
    
    slider_2 = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((50 + 15,10 + 70 + 5* botoien_distantzia + 10), (300, 20)),
        start_value=profundidad_minmax_2,  # Valor inicial del deslizador
        value_range=(1, 25),  # Rango de valores del deslizador
        manager=manager)
    
    slider_3 = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((50 + 15,10 + 70 + 6* botoien_distantzia + 10), (300, 20)),
        start_value=iteraciones_maximas,  # Valor inicial del deslizador
        value_range=(1, 500),  # Rango de valores del deslizador
        manager=manager)
    
    slider_4 = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((50 + 15,10 + 70 + 7* botoien_distantzia + 10), (300, 20)),
        start_value=probabilidad_cambio_de_turno,  # Valor inicial del deslizador
        value_range=(0,1),  # Rango de valores del deslizador
        manager=manager)
    

    while running:
        for event in pygame.event.get():
            manager.process_events(event)
            keys = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                running = False
                zer_egin = "terminar"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if botoia_itzuli_menura.rect.collidepoint(event.pos):
                        running = False
                        zer_egin = "menu"
                    elif botoia_jokoz_aldatu.rect.collidepoint(event.pos):
                        i_modo_juego = (i_modo_juego + 1) % 3
                    elif botoia_mapaz_aldatu.rect.collidepoint(event.pos):
                        i_mapas = (i_mapas + 1) % len(mapas)
                        mapa_matriz = pickle.load(open(mapas[i_mapas],"rb"))
                    elif botoia_algoritmoz_aldatu_1.rect.collidepoint(event.pos):
                        i_algoritmos_1 = (i_algoritmos_1 + 1) % len(algoritmos)
                    elif botoia_algoritmoz_aldatu_2.rect.collidepoint(event.pos):
                        i_algoritmos_2 = (i_algoritmos_2 + 1) % len(algoritmos)
                    elif botoia_minmax_aldatu.rect.collidepoint(event.pos):
                        hay_poda = not hay_poda

        profundidad_minmax = round(slider_1.get_current_value())
        profundidad_minmax_2 = round(slider_2.get_current_value())
        imax = round(slider_3.get_current_value())
        probabilidad_cambio_de_turno = round(slider_4.get_current_value(),2)
        screen.fill(WHITE)

        # Mapa:
        dibujar_grid_ajustes(mapa_matriz,screen)
        
        # Textuak:
        screen.blit(izenburua.render("Seleccionar ajustes del juego", True, (0,0,0)),(20, 20))
        screen.blit(informacion.render(mapas[i_mapas],True,(34,139,34)),(50 + 190 + 15,10 + 70 ))
        screen.blit(informacion.render(modos_de_juego[i_modo_juego],True,(34,139,34)),(50 + 190 + 15,10 + 70 + botoien_distantzia))
        screen.blit(informacion.render(algoritmos[i_algoritmos_1],True,(34,139,34)),(50 + 190 + 15,10 + 70 + 2* botoien_distantzia))
        screen.blit(informacion.render(f"Cambiar profundidad minmax:",True,(0,0,0)),(50 + 15, + 70 + 3* botoien_distantzia))
        screen.blit(informacion.render(f"{profundidad_minmax}",True,(34,139,34)),(50 + 15 + 310, + 70 + 3* botoien_distantzia))
        screen.blit(informacion.render(algoritmos[i_algoritmos_2],True,(34,139,34)),(50 + 190 + 15,10 + 70 + 4* botoien_distantzia))
        screen.blit(informacion.render(f"Cambiar profundidad minmax 2:",True,(0,0,0)),(50 + 15, + 70 + 5* botoien_distantzia))
        screen.blit(informacion.render(f"{profundidad_minmax_2}",True,(34,139,34)),(50 + 35 + 310, + 70 + 5* botoien_distantzia))
        screen.blit(informacion.render(f"Iteraciones maximas:",True,(0,0,0)),(50 + 15, + 70 + 6* botoien_distantzia))
        screen.blit(informacion.render(f"{imax}",True,(34,139,34)),(50 + 35 + 310, + 70 + 6* botoien_distantzia))
        screen.blit(informacion.render(f"Probabilidad cambio de turno:",True,(0,0,0)),(50 + 15, + 70 + 7* botoien_distantzia))
        screen.blit(informacion.render(f"{probabilidad_cambio_de_turno}",True,(34,139,34)),(50 + 35 + 310, + 70 + 7* botoien_distantzia))
        screen.blit(informacion.render(f"Hay poda = {hay_poda}", True,(34,139,34)),(50 + 190 + 15,10 + 70 + 8* botoien_distantzia))

        screen.blit(mapa_info.render(f"{mapas[i_mapas]}",True,(34,139,34)),(620, 100))

        # Scroll barrak:
        manager.update(delta_time)
        manager.draw_ui(screen)

        # Botoiak:
        botoia_itzuli_menura.draw(screen)
        botoia_mapaz_aldatu.draw(screen)
        botoia_jokoz_aldatu.draw(screen)
        botoia_algoritmoz_aldatu_1.draw(screen)
        botoia_algoritmoz_aldatu_2.draw(screen)
        botoia_minmax_aldatu.draw(screen)


        pygame.display.flip()


    return [zer_egin, mapas[i_mapas], modos_de_juego[i_modo_juego], algoritmos[i_algoritmos_1], profundidad_minmax, algoritmos[i_algoritmos_2],profundidad_minmax_2, imax,probabilidad_cambio_de_turno,hay_poda]

def main():
    que_hacer = "menu"

    # Ajustes iniciales
    mapa = "mapa_1.pkl"
    modo_de_juego = "perseguido"
    algoritmo_1 = "A estrella"
    profundidad_minmax = 20
    algoritmo_2 = "distancia de manhattan"
    profundidad_minmax_2 = 10
    iteraciones_maximas = 200
    probabilidad_cambio_de_turno = 0.05
    hay_poda = True

    pygame.init()

    while que_hacer != "terminar":

        if que_hacer == "menu":
            que_hacer = menu()

        elif que_hacer == "crear mapa":
            que_hacer = crear_mapa()

        elif que_hacer == "ajustes":
            info = seleccionar_ajustes(mapa,modo_de_juego,algoritmo_1, profundidad_minmax, 
                                       algoritmo_2, profundidad_minmax_2, iteraciones_maximas, 
                                       probabilidad_cambio_de_turno,hay_poda)
            que_hacer = info[0]
            mapa = info[1]
            modo_de_juego = info[2]
            algoritmo_1 = info[3]
            profundidad_minmax = info[4]
            algoritmo_2 = info[5]
            profundidad_minmax_2 =info[6]
            iteraciones_maximas =info[7]
            probabilidad_cambio_de_turno = info[8]
            hay_poda = info[9]

        elif que_hacer == "juego":

            mapa_matriz = pickle.load(open(mapa,"rb"))

            if algoritmo_1 == "A estrella":
                alg1 = A_star
            elif algoritmo_1 == "distancia euclidea":
                alg1 = distancia_euclidea
            else:
                alg1 = distancia_manhattan

            if algoritmo_2 == "A estrella":
                alg2 = A_star
            elif algoritmo_2 == "distancia euclidea":
                alg2 = distancia_euclidea
            else:
                alg2 = distancia_manhattan

            p1 = PillaPilla(modo_de_juego,alg1,profundidad_minmax,mapa = mapa_matriz,
                            funcion_evaluacion_2=alg2, profundidad_minmax_2=profundidad_minmax_2,
                              imax=iteraciones_maximas,probabilidad_cambio_de_turno = probabilidad_cambio_de_turno, hay_poda = hay_poda)
            que_hacer = juego(p1)
            
    pygame.quit()








if __name__ == "__main__":
    main()

