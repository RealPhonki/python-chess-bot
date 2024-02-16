# external imports
import chess
import os

# local imports
from eval_config import piece_values, square_table

class ChessBot:
    def __init__(self, color: chess.Color) -> None:
        self.SEARCH_DEPTH = 4
        self.COLOR = color

    def evaluate(self, board: chess.Board) -> float:
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return float("-inf")
            if board.turn == chess.BLACK:
                return float("inf")
        
        white_material = 0
        black_material = 0

        # loop through every square in the board
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece:
                continue
            # get the piece value
            piece_value = piece_values[piece.piece_type]

            # get the piece positional value
            row, col = chess.square_rank(square), chess.square_file(square)
            flipped_square = chess.square(col, 7 - row)
            lookup_square = square if piece.color == chess.BLACK else flipped_square
            positional_value = square_table[piece.piece_type][lookup_square]

            # add material to total
            if piece.color == chess.WHITE:
                white_material += piece_value + positional_value
            else:
                black_material += piece_value + positional_value

        return round(white_material - black_material, 2)

    def minimax(self, board: chess.Board, depth, alpha: float, beta: float) -> float:
        # check if a leaf node has been reached
        if depth == 0:
            self.leaf_nodes += 1
            return self.evaluate(board)

        # white to play
        if board.turn:
            # initialize search data
            best_evaluation = float("-inf")

            for move in board.legal_moves:
                # search sub tree and return the evaluation
                board.push(move)
                evaluation = self.minimax(board, depth - 1, alpha, beta)
                board.pop()

                # store the move if it is better than the old best move
                if evaluation > best_evaluation:
                    best_evaluation = evaluation
                    self.best_variation[self.SEARCH_DEPTH - depth] = board.san(move)
                
                # update alpha
                alpha = max(alpha, evaluation)

                # prune remaining branches
                if alpha >= beta:
                    break

        else:
            # initialize search data
            best_evaluation = float("inf")

            for move in board.legal_moves:
                # search sub tree and return the evaluation
                board.push(move)
                evaluation = self.minimax(board, depth - 1, alpha, beta)
                board.pop()

                # store the move if it is better than the old best move
                if evaluation < best_evaluation:
                    best_evaluation = evaluation
                    self.best_variation[self.SEARCH_DEPTH - depth] = board.san(move)

                # update beta
                beta = min(beta, evaluation)

                if alpha >= beta:
                    break

        return best_evaluation

    def get_best_move(self, board: chess.Board) -> chess.Move:
        # initialize search data, assume the bot is playing black
        self.leaf_nodes = 0
        self.best_variation = [None] * self.SEARCH_DEPTH
        best_move = None
        best_evaluation = float("inf")
        all_evaluations = []

        for iteration, move in enumerate(board.legal_moves):
            # search sub tree and return the evaluation
            board.push(move)
            evaluation = self.minimax(board, self.SEARCH_DEPTH - 1, alpha = float("-inf"), beta = float("inf"))
            board.pop()

            # debug
            all_evaluations.append([board.san(move), evaluation])
            os.system("clear")
            print(f"Searched {iteration+1}/{len(list(board.legal_moves))} moves")

            # store the move if it is better than the old best move
            if evaluation < best_evaluation:
                best_move = move
                best_evaluation = evaluation
                self.best_variation[0] = board.san(move)
        
        if best_move == None:
            return list(board.legal_moves)[0]

        # debug
        print("-"*16)
        print(f"Best evaluation: {best_evaluation}, Leaf nodes: {self.leaf_nodes}")
        
        print("Depth 0 evaluations: ", end="")
        for move, evaluation in all_evaluations:
            print(f"{move}: {evaluation}, ", end="")
        print()

        print("Best variation: ", end="")
        for move in self.best_variation:
            print(move, end=", ")
        print()

        return best_move

