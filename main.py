from constants import *
from mouse import *
from bot import *
import pygame as pg
import argparse

parser = argparse.ArgumentParser(prog='Chess Bot')
parser.add_argument('--mode', help="Select the mode, args are \"human-vs-human\", \"human-vs-bot\", and \"bot-vs-bot\"")
parser.add_argument('--color', help="Select what color you want to play, args are \"white\" and \"black\"")
parser.add_argument('--fen', help="Select the starting position of the game, this is an optional argument")
args = parser.parse_args()

if not (args.mode in ["human-vs-human", "human-vs-bot", "bot-vs-bot"]):
    raise ValueError("Please select human-vs-human, human-vs-bot, or bot-vs-bot")

if args.mode == "human-vs-bot" and not(args.color in ["white", "black"]):
    raise ValueError("Please select white or black")

class App():
    def __init__(self):
        pg.init()
        
        # constants
        self.player_color = args.color
        self.mode = args.mode

        # window
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()

        # class attributes
        self.board = chess.Board()
        self.mouse = Mouse(self)
        self.bot = ChessBot(self, search_depth = 10)

        # game information
        self.piece_to_promote_to = "q"

        # init stuff
        if args.fen != None: self.board.set_board_fen(args.fen)
        self.draw_board()

    def play_move(self, move):
        self.board.push_san(move)
        if self.board.is_game_over():
            if self.board.turn: print("BLACK WINS")
            else:               print("WHITE WINS")

            exit()

    def make_move(self, move, first_square, second_square, piece):
        
        # if the move is irregular like an en passant or castling then the whole board needs to be redrawn
        if self.board.is_en_passant(chess.Move.from_uci(move)) or self.board.is_castling(chess.Move.from_uci(move)) or chess.Move.from_uci(move).promotion != None:
            self.play_move(move)
            self.draw_board()
            pg.display.update()
            return

        self.play_move(move)

        # if the move is a normal move you can get away with redrawing only the tiles that were moved since
        # there is no need to redraw the whole board...
        if self.mouse.last_selected != None: self.draw_tile(self.mouse.last_selected, outline=HIGHLIGHT_THICKNESS)
        self.draw_tile(first_square)
        self.draw_tile(second_square)
        self.draw_tile(second_square, color=LAST_MOVE_HIGHLIGHT, outline=HIGHLIGHT_THICKNESS)
        self.draw_piece(second_square, piece)

        # update the screen
        pg.display.update()

    def draw_piece(self, coordinates, piece_string):
        key = {"K": 0, "P": 1, "N": 2, "B": 3, "R": 4, "Q": 5, "k": 6, "p": 7, "n": 8, "b": 9, "r": 10, "q": 11}

        if self.player_color == "black":
            coordinates = (7 - coordinates[0], 7 - coordinates[1])


        self.screen.blit(pieces[key[piece_string]], (
                    coordinates[0]*TILESIZE,
                    coordinates[1]*TILESIZE
                ))

    def draw_tile(self, coordinates, color=None, outline=0):
        if self.player_color == "black":
            coordinates = (7 - coordinates[0], 7 - coordinates[1])
        
        if color == None:
            if (coordinates[0] + coordinates[1]) % 2 == 0: 
                color = COLOR1
            else:
                color = COLOR2

        pg.draw.rect(self.screen, color, (coordinates[0]*TILESIZE, coordinates[1]*TILESIZE, TILESIZE, TILESIZE), outline)

    def draw_board(self):
        # draw tiles a bunch of times
        for rank in range(8):
            for file in range(8):
                self.draw_tile((rank, file))
        

        for rank, row in enumerate(str(self.board).splitlines()):
            for file, tile in enumerate(row.split(' ')):
                if tile == ".": continue

                self.draw_piece((file, rank), tile)
        
        pg.display.update()

    def handle_events(self):
        # exit pygame is the window is closed
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                piece_at_square = str(self.board.piece_at(self.mouse.square))

                if self.mode == "human-vs-bot":
                    # if this is the first selection
                    if self.mouse.selected == None:
                        # only select if it is a friendly piece
                        if ((self.player_color == "white" and piece_at_square.isupper()) or (self.player_color == "black" and piece_at_square.islower())):
                            self.mouse.process_lmb(self.board, piece_at_square)

                    # if this is the second selection (a move is being played or the player is deselecting their piece)
                    else:
                        self.mouse.process_lmb(self.board, piece_at_square)
                
                elif self.mode == "human-vs-human":
                    if self.mouse.selected != None:
                        self.mouse.process_lmb(self.board, piece_at_square)
                    else:
                        # only let the player select movable pieces
                        if (self.board.turn and piece_at_square.isupper()) or (not self.board.turn and piece_at_square.islower()):
                            self.mouse.process_lmb(self.board, piece_at_square)
                
                # the mode "bot-vs-bot" doesn't allow for user input
            
            if event.type == pg.KEYDOWN:
                # undo moves if there are moves to undo and this is not bot vs bot
                if event.key == pg.K_z and self.board.move_stack != [] and self.mode != "bot-vs-bot":
                    # need to undo the bots move as well so undo 1 extra move
                    if self.mode == "human-vs-bot":
                        self.board.pop()
                        
                    self.board.pop()
                    self.mouse.last_selected = None
                    self.draw_board()
                
                # promotions
                if event.key == pg.K_q: self.piece_to_promote_to = "q"
                if event.key == pg.K_r: self.piece_to_promote_to = "r"
                if event.key == pg.K_k: self.piece_to_promote_to = "n"
                if event.key == pg.K_b: self.piece_to_promote_to = "b"

                if event.key == pg.K_e: print(f"Current Material Advantage: {self.bot.evaluate_board(self.board)}")

    def update(self):
        # player plays both sides
        if self.mode == "human-vs-human":
            self.mouse.update()

        elif self.mode == "human-vs-bot":
            # player's turn
            if (self.player_color == "white" and self.board.turn) or (self.player_color == "black" and not self.board.turn):
                self.mouse.update()

            # bots turn
            else:
                is_playing_white = (self.player_color != "white")       # bot plays opposite color
                move_object = self.bot.get_best_move(self.board, is_playing_white)

                piece = str(self.board.piece_at(move_object.from_square))
                first_square = self.mouse.square_to_coord(move_object.from_square)
                second_square = self.mouse.square_to_coord(move_object.to_square)

                self.make_move(str(move_object), first_square, second_square, piece)
                self.mouse.last_selected = second_square

        # bot plays both sides
        elif self.mode == "bot-vs-bot":
            if self.board.turn: is_playing_white = True
            else:               is_playing_white = False
            
            move_object = self.bot.get_best_move(self.board, is_playing_white)

            piece = str(self.board.piece_at(move_object.from_square))
            first_square = self.mouse.square_to_coord(move_object.from_square)
            second_square = self.mouse.square_to_coord(move_object.to_square)

            self.make_move(str(move_object), first_square, second_square, piece)
            self.mouse.last_selected = second_square

    def run(self):

        while True:
            self.handle_events()
            self.update()
            self.clock.tick(FPS)
            pg.display.set_caption(f"CHESS GAME LOL AND YES THIS IS MADE BY PHONG                      FPS: {str(round(self.clock.get_fps(), 2))}")

if __name__ == '__main__':
    app = App()
    app.run()