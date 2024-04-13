# Minmax_Algorithm_Game
Aplicación del algoritmo minmax con poda alfa-beta para un juego del estilo "pilla-pilla".

Se trata del juego de "pilla-pilla", puedes elegir jugar como perseguidor o como perseguido. El nivel de dificultad, junto a otros muchos parámetros, los eliges tú.

La dificultad varía dependiendo de la función de evaluación que se use: el algoritmo A estrella, la distancia de manhattan y la distancia euclidea (dificultad decreciente). Por otro lado, cuanta mayor profundidad tenga el algoritmo "minmax", mayor dificultad tendrá el juego.

El juego también incluye un modo de creación de mapas, sin embargo, hay tres mapas predefinidos: "mapa_1.pkl", "mapa_2.pkl" y "mapa_3.pkl". Además, puedes seleccionar el modo de juego "maquina vs  maquina" y ver cómo juegan dos algoritmos diferentes:
- algoritmo1 = algoritmo del perseguidor
- algoritmo2 = algoritmo del perseguido

El juego tiene algunas reglas:
- Es por turnos y siempre empieza el perseguidor
- Las posiciones iniciales son siempre las mismas: las esquinas
- Los jugadores no pueden atravesar muros
- No se puede volver a la última casilla que has pisado
- De vez en cuando (la probabilidad se cambia en los ajustes) al perseguidor se le dan turnos dobles
- El juego acaba cuando un jugador esté al lado, encima o debajo del otro (no en las diagonales), o cuando se llegue a las iteraciones máximas (200 por defecto, se cambia en ajustes)
