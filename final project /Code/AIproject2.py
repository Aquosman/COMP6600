#@authors Josh Adkins, Henry Paek, Ian Fair

import sys, pygame, time, numpy # Import the relevant libraries
from numpy import random
from copy import deepcopy
pygame.init() # Initialize the game so anything can be added.

ai_turn = -1
player_turn = -1
while ai_turn == -1:
	my_input = input("Enter 0 or 1 to choose a side (Black = 0, White = 1): ")
	if my_input == "0":
		ai_turn = 1
		player_turn = 0
	elif my_input == "1":
		ai_turn = 0
		player_turn = 1
	else:
		print("Error: invalid input. Please choose a side again.")

screen = pygame.display.set_mode((450,450)) # Creates the game window at 450x450
positions = [[ 3 for i in range(15)] for j in range(15)] # Creates a 15x15 square to hold pieces. 3 = empty, 1 = tan, 2 = black.
cursor = (0,0) # Position of the cursor for selecting and showing the selector
bg = pygame.image.load("board.gif") # Loads in the gomaku board behind.
turn_color = [(0,0,0), (210,180,140)] # Tan and Black RGB
turn_count = 0; # Counts up the turns. Modulus 2 for colors.
game_over = False # Shows whether a complete line is formed.
last_move = (0,0)
NEARNESS_SCORE = 20	# Divisor to the weight that makes placing pieces closer better.
IN_A_ROW_SCORE = 1.3	# Exponent that makes placing multiple in a row more valuable than multiple intersections!

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

def gomoku_AI():
	if turn_count <= 1:
		x = random.randint(3)
		print(x)
		for i in range(3):
			if positions[6+x][6+i] == 3:
				positions[6+x][6+i] = ai_turn
				break
	else:
		score = alphabeta(positions, 3, (-sys.maxsize-1), sys.maxsize, True, 0, 0)
		#print("Score: ", score)
		#print("Move: ", last_move)
		positions[last_move[0]][last_move[1]] = ai_turn


def alphabeta(copy_positions, depth, alpha, beta, aiTurn_bool, xpos, ypos):
	#print("Depth: ", depth)
	if depth == 0: # If the maximum amount of later turns to look at is reached...
		#print("Score Pos: ", xpos, ypos)
		#print("Returning Score: ", get_value(copy_positions, xpos, ypos))
		return get_value(copy_positions, xpos, ypos) # Return the heuristic

	# Finds every empty spot on the board.
	empty_spots = []# Creates an array to hold empty spots
	for i in range(len(copy_positions)):	# Iterates through the passed board to find any empty spots
		for j in range(len(copy_positions[i])):
			if copy_positions[i][j] == 3:
				empty_spots.append(tuple([i, j]))	# Adds them
	#print("Empty Spot Found: ", empty_spots)
	
	if aiTurn_bool:	# If it would be the AI's turn..
		#print("AB, ai")
		value = (-sys.maxsize-1)	# Set the min value
		
		# GO through each possible move you can make..
		for move in empty_spots:
			#print("Move: ", move)
			# Make a new board to simulate each move
			new_positions = deepcopy(copy_positions)
			new_positions[move[0]][move[1]] = ai_turn	# Perform the move on the new board
			#for i in range(len(new_positions)):
			#	print(new_positions[i])
			#input("Enter to continue...")
			
			#print("Value going in: ", value)
			#value = max(value, alphabeta(new_positions, depth-1, alpha, beta, False, move[0], move[1])) # And recursively determine the value for that move chain
			temp = alphabeta(new_positions, depth-1, alpha, beta, False, move[0], move[1])
			if temp > value:
				#print(temp, value)
				global last_move 
				last_move = (move[0], move[1])
				#print("LM Updated: ", last_move)
				value = temp
			#print("Value coming out: ", value)
			#input("Enter to continue . . . . . ")
			#print(alpha, beta)
			alpha = max(alpha, value)	# IF it's better than what has been found, make it the new alpha
			
			if (alpha >= beta):	# If we're beating the player's best move, break immediately.
				break
		return value
	else:	# If it would be the player's turn
		#print("AB, player")
		value = sys.maxsize	# Set value above what is possible on the board
		
		# GO through each possible move you can make..
		for move in empty_spots:
			#print("Move: ", move)
			# Make a new board to simulate each move
			new_positions = deepcopy(copy_positions)
			new_positions[move[0]][move[1]] = (ai_turn+1)%2	# Perform the move on the new board
			#for i in range(len(new_positions)):
			#	print(new_positions[i])
			#input("Enter to continue...")
			
			#print("Value going in: ", value)
			value = min(value, alphabeta(new_positions, depth-1, alpha, beta, True, move[0], move[1]))
			#print("Value coming out: ", value)
			#input("Enter to continue . . . . . ")
			beta = min(beta, value)
			
			if (beta <= alpha):
				break
		return value
	
# Have to make it general between AI score and player score
def get_value(board, xpos, ypos):
	combined_Score = 0
	
	copy_board = deepcopy(board)
	copy_board[xpos][ypos] = 3
	combined_Score += get_horizontalScore(copy_board, xpos, ypos)
	#print("H: ", combined_Score)
	combined_Score += get_verticalScore(copy_board, xpos, ypos)
	#print("V: ", combined_Score)
	combined_Score += get_diagonalScore(copy_board, xpos, ypos)
	#print("D: ", combined_Score)
	combined_Score += get_antiDiagonalScore(copy_board, xpos, ypos)
	#print("A: ", combined_Score)
	return combined_Score
	
def get_diagonalScore(board, xpos, ypos):
	diagonal = numpy.diagonal(board, ypos-xpos)
	length = len(diagonal)
	max_Score = 0
	score = 0
	row_pos = (xpos-ypos)
	if row_pos >= 0:
		abs_pos = xpos - (xpos-ypos)
	else:
		abs_pos = ypos - (ypos-xpos)
	for i in range(length):
		for j in range( min(length-i, 5) ):
			#print("Slide Diagonal")
			if diagonal[i+j] == ai_turn:
				#print("Diagonal: ", i, j)
				score += 1 + (2/ (abs(i+j-abs_pos) + 1))/NEARNESS_SCORE
			elif diagonal[i+j] == player_turn:
				score -= 1
		if max_Score < score:
			max_Score = score
		score = 0
	return max_Score**IN_A_ROW_SCORE
	
def get_antiDiagonalScore(board, xpos, ypos):	#Some issues giving 1 score on bottom left.
	anti_diagonal = numpy.diagonal(numpy.fliplr(board), 14-xpos-ypos)
	length = len(anti_diagonal)
	max_Score = 0
	score = 0
	row_pos = 14-xpos-ypos
	if row_pos >= 0:
		abs_pos = (4-xpos)-(4-xpos-ypos)
	else:
		abs_pos = ypos-(4-ypos-xpos)
	for i in range(length):
		for j in range( min(length-i, 5) ):
			#print("Slide Anti-Diagonal")
			if anti_diagonal[i+j] == ai_turn:
				#print("Anti-Diagonal: ", i, j)
				score += 1 + (2/ (abs(i+j-abs_pos) + 1))/NEARNESS_SCORE
			elif anti_diagonal[i+j] == player_turn:
				score -= 1
		if max_Score < score:
			max_Score = score
		score = 0
	return max_Score**IN_A_ROW_SCORE

def get_horizontalScore(board, xpos, ypos):
	lmax = max(0, xpos-4)
	rmax = min(14,xpos+4)
	max_Score = 0
	score = 0
	for i in range(lmax, rmax-4):
		for j in range(5):
			#print("Slide Horizontal")
			if board[i+j][ypos] == ai_turn:
				#print(i+j, ypos)
				score += 1 + (2 / (abs(i+j-xpos) + 1))/NEARNESS_SCORE # +1 point per piece. And an extra small amount for being close. This makes it like to place next to other pieces.
			elif board[i+j][ypos] == player_turn:
				score -= 1
		if max_Score < score:
			max_Score = score
		score = 0
	return max_Score**IN_A_ROW_SCORE
	
def get_verticalScore(board, xpos, ypos):
	umax = max(0, ypos-4)
	dmax = min(14,ypos+4)
	max_Score = 0
	score = 0
	for i in range(umax, dmax-4):
		for j in range(5):
			#print("Slide Vertical")
			if board[xpos][i+j] == ai_turn:
				#print(i+j, xpos)
				score += 1 + (2 / (abs(i+j-ypos) + 1))/NEARNESS_SCORE
			elif board[xpos][i+j] == player_turn:
				score -= 1
		if max_Score < score:
			max_Score = score
		score = 0
	return max_Score**1.3

while game_over == False: # Main game loop
	draw() # Draw everything first
	if turn_count%2 == player_turn:
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
	else:
		final_pos = gomoku_AI()
		#positions[final_pos[0]][final_pos[1]] = turn_count % 2
		turn_count += 1
		my_turn = True
	pygame.display.update() # Update all the info that might have changed.
    
# overflow bug at bottom right. +1 to far index?