import chess, time, random, os

class ChessBot():
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }

    def __init__(self, app, search_depth):
        self.app = app
        self.search_depth = search_depth
        self.transposition_table = {}

    def evaluate_board(self, board):
        if board.is_checkmate():
            if board.turn: return float('-inf')
            else:          return float('inf')

        score = 0

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                piece_value = self.piece_values.get(piece.piece_type, 0)
                score += piece_value if piece.color == chess.WHITE else -piece_value

        return score
        
    def mvv_lva_ordering(self, board):
        return sorted(board.legal_moves, key=lambda move: self.piece_values.get(board.piece_type_at(move.to_square), 0), reverse=True)

    def alphabeta(self, board, depth, alpha, beta, maximizing):
        # if this position has already been reached then return
        fen_key = board.fen()
        if fen_key in self.transposition_table:
            return self.transposition_table[fen_key]

        # if this is a leaf node then return the value
        if depth <= 0:
            return self.evaluate_board(board)

        # debug
        self.searched_nodes += 1

        if maximizing:
            best_score = float('-inf')
            for move in self.mvv_lva_ordering(board):
                copy = board.copy()
                copy.push(move)

                if not board.is_capture(move):
                    depth -= 1

                score = self.alphabeta(copy, depth - 1, alpha, beta, False)
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)

                if beta <= alpha:
                    break
            
            return best_score
        else:
            best_score = float('inf')
            for move in self.mvv_lva_ordering(board):
                copy = board.copy()
                copy.push(move)

                if not board.is_capture(move):
                    depth -= 1

                score = self.alphabeta(copy, depth - 1, alpha, beta, True)
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            
            self.transposition_table[fen_key] = best_score
            return best_score

    def get_best_move(self, board, maximizing):

        # debug values
        start_time = time.time()
        self.searched_nodes = 0

        # algorithm values
        best_move  = None
        best_score = float('-inf') if maximizing else float(' inf')
        alpha      = float(' inf') if maximizing else float('-inf')
        beta       = float('-inf') if maximizing else float(' inf')
        self.transposition_table.clear()

        # loop through every possible move
        for i, move in enumerate(self.mvv_lva_ordering(board)):
            # debug
            os.system('clear')
            print(f"Calculating... {i+1}/{len(list(board.legal_moves))}")

            # play the move
            copy = board.copy()
            copy.push(move)

            # evaluate that move, if this is a better move than the currently saved move then save it
            score = self.alphabeta(copy, self.search_depth - 1, alpha, beta, not maximizing)
            if (maximizing and (score > best_score)) or (not maximizing and (score < best_score)):
                best_score = score
                best_move = move

        # if the bot cannot escape checkmate it returns no best move, so this catches that error
        if best_move == None:
            if board.legal_moves != []:
                return random.choice(list(board.legal_moves))
            exit()

        # debug
        print(f"Time Elapsed: {round(time.time() - start_time, 2)}, Searched Nodes: {self.searched_nodes}, Best Eval: {best_score}")
        
        return best_move