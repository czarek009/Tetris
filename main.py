import pygame
import random
from copy import deepcopy
import pickle

class Piece:

	def __init__(self, x, y, shape, color):

		self.x = x
		self.y = y
		self.color = color
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
	PADDING     = BLOCK_SIZE
	COLS_N      = 10
	ROWS_N      = 20
	RIGHT_MENU  = 6*BLOCK_SIZE
	GRID_WIDTH  = COLS_N * BLOCK_SIZE
	GRID_HEIGHT = ROWS_N * BLOCK_SIZE
	WIN_WIDTH   = GRID_WIDTH + 2*PADDING + RIGHT_MENU
	WIN_HEIGHT  = GRID_HEIGHT + 2*PADDING
	SHAPES      = ['I', 'T', 'O', 'L', 'J', 'S', 'Z']
	BACKGROUND_COLOR = (48, 48, 96)

	def __init__(self):

		pygame.font.init()
		pygame.display.set_caption('TETRIS')
		self.myfont = pygame.font.SysFont('default', self.BLOCK_SIZE)
		self.window = pygame.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))
		self.board  = [[(0, 0, 0) for _ in range(self.COLS_N)] for _ in range(self.ROWS_N)]
		self.score  = 0
		self.mult   = 1.0

	def start_game(self):

		clock      = pygame.time.Clock()
		fall_speed = self.SPEED
		fall_time  = 0
		running    = True
		piece      = Piece(5, 0, random.choice(self.SHAPES), (0, 0, 0))
		next_piece = Piece(5, 0, random.choice(self.SHAPES), (0, 0, 0))

		while running:

			self.draw_board(piece, next_piece)
			
			# Move piece down
			fall_time += clock.get_rawtime()
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
						exit(0)
					fall_speed *= .99
					self.mult *= 1.01

					piece = next_piece
					next_piece = Piece(5, 0, random.choice(self.SHAPES), (0, 0, 0))

			# Keyboard input
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False

				if event.type == pygame.KEYDOWN:

					if event.key == pygame.K_LEFT:
						if self.can_move_left(piece):
							piece.x -= 1

					if event.key == pygame.K_RIGHT:
						if self.can_move_right(piece):
							piece.x += 1

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

		pygame.display.quit()
		quit()
	
	# ---------- LOGIC ---------- # 

	def add_piece2board(self, piece):

		for x in range(piece.w):
			for y in range(piece.h):
				if piece.shape[y][x] == 1:
					self.board[piece.y + y][piece.x + x] = piece.color

	def clear_row(self):

		for i in range(self.ROWS_N):
			if all([x != (0, 0, 0) for x in self.board[i]]):
				self.board[i] = [(0, 0, 0) for _ in self.board[i]]
				for j in range(0, i):
					for k in range(self.COLS_N):
						self.board[i-j][k] = self.board[i-j-1][k]
				self.score = int(self.score + 1000 * self.mult)

	def game_over(self):

		if any([x != (0, 0, 0) for x in self.board[0]]):
			return True

	def save_score(self):
		
		self.myfont2 = pygame.font.SysFont('default', self.BLOCK_SIZE*2)
		text = self.myfont2.render('GAME OVER', False, (255, 255, 255))
		self.window.blit(text, (self.PADDING + self.COLS_N//2*self.BLOCK_SIZE - text.get_width()//2, 
														self.WIN_HEIGHT//2 - text.get_height()//2))


		running = True
		name = ''
		while running:

			self.tombstone(name)

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

		print(name, "score:", self.score)	

	# ----------- GUI ----------- #

	def tombstone(self, name):

		w = self.BLOCK_SIZE*5
		h = self.BLOCK_SIZE*2
		x = self.COLS_N*self.BLOCK_SIZE + 2*self.PADDING
		y = self.BLOCK_SIZE*8 + 2*self.PADDING
		pygame.draw.rect(self.window, (32, 32, 80), (x, y, w, h), 0)

		#text = self.myfont.render('Score: ' + str(self.score), False, (200, 200, 200))
		#self.window.blit(text, (x + self.BLOCK_SIZE//2, y + self.BLOCK_SIZE//2))
		text = self.myfont.render(name, False, (200, 200, 200))
		self.window.blit(text, (x + self.BLOCK_SIZE//2, y + self.BLOCK_SIZE//2))


		pygame.display.update()

	def draw_board(self, piece, next_piece):
		
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
		pygame.display.update()

	def draw_block(self, color, x, y):
		
		ltx = self.PADDING + self.BLOCK_SIZE*x
		lty = self.PADDING + self.BLOCK_SIZE*y
		pygame.draw.rect(self.window, color, (ltx, lty, self.BLOCK_SIZE, self.BLOCK_SIZE), 0)

	def draw_grid(self):
		
		BORDER_COLOR = (32, 32, 64)
		GRID_COLOR = (128, 128, 128)
		B = self.PADDING
		# GRID
		x = B + self.BLOCK_SIZE
		y = B
		for i in range(self.COLS_N - 1):
			pygame.draw.line(self.window, GRID_COLOR, (x, y), (x, y+self.GRID_HEIGHT))
			x += self.BLOCK_SIZE
		x = B
		y = B + self.BLOCK_SIZE
		for i in range(self.ROWS_N - 1):
			pygame.draw.line(self.window, GRID_COLOR, (x, y), (x + self.GRID_WIDTH, y))
			y += self.BLOCK_SIZE

		# BORDER
		pygame.draw.line(self.window, BORDER_COLOR, (B, B), (B, B + self.GRID_HEIGHT), 4)
		pygame.draw.line(self.window, BORDER_COLOR, (B + self.GRID_WIDTH, B), (B + self.GRID_WIDTH, B + self.GRID_HEIGHT), 4)
		pygame.draw.line(self.window, BORDER_COLOR, (B, B), (B + self.GRID_WIDTH, B), 4)
		pygame.draw.line(self.window, BORDER_COLOR, (B, B + self.GRID_HEIGHT), (B + self.GRID_WIDTH, B + self.GRID_HEIGHT), 4)

	def draw_next_piece(self, piece):

		text = self.myfont.render('NEXT PIECE:', False, (200, 200, 200))
		self.window.blit(text, (2*self.PADDING + self.BLOCK_SIZE*self.COLS_N + int(.45*self.BLOCK_SIZE), self.PADDING + int(.2*self.BLOCK_SIZE)))

		shape = piece.id
		color = piece.color

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
				

		BORDER_COLOR = (32, 32, 64)
		GRID_COLOR = (128, 128, 128)

		
		# box
		pygame.draw.line(self.window, BORDER_COLOR, (2*self.PADDING + self.COLS_N*self.BLOCK_SIZE, self.PADDING + self.BLOCK_SIZE), 
																								(2*self.PADDING + self.COLS_N*self.BLOCK_SIZE, self.PADDING + 5*self.BLOCK_SIZE), 4)
		pygame.draw.line(self.window, BORDER_COLOR, (2*self.PADDING + self.COLS_N*self.BLOCK_SIZE + 5*self.BLOCK_SIZE, self.PADDING + self.BLOCK_SIZE), 
																								(2*self.PADDING + self.COLS_N*self.BLOCK_SIZE + 5*self.BLOCK_SIZE, self.PADDING + 5*self.BLOCK_SIZE), 4)
		pygame.draw.line(self.window, BORDER_COLOR, (2*self.PADDING + self.COLS_N*self.BLOCK_SIZE, self.PADDING + self.BLOCK_SIZE), 
																								(2*self.PADDING + self.COLS_N*self.BLOCK_SIZE + 5*self.BLOCK_SIZE, self.PADDING + self.BLOCK_SIZE), 4)
		pygame.draw.line(self.window, BORDER_COLOR, (2*self.PADDING + self.COLS_N*self.BLOCK_SIZE, self.PADDING + 5*self.BLOCK_SIZE), 
																								(2*self.PADDING + self.COLS_N*self.BLOCK_SIZE + 5*self.BLOCK_SIZE, self.PADDING + 5*self.BLOCK_SIZE), 4)

	def print_score(self):

		text = self.myfont.render('SCORE: ' + str(self.score), False, (200, 200, 200))
		self.window.blit(text, (2*self.PADDING + self.BLOCK_SIZE*self.COLS_N, self.PADDING + 7*self.BLOCK_SIZE))

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
