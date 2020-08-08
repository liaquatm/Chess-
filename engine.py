class GameState():
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingPos = (7, 4)
        self.blackKingPos = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    def makeMove(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.piece_moved == 'wK':
            self.whiteKingPos = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.blackKingPos = (move.end_row, move.end_col)

        if move.isPawnPromotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        if move.isEnpassantMove:
            self.board[move.start_row][move.end_col] = '--'
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row)==2:
            self.enpassantPossible = ((move.start_row+move.end_row)//2, move.end_col)
        else:
            self.enpassantPossible = ()

        if move.isCastleMove:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = '--'
            else:
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = '--'

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))


    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove
            if move.piece_moved == 'wK':
                self.whiteKingPos = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.blackKingPos = (move.start_row, move.start_col)
            if move.isEnpassantMove:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassantPossible = (move.end_row, move.end_col)
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassantPossible = ()

            self.castleRightsLog.pop()
            self.currentCastlingRights = self.castleRightsLog[-1]

            if move.isCastleMove:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = '--'
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

    def updateCastleRights(self, move):
        if move.piece_moved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.piece_moved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.currentCastlingRights.wqs = False
                elif move.start_col == 7:
                    self.currentCastlingRights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.currentCastlingRights.bqs = False
                elif move.start_col == 7:
                    self.currentCastlingRights.bks = False

    def getValidMoves(self):
        for log in self.castleRightsLog:
            print([log.wks, log.bks, log.wqs, log.bqs])
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingPos[0], self.whiteKingPos[1], moves)
        else:
            self.getCastleMoves(self.blackKingPos[0], self.blackKingPos[1], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareCaptured(self.whiteKingPos[0], self.whiteKingPos[1])
        else:
            return self.squareCaptured(self.blackKingPos[0], self.blackKingPos[1])

    def squareCaptured(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if r > 0 and self.board[r - 1][c] == '--':
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantPossible = True))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantPossible = True))
        else:
            if r < 7 and self.board[r + 1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantPossible = True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantPossible = True))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                next_row = r + d[0] * i
                next_col = c + d[1] * i
                if 0 <= next_row < 8 and 0 <= next_col < 8:
                    next_piece = self.board[next_row][next_col]
                    if next_piece == '--':
                        moves.append(Move((r, c), (next_row, next_col), self.board))
                    elif next_piece[0] == enemy:
                        moves.append(Move((r, c), (next_row, next_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (1, 1), (1, -1), (-1, 1))
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                next_row = r + d[0] * i
                next_col = c + d[1] * i
                if 0 <= next_row < 8 and 0 <= next_col < 8:
                    next_piece = self.board[next_row][next_col]
                    if next_piece == '--':
                        moves.append(Move((r, c), (next_row, next_col), self.board))
                    elif next_piece[0] == enemy:
                        moves.append(Move((r, c), (next_row, next_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        directions = ((-1, -2), (-1, 2), (-2, -1), (-2, 1), (1, -2), (1, 2), (2, -1), (2, 1))
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:
            next_row = r + d[0]
            next_col = c + d[1]
            if 0 <= next_row < 8 and 0 <= next_col < 8:
                next_piece = self.board[next_row][next_col]
                if next_piece == '--':
                    moves.append(Move((r, c), (next_row, next_col), self.board))
                elif next_piece[0] == enemy:
                    moves.append(Move((r, c), (next_row, next_col), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        directions = ((-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1), (1, 0), (1, -1), (1, 1))
        enemy = 'b' if self.whiteToMove else 'w'
        for i in range(8):
            next_row = r + directions[i][0]
            next_col = c + directions[i][1]
            if 0 <= next_row < 8 and 0 <= next_col < 8:
                next_piece = self.board[next_row][next_col]
                if next_piece == '--':
                    moves.append(Move((r, c), (next_row, next_col), self.board))
                elif next_piece[0] == enemy:
                    moves.append(Move((r, c), (next_row, next_col), self.board))


    def getCastleMoves(self, r, c, moves):
        if self.squareCaptured(r,c):
            return

        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)
    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareCaptured(r, c+1) and not self.squareCaptured(r, c+2):
                moves.append(Move((r,c), (r, c+2), self.board, isCastleMove = True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareCaptured(r, c-1) and not self.squareCaptured(r, c-2):
                moves.append(Move((r,c), (r, c-2), self.board, isCastleMove = True))



class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs



class Move:
    rankstorows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowstoranks = {v: k for k, v in rankstorows.items()}
    colstofiles = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    filestocols = {v: k for k, v in colstofiles.items()}

    def __init__(self, start_sq, end_sq, board, isEnpassantPossible = False, isCastleMove = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.isPawnPromotion = False
        if (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7):
            self.isPawnPromotion = True
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

        self.isEnpassantMove = isEnpassantPossible
        if self.isEnpassantMove:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        self.isCastleMove = isCastleMove

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def getChessNotation(self):
        return self.getRankFile(self.start_row, self.start_col) + self.getRankFile(self.end_row, self.end_col)

    def getRankFile(self, r, c):
        return self.colstofiles[c] + self.rowstoranks[r]
