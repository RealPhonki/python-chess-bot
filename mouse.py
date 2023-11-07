from constants import *
import pygame as pg
import chess

class Mouse():
    def __init__(self, app):
        self.app = app
        self.screen = pg.display.get_surface()
        self.position = self.x, self.y = (0, 0)
        self.tileposition = self.tilex, self.tiley = (0, 0)
        self.square = 0
        self.last_selected = None
        self.selected = None
    
    def square_to_coord(self, square):
        return (square % 8, 7 - square // 8)

    def coord_to_square(self, coordinate):
        return coordinate[0] + (7 - coordinate[1]) * 8

    # convert tile to chess notation
    def coord_to_notation(self, tile):
        x_lookup = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
        y_lookup = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
        return x_lookup[tile[0]] + y_lookup[tile[1]]

    def select_square(self):
        self.selected = self.tileposition
        self.app.draw_tile(self.selected, color=SELECT_HIGHLIGHT, outline=HIGHLIGHT_THICKNESS)
        pg.display.update()

    def deselect_square(self):
        self.app.draw_tile(self.selected, outline=HIGHLIGHT_THICKNESS)
        self.selected = None
        pg.display.update()

    # select a square
    def process_lmb(self, board, piece_at_square):
        # if nothing is selected yet and you are selecting an actual piece:
        if self.selected == None and piece_at_square != "None":
            self.select_square()
        
        elif self.selected != None:
            # get the piece at the originally selected square for future reference
            piece_at_first_square = str(board.piece_at(self.coord_to_square(self.selected)))

            # if you are reselecting the same piece then deselect
            if self.selected == self.tileposition:
                self.deselect_square()
                return

            # if the new piece is a friendly piece then select that new piece
            if (piece_at_first_square.isupper() and piece_at_square.isupper()) or (piece_at_first_square.islower() and piece_at_square.islower()):
                self.deselect_square()
                self.process_lmb(board, piece_at_square)
                return
            
            # convert the coordinates of the first and last click to chess notation and pass it in as a move
            move = self.coord_to_notation(self.selected) + self.coord_to_notation(self.tileposition)

            # check for pawn promation: If true then append the promotion piece to the end of the move string
            if piece_at_first_square.lower() == "p" and (self.coord_to_notation(self.tileposition)[1] in ["0", "8"]):
                move = move + self.app.piece_to_promote_to

            if chess.Move.from_uci(move) in board.legal_moves:
                self.app.make_move(move, self.selected, self.tileposition, piece_at_first_square)
                self.last_selected = self.tileposition
                self.deselect_square()

    # update all of the information handled by the mouse
    def update(self):
        # flip mouse position if playing black
        if self.app.player_color == "black": self.position = self.x, self.y = WIDTH - pg.mouse.get_pos()[0], HEIGHT - pg.mouse.get_pos()[1]
        else:                         self.position = self.x, self.y = pg.mouse.get_pos()

        self.tileposition = self.tilex, self.tiley = int(self.x / TILESIZE), int(self.y / TILESIZE)
        self.square = self.coord_to_square(self.tileposition)