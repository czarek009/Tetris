import pygame
import random
from copy import deepcopy
import pickle
import os


class Piece:

	def __init__(self, x, y, shape):

		self.x = x
		self.y = y
		self.id = shape

		if shape == 'O':
			self.color = (255, 255, 0)
			self.w = 2
			self.h = 2
			self.shape = [[1, 1],
										[1, 1]]
		elif shape == 'T':
			self.color = (255, 0, 255)
			self.w = 3
			self.h = 2
			self.shape = [[1, 1, 1],
										[0, 1, 0]]
		elif shape == 'I':
			self.color = (0, 0, 255)
			self.w = 4
			self.h = 1
			self.shape = [[1, 1, 1, 1]]
		elif shape == 'L':
			self.color = (255, 128, 0)
			self.w = 3
			self.h = 2
			self.shape = [[0, 0, 1],
										[1, 1, 1]]
		elif shape == 'J':
			self.color = (0, 255, 255)
			self.w = 3
			self.h = 2
			self.shape = [[1, 0, 0],
										[1, 1, 1]]
		elif shape == 'Z':
			self.color = (0, 255, 0)
			self.w = 3
			self.h = 2
			self.shape = [[1, 1, 0],
										[0, 1, 1]]
		elif shape == 'S':
			self.color = (128, 64, 192)
			self.w = 3
			self.h = 2
			self.shape = [[0, 1, 1],
										[1, 1, 0]]
		else:
			self.color = (192, 192, 192)
			self.w = 1
			self.h = 1
			self.shape = [[1]]

	def __str__(self):
		out = "x: " + str(self.x) + ", y: " + str(self.y) + ", w: " + str(self.w) + ", h: " + str(self.h)
		print("x:",self.x)
		print("y:",self.y)
		print("w:",self.w)
		print("h:",self.h)
		print(self.shape)
		return out

	def rotate(self):
		self.w, self.h = self.h, self.w
		new_shape = [[self.shape[j][i] for j in range(len(self.shape))] for i in range(len(self.shape[0])-1,-1,-1)]
		self.shape = new_shape


class Tetris:

	SPEED       = 250
	BLOCK_SIZE  = 60
	COLS_N      = 10
	ROWS_N      = 20
	PADDING     = BLOCK_SIZE + 30
	RIGHT_BAR   = 5*BLOCK_SIZE
	GRID_WIDTH  = COLS_N * BLOCK_SIZE
	GRID_HEIGHT = ROWS_N * BLOCK_SIZE
	WIN_WIDTH   = GRID_WIDTH + 3*PADDING + RIGHT_BAR
	WIN_HEIGHT  = GRID_HEIGHT + 2*PADDING
	SHAPES      = ['I', 'T', 'O', 'L', 'J', 'S', 'Z']
	BACKGROUND_COLOR = (48, 48, 96)
	BORDER_COLOR     = (32, 32, 64)
	GRID_COLOR       = (128, 128, 128)
	TEXT_COLOR       = (200, 200, 200)
	SCORES_FILE = 'high_scores.pickle'

	def __init__(self):

		pygame.font.init()
		pygame.display.set_caption('TETRIS')
		self.myfont = pygame.font.SysFont('default', self.BLOCK_SIZE)
		self.window = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
		self.board  = [[(0, 0, 0) for _ in range(self.COLS_N)] for _ in range(self.ROWS_N)]
		self.score  = 0
		self.mult   = 1.0
		
		if os.path.isfile(self.SCORES_FILE):
			with open(self.SCORES_FILE, "rb") as file:
				self.high_scores = pickle.load(file)
		else:
			self.high_scores = []

		self.high_scores.sort(key = lambda e: e[1], reverse = True)
		print(self.high_scores)

	def start_game(self):
		'''
		Execute main loop
		'''
		clock       = pygame.time.Clock()
		fall_speed  = self.SPEED
		fall_time   = 0
		input_speed = 100
		input_time  = 0
		running     = True
		piece       = Piece(4, 0, random.choice(self.SHAPES))
		next_piece  = Piece(4, 0, random.choice(self.SHAPES))

		while running:

			self.draw_board(piece, next_piece)
			
			# Move piece down
			fall_time  += clock.get_rawtime()
			input_time += clock.get_rawtime()
			clock.tick()
			if fall_time >= fall_speed:
				fall_time = 0
				if self.can_fall(piece):
					piece.y += 1
				else:
					self.add_piece2board(piece)
					self.clear_row()
					if self.game_over():
						running = False
						self.save_score()
						break
					fall_speed *= .99
					self.mult *= 1.01

					piece = next_piece
					next_piece = Piece(4, 0, random.choice(self.SHAPES))

			# Keyboard input
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

				if event.type == pygame.KEYDOWN:

					if event.key == pygame.K_UP:
						if self.can_rotate(piece, 'right'):
							piece.rotate()
							piece.rotate()
							piece.rotate()

					if event.key == pygame.K_DOWN: # left
						if self.can_rotate(piece, 'left'):
							piece.rotate()

					if event.key == pygame.K_SPACE:
						while self.can_fall(piece):
							self.score = int(self.score + 10 * self.mult)
							piece.y += 1

					if event.key == pygame.K_ESCAPE:
						running = False
			
			if input_time >= input_speed:
				input_time = 0
				keys = pygame.key.get_pressed()
				if keys[pygame.K_LEFT]:
					if self.can_move_left(piece):
						piece.x -= 1
				if keys[pygame.K_RIGHT]:
					if self.can_move_right(piece):
						piece.x += 1

		pygame.display.quit()
		quit()
	
	# ---------- LOGIC ---------- # 

	def add_piece2board(self, piece):
		'''
		Adds current piece to `self.board`. Returns nothing.

		Arguments:
		----------
		piece : piece to add
		'''
		for x in range(piece.w):
			for y in range(piece.h):
				if piece.shape[y][x] == 1:
					self.board[piece.y + y][piece.x + x] = piece.color

	def clear_row(self):
		'''
		Checks if there are any full rows to clear. If so, clears them and move higher elements down. Returns nothing.
		'''
		for i in range(self.ROWS_N):
			if all([x != (0, 0, 0) for x in self.board[i]]):
				self.board[i] = [(0, 0, 0) for _ in self.board[i]]
				for j in range(0, i):
					for k in range(self.COLS_N):
						self.board[i-j][k] = self.board[i-j-1][k]
				self.score = int(self.score + 1000 * self.mult)

	def game_over(self):
		'''
		Returns true if any block in the highest row is not empty. False otherwise.
		'''
		if any([x != (0, 0, 0) for x in self.board[0]]):
			return True
		return False

	def save_score(self):
		'''
		Ask player for name and save score. Then exit.
		'''
		big_font = pygame.font.SysFont('default', self.BLOCK_SIZE*2)
		text = big_font.render('GAME OVER', True, self.TEXT_COLOR)
		self.window.blit(text, 
						 (self.PADDING + (self.COLS_N*self.BLOCK_SIZE - text.get_width())//2, 
						  (self.WIN_HEIGHT - text.get_height())//2))


		running = True
		name = ''
		while running:

			self.tombstone(name)
			pygame.display.update()

			for event in pygame.event.get():

				if event.type == pygame.QUIT:
					exit(0)

				if event.type == pygame.KEYDOWN:

					if event.key == pygame.K_BACKSPACE:
						name = name[:-1]
					elif event.key == pygame.K_RETURN:
						running = False
					elif event.key == pygame.K_ESCAPE:
						exit(0)
					else:
						name += event.unicode

		self.high_scores.append((name, self.score))
		with open(self.SCORES_FILE, "wb") as file:
			pickle.dump(self.high_scores, file)

	# ----------- GUI ----------- #

	def draw_board(self, piece, next_piece):
		'''
		Draws all interface.
		'''
		self.window.fill(self.BACKGROUND_COLOR)

		# draw current piece
		for x in range(piece.w):
			for y in range(piece.h):
				if piece.shape[y][x] == 1:
					self.draw_block(piece.color, piece.x + x, piece.y + y)

		# draw static elements
		for x in range(self.COLS_N):
			for y in range(self.ROWS_N):
				if (self.board[y][x] != (0,0,0)):
					self.draw_block(self.board[y][x], x, y)

		self.draw_grid()
		self.draw_next_piece(next_piece)
		self.print_score()
		self.scoreboard()
		pygame.display.update()

	def draw_grid(self):
		# GRID
		B = self.PADDING

		for i in range(1, self.COLS_N):
			pygame.draw.line(self.window, 
							 self.GRID_COLOR, 
							 (B + i*self.BLOCK_SIZE, B), 
							 (B + i*self.BLOCK_SIZE, B + self.GRID_HEIGHT))

		for i in range(1, self.ROWS_N):
			pygame.draw.line(self.window, 
							 self.GRID_COLOR, 
							 (B, B + i*self.BLOCK_SIZE), 
							 (B + self.GRID_WIDTH, B + i*self.BLOCK_SIZE))

		# BORDER
		pygame.draw.rect(self.window,
						 self.BORDER_COLOR,
						 (B, B, self.GRID_WIDTH+4, self.GRID_HEIGHT+4),
						 4)
		
	def draw_next_piece(self, piece):
		'''
		Shows box with next piece.
		'''
		text = self.myfont.render('NEXT PIECE:', True, self.TEXT_COLOR)
		self.window.blit(text, 
						 (2*self.PADDING + self.BLOCK_SIZE*self.COLS_N + int(.45*self.BLOCK_SIZE), 
						 self.PADDING + int(.2*self.BLOCK_SIZE)))

		shape = piece.id
		color = piece.color

		# kawałek brzydkiego kodu, żeby każdy element rysował się wyśrodkowany
		if piece.w%2 == 1:
			bx = 2*self.PADDING + self.BLOCK_SIZE*self.COLS_N + self.BLOCK_SIZE
			by = 2*self.PADDING + self.BLOCK_SIZE
		else:
			if shape == 'O':
				bx = 2*self.PADDING + self.BLOCK_SIZE*self.COLS_N + int(1.5*self.BLOCK_SIZE)
				by = 2*self.PADDING + self.BLOCK_SIZE
			elif shape == 'I':
				bx = 2*self.PADDING + self.BLOCK_SIZE*self.COLS_N + int(.5*self.BLOCK_SIZE)
				by = 2*self.PADDING + int(1.5*self.BLOCK_SIZE)

		y = by
		x = bx
		for j in range(piece.h):
			for i in range(piece.w):
				if piece.shape[j][i] != 0:
					pygame.draw.rect(self.window, color, (x, y, self.BLOCK_SIZE, self.BLOCK_SIZE), 0)
				x += self.BLOCK_SIZE
			y += self.BLOCK_SIZE
			x = bx

		# box
		pygame.draw.rect(self.window,
						 self.BORDER_COLOR,
						 (2*self.PADDING + self.COLS_N*self.BLOCK_SIZE, self.PADDING + self.BLOCK_SIZE, 
						  5*self.BLOCK_SIZE, 4*self.BLOCK_SIZE), 
						 4)

	def print_score(self):
		'''
		Shows your current score.
		'''
		self.window.blit(self.myfont.render('SCORE: ' + str(self.score), True, self.TEXT_COLOR), 
		                 (2*self.PADDING + self.BLOCK_SIZE*self.COLS_N, 
										  self.PADDING + 7*self.BLOCK_SIZE))

	def draw_block(self, color, x, y):
		'''
		Draws single block on board.

		Arguments:
		----------
		color : (R, G, B) color of the block
		x, y : coordinates of block on board grid
		'''
		x = self.PADDING + self.BLOCK_SIZE*x
		y = self.PADDING + self.BLOCK_SIZE*y
		pygame.draw.rect(self.window, 
						 color, 
						 (x, y, self.BLOCK_SIZE, self.BLOCK_SIZE), 
						 0)

	def tombstone(self, name):
		'''
		Draws textbox to type your name.
		'''
		w = self.BLOCK_SIZE*5
		h = self.BLOCK_SIZE*2
		x = self.COLS_N*self.BLOCK_SIZE + 2*self.PADDING
		y = 8*self.BLOCK_SIZE + self.PADDING
		pygame.draw.rect(self.window, 
						 (32, 32, 80), 
						 (x, y, w, h), 
						 0)
		text = self.myfont.render(name, True, self.TEXT_COLOR)
		self.window.blit(text, 
						 (x + w//2 - text.get_width()//2, 
						 y + h//2 - text.get_height()//2))

	def scoreboard(self):
		'''
		Shows best players.
		'''
		x = self.PADDING*2 + self.COLS_N*self.BLOCK_SIZE
		y = self.PADDING + self.BLOCK_SIZE*10
		pygame.draw.rect(self.window,
						 self.BORDER_COLOR,
						 (x,
						  y,
						  self.BLOCK_SIZE*5,
						  self.BLOCK_SIZE*10),
						 4)
		
		for s in self.high_scores[:10]:
			text = self.myfont.render(s[0] + ": " + str(s[1]), True, self.TEXT_COLOR)
			self.window.blit(text, 
							 (x + 4, 
							  y + (self.BLOCK_SIZE - text.get_height())//2))
			y += self.BLOCK_SIZE

	# ----- KEYBOARD  INPUT ----- #

	def can_fall(self, piece):
		'''
		Returns True if piece can move one position down. False otherwise.
		'''
		for x in range(piece.w):
			for y in range(piece.h):
				if piece.y + piece.h >= self.ROWS_N:
					return False
				if piece.shape[y][x] == 1:
					if self.board[piece.y+y+1][piece.x+x] != (0, 0, 0):
						return False

		return True

	def can_move_left(self, piece):
		'''
		Returns True if piece can move one position left. False otherwise.
		'''
		for x in range(piece.w):
			for y in range(piece.h):
				if piece.x == 0:
					return False
				if piece.shape[y][x] == 1:
					if self.board[piece.y+y][piece.x+x-1] != (0, 0, 0):
						return False

		return True

	def can_move_right(self, piece):
		'''
		Returns True if piece can move one position right. False otherwise.
		'''
		for x in range(piece.w):
			for y in range(piece.h):
				if piece.x + piece.w >= self.COLS_N:
					return False
				if piece.shape[y][x] == 1:
					if self.board[piece.y+y][piece.x+x+1] != (0, 0, 0):
						return False

		return True

	def can_rotate(self, piece, direction):
		'''
		Checks if piece can rotate in given direction.

		Arguments:
		----------
		piece : current piece
		direction : 'right' (clockwise) or 'left' (counterclockwise)

		Returns:
		--------
		True if piece can rotate. False otherwise.
		'''		
		dc_piece = deepcopy(piece)
		if direction == 'left':
			dc_piece.rotate()
		elif direction == 'right':
			dc_piece.rotate()
			dc_piece.rotate()
			dc_piece.rotate()

		x = dc_piece.x
		y = dc_piece.y

		if x + dc_piece.w > self.COLS_N:
			return False
		if y + dc_piece.h > self.ROWS_N:
			return False

		for i in range(dc_piece.w):
			for j in range(dc_piece.h):
				if dc_piece.shape[j][i] == 1 and self.board[y+j][x+i] != (0, 0, 0):
					return False

		return True


if __name__ == "__main__":

	Game = Tetris()
	Game.start_game()
