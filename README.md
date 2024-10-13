# Algorithmic-Hide-and-Seek-
Minmax algorithm applied to a simplified version of hide and seek. It uses the A star algorithm as evaluation function. The rules of the game are the following ones:

- The game is turn-based.
- The seeker is the red player and the hider is the green one.
- The seeker always plays first.
- Players cannot return to the exact spot they moved from on the previous turn.
- The game ends either when the seeker catches the hider or after 200 turns (100 turns per player).

In order to play the game execute the "juego.py" file.


## Customizable settings:

- You can create personalized maps.
- You can change the game mode: play as the hider, the seeker, or machine vs. machine.
- You can choose the evaluation function for the opponent (algorithm 1) and set the depth at which the function is evaluated.
- You can set the maximum number of game turns.
- In machine vs. machine (MvsM) mode, algorithm 1 controls the seeker, and algorithm 2 controls the hider.
- You can decide wether there is a probability (default = 0) for the seeker to repeat their turn or not