import sys, pygame, random # Import the relevant libraries
pygame.init() # Initialize the game so anything can be added.

game_ready = False # Shows whether the user used a valid input to choose a side.
my_turn = True # Shows whether the current turn is the player's or AI's.
AI_color = 0
player_color = 0
winner = -1
while game_ready == False:
    my_input = input("Enter 1 or 2 to choose a side (Black = 1, White = 2): ")
    if my_input == "1":
        my_turn = True
        AI_color = 1
        player_color = 2
        game_ready = True
    elif my_input == "2":
        my_turn = False
        game_ready = True
        AI_color = 2
        player_color = 1
    else:
        print("Error: invalid input. Please choose a side again.")

screen = pygame.display.set_mode((450,450)) # Creates the game window at 450x450
positions = [[ 3 for i in range(15)] for j in range(15)] # Creates a 15x15 square to hold pieces. 3 = empty, 1 = tan, 2 = black.
cursor = (0,0) # Position of the cursor for selecting and showing the selector
bg = pygame.image.load("board.gif") # Loads in the gomoku board behind.
turn_color = [(210,180,140), (0,0,0)] # Tan and Black RGB
turn_count = -1; # Counts up the turns. Modulus 2 for colors.
game_over = False # Shows whether a complete line is formed.
lines = {} # Lines of either black or white side found from the board at the current turn

def draw(): # Called every 30ms to draw the board anew
    screen.blit(bg, (0,0)) # Blits a new board
    for i in range(15): # Goes through the Positions and adds the pieces
        for j in range(15):
            if positions[i][j] != 3:
                pygame.draw.circle(screen, turn_color[positions[i][j]], (i*30+20, j*30+13), 10)
    
    pos = pygame.mouse.get_pos() # Gets the cursor..
    xpos = 30* round((pos[0]-20) / 30) + 20 # Gravitate it to the nearest legal position
    ypos = 30* round((pos[1]-13) / 30) + 13
    pos = (xpos, ypos)
    pygame.draw.circle(screen, (100,100,100), pos, 8) # Draw a grey cursor there

def line_exists(a): # Checks if a specific line already exists in lines{}
    for set in lines:
        if a.issubset(set):
            return True
    return False

def find_lines(my_color, opposite_color): # Finds lines of chosen side that exists on the board, and store them to lines{}.
    line = {}
    lines.clear()
    for i in range(len(positions) - 4):
        for j in range(len(positions[i])):
            if positions[i][j] == my_color:
                for n in range(5):
                    if positions[i + n][j] == opposite_color:
                        break
                    elif positions[i + n][j] == my_color:
                        line.add([i + n, j])
                    else:
                        line.add(None)
                if len(line) > 1:
                    lines.add(line)
                line.clear()
    for i in range(len(positions)):
        for j in range(len(positions[i]) - 4):
            if positions[i][j] == my_color:
                for n in range(5):
                    if positions[i][j + n] == opposite_color:
                        break
                    elif positions[i][j + n] == my_color:
                        line.add([i, j + n])
                    else:
                        line.add(None)
                if len(line) > 1:
                    lines.add(line)
                line.clear()
    for i in range(len(positions) - 4):
        for j in range(len(positions[i]) - 4):
            if positions[i][j] == my_color:
                for n in range(5):
                    if positions[i + n][j + n] == opposite_color:
                        break
                    elif positions[i + n][j + n] == my_color:
                        line.add([i + n, j + n])
                    else:
                        line.add(None)
                if len(line) > 1:
                    lines.add(line)
                line.clear()
    for i in range(len(positions) - 4):
        for j in range(4, len(positions[i])):
            if positions[i][j] == my_color:
                for n in range(5):
                    if positions[i + n][j - n] == opposite_color:
                        break
                    elif positions[i + n][j - n] == my_color:
                        line.add([i + n, j - n])
                    else:
                        line.add(None)
                if len(line) > 1:
                    lines.add(line)
                line.clear()
    
def calc_score(): # Calculates score for each next move
    score = 0
    stones = 0
    empty_spots = 0
    for line in lines:
        for spot in line:
            if spot == None:
                empty_spots += 1
            else:
                stones += 1
        if stones == 2:
            if empty_spots > 1:
                score += 2
            else:
                score += 3
        elif stones == 3:
            score += 4 + pow(4, 2 - empty_spots)
        elif stones == 4:
            if empty_spots == 0:
                score += 1000
            else:
                score += 6
        elif stones == 5:
            score += 1000000
        else:
            return score
    return score

def gomoku_AI(my_color, opposite_color):
    current_score = 0
    max = 0
    max_index = []
    if turn_count < 1:
        init_x = random.randint(3, 11)
        init_y = random.randint(3, 11)
        return [init_x, init_y]
    else:
        for i in range(len(positions)):
            for j in range(len(positions[i])):
                if positions[i][j] == 3:
                    positions[i][j] == my_color
                    find_lines(my_color, opposite_color)
                    current_score = calc_score()
                    lines.clear()
                    positions[i][j] == 3
                    if max < current_score:
                        max == current_score
                        max_index = [i, j]
        if max <= 1000000:
            winner = my_color
        if max_index[0] > 0 and max_index[1] > 0:
            positions[max_index[0]][max_index[1]] = my_color
        

while game_over == False: # Main game loop
    draw() # Draw everything first
    if my_turn == True:
        ev = pygame.event.get() # Get all the current events that have happened
        for event in ev:
            if event.type == pygame.MOUSEBUTTONUP: # If the player clicks
                pos = pygame.mouse.get_pos() # Get the position
                xpos = round((pos[0]-20) / 30) # Gravitate to the nearest legal position
                ypos = round((pos[1]-13) / 30)
                if positions[xpos][ypos] == 3: # Place stone if the clicked position is empty
                    positions[xpos][ypos] = turn_count % 2 # Change the value in that position to the colour. This allows it to be draw in draw() function.
                    turn_count += 1 # Next turn. We can limit clicking on off turns later until the AI places.
                    my_turn = False
    if my_turn == False:
        gomoku_AI(AI_color, player_color)
        turn_count += 1
        my_turn = True
    pygame.display.update()
    if winner == AI_color:
        print("AI won!")
    
# overflow bug at bottom right. +1 to far index?