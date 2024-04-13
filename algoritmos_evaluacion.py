import pygame
import numpy as np
from math import sqrt


def distancia_manhattan(pilla_pilla):
    return abs(pilla_pilla.posicion_perseguidor[0]-pilla_pilla.posicion_perseguido[0]) + abs(pilla_pilla.posicion_perseguidor[1]-pilla_pilla.posicion_perseguido[1])

def distancia_euclidea(pilla_pilla):
    return sqrt(abs(pilla_pilla.posicion_perseguidor[0]-pilla_pilla.posicion_perseguido[0])**2 + abs(pilla_pilla.posicion_perseguidor[1]-pilla_pilla.posicion_perseguido[1])**2)









# ---------------------------------------------------------------
# ------------------INICIO ALGORITMO A ESTRELLA------------------
# ---------------------------------------------------------------
def heuristico(posicion,posicion_final):
    return abs(posicion_final[0]-posicion[0]) + abs(posicion_final[1]-posicion[1])

def calcular_f(c,posicion_final):
    return (len(c)-1) + heuristico(c[-1],posicion_final)

def esta_dentro_del_tablero(posicion,n):
    return ( 0 <= posicion[0] ) and (posicion[0] < n) and ( 0 <= posicion[1] ) and (posicion[1] < n)

def no_choca_con_borde(nuevo_movimiento,mapa):
    x,y = nuevo_movimiento
    return mapa[x][y] != 1

def sucesores(c_min,mapa,visitados,g_visitados,A,f,n,posicion_final,f_sol):
    movimientos = [(1,0),(0,1),(-1,0),(0,-1)]
    x,y = c_min[-1]
    for dx,dy in movimientos:
        nuevo_movimiento = (x+dx,y+dy)
        if esta_dentro_del_tablero(nuevo_movimiento,n) and no_choca_con_borde(nuevo_movimiento,mapa) and nuevo_movimiento not in c_min and nuevo_movimiento not in visitados:
            if calcular_f(c_min + [nuevo_movimiento],posicion_final) <= f_sol:
                A.append(c_min + [nuevo_movimiento])
                visitados.append(nuevo_movimiento)
                g_visitados.append(len(c_min))
                f.append(calcular_f(c_min + [nuevo_movimiento],posicion_final))
        
        elif esta_dentro_del_tablero(nuevo_movimiento,n) and no_choca_con_borde(nuevo_movimiento,mapa) and nuevo_movimiento not in c_min and nuevo_movimiento in visitados:
            indice_visitados = visitados.index(nuevo_movimiento)
            if len(c_min) < g_visitados[indice_visitados] and calcular_f(c_min + [nuevo_movimiento],posicion_final) <= f_sol:
                g_visitados[indice_visitados] = len(c_min)
                A.append(c_min + [nuevo_movimiento])
                f.append(calcular_f(c_min + [nuevo_movimiento],posicion_final))
                
            
def A_star(pilla_pilla):
    # if tuple(pilla_pilla.posicion_perseguido) == tuple(pilla_pilla.posicion_perseguidor):
    #     return 0
    mapa = pilla_pilla.mapa.copy()
    i,j = pilla_pilla.posicion_perseguidor
    mapa[i,j] = 3
    i,j = pilla_pilla.posicion_perseguido
    mapa[i,j] = 4
    n = len(mapa)
    
    # Definir posiciones iniciales y finales: 
    posicion_inicial = (0,0)
    posicion_final = (n-1,n-1)
    for i,fila in enumerate(mapa):
        for j,valor in enumerate(fila):
            if valor == 3:
                posicion_inicial = (i,j)
            elif valor == 4:
                posicion_final = (i,j)

    if posicion_inicial == (0,0):
        mapa[0][0] = 3
    if posicion_final == (n-1,n-1):
        mapa[n-1][n-1] = 4
    # print(f"Posicion inicial = {posicion_inicial}")
    # print(f"Posicion final = {posicion_final}")

    # Variables necesarias:
    visitados = [posicion_inicial] # Importa el orden
    g_visitados = [0] # Importa el orden
    A = [ [posicion_inicial] ] # Lista de listas (caminos), importa el orden
    f = [ calcular_f(A[0],posicion_final) ]
    sol = None # Solucion temporal
    f_sol = float("inf") # Distancia de la mejor solucion hasta el momento (como no
    # tenemos soluciones lo definiremos como infinito)
    
    while A != []:
        min_index = np.argmin(f)
        c_min = A[min_index]
        f_c_min = f[min_index]
        A.pop(min_index)
        f.pop(min_index)
        if c_min[-1] == posicion_final and f_c_min < f_sol: # Si es una solución mejor a la que ya tenemos
            # Actualizar solucion y coste minimo:
            sol = c_min[:]
            f_sol = f_c_min
            # Podar:
            indices_para_podar = []
            for i,f_i in enumerate(f):
                if f_i >= f_sol:
                    indices_para_podar.append(i)
            A = [camino for indice,camino in enumerate(A) if indice not in indices_para_podar]
            f = [valor_f for indice, valor_f in enumerate(f) if indice not in indices_para_podar]

        else: # Si no es solución o es peor que la que ya tenemos
            sucesores(c_min,mapa,visitados,g_visitados,A,f,n,posicion_final,f_sol) # La función modificará las listas A, visitados y g_visitados

    return len(sol)-2


# ---------------------------------------------------------------
# --------------------FIN ALGORITMO A ESTRELLA-------------------
# ---------------------------------------------------------------
