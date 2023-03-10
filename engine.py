"""
this file is responsible for storing the current board + valid moves
"""
class CurrentBoard():
    def __init__(self):
        #8x8 board; 1st char is color, 2nd is piece type
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],]
        self.movePieces = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
        'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.moveLog = []
        self.whiteMove = True
        self.WKLocation = (7, 4)
        self.BKLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()  #coordinates for possible en passant after moving pawn two squares
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]


    #takes a move as a parameter and executes it
    def move(self, move):
        self.board[move.row1][move.col1] = "--"
        self.board[move.row2][move.col2] = move.pieceMoved
        self.moveLog.append(move) #keep track of moves
        self.whiteMove = not self.whiteMove
        if move.pieceMoved == "wK":
            self.WKLocation = (move.row2, move.col2)
        elif move.pieceMoved == "bK":
            self.BKLocation = (move.row2, move.col2)


        #pawn promo
        if move.isPawnPromotion:
            self.board[move.row2][move.col2] = move.pieceMoved[0] + 'Q'

        #en passant
        if move.isEnpassantMove:
            self.board[move.row1][move.col2] = "--"  #capture the pawn in en passant

        #update en passant possible
        if move.pieceMoved[1] == 'p' and abs(move.row1 - move.row2) == 2:  #when pawn moves twice
            self.enpassantPossible = ((move.row1 + move.row2) // 2, move.col1)
        else:
            self.enpassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.col2 - move.col1 == 2:  #kingside castle
                self.board[move.row2][move.col2 - 1] = self.board[move.row2][move.col2 + 1]  #moves rook
                self.board[move.row2][move.col2 + 1] = "--"  #erase old rook
            else:  #queenside castle
                self.board[move.row2][move.col2 + 1] = self.board[move.row2][move.col2 - 2]  #moves rook
                self.board[move.row2][move.col2 - 2] = "--"  #erase old rook

        self.enpassantPossibleLog.append(self.enpassantPossible)

       #update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

    """
    Undo last move
    """
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.row1][move.col1] = move.pieceMoved
            self.board[move.row2][move.col2] = move.pieceCaptured
            self.whiteMove = not self.whiteMove
            if move.pieceMoved == "wK":
                self.WKLocation = (move.row1, move.col1)
            elif move.pieceMoved == "bK":
                self.BKLocation = (move.row1, move.col1)
            #undo enpassant
            if move.isEnpassantMove:
                self.board[move.row2][move.col2] = "--" #leave landing square blank
                self.board[move.row1][move.col2] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]


            #undo castling rights
            self.castleRightsLog.pop()  #get rid of newest castle rights
            newRights =  self.castleRightsLog[-1]  #set current to last element
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            #undo castle move
            if move.isCastleMove:
                if move.col2 - move.col1 == 2:  #kingside
                    self.board[move.row2][move.col2 + 1] = self.board[move.row2][move.col2 - 1]
                    self.board[move.row2][move.col2 - 1] = "--"
                else:  #queenside
                    self.board[move.row2][move.col2 - 2] = self.board[move.row2][move.col2 + 1]
                    self.board[move.row2][move.col2 + 1] = "--"

            self.checkmate = False
            self.stalemate = False
    """
    Update the castling rights
    """

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "wR":
            if move.row1 == 7:
                if move.col1 == 0:  #left white rook
                    self.currentCastlingRights.wqs = False
                elif move.col1 == 7:  #right
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.row1 == 0:
                if move.col1 == 0:  #left black rook
                    self.currentCastlingRights.bqs = False
                elif move.col1 == 7:  #right
                    self.currentCastlingRights.bks = False

        #if rook captured before moving off starting square
        if move.pieceCaptured == "wR":
            if move.row2 == 7:
                if move.col2 == 0:
                    self.currentCastlingRights.wqs = False
                elif move.col2 == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.row2 == 0:
                if move.col2 == 0:
                    self.currentCastlingRights.bqs = False
                elif move.col2 == 7:
                    self.currentCastlingRights.bks = False


    """     
    All moves considering checks
    """
    def getValidMoves(self):
        # NAIVE ALGORITHM: see if all possible moves lead to check
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        moves = self.getAllPossibleMoves()
        if self.whiteMove:
            self.getCastleMoves(self.WKLocation[0], self.WKLocation[1], moves)
        else:
            self.getCastleMoves(self.BKLocation[0], self.BKLocation[1], moves)
        for i in range(len(moves)-1, -1, -1):
            self.move(moves[i])
            self.whiteMove = not self.whiteMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteMove = not self.whiteMove
            self.undoMove()
        if len(moves) == 0: #check for checkmate or stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights

        return moves



    #determine if player in check
    def inCheck(self):
        if self.whiteMove:
            return self.isAttacked(self.WKLocation[0], self.WKLocation[1])
        else:
            return self.isAttacked(self.BKLocation[0], self.BKLocation[1])


    #determine if square under attack
    def isAttacked(self, r, c):
        self.whiteMove = not self.whiteMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteMove = not self.whiteMove  #fix turn order
        for move in oppMoves:
            if move.row2 == r and move.col2 == c:  #piece under attack
                return True
        return False

    """
    All moves without thinking about checks
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #rows
            for c in range(len(self.board[r])): #columns
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteMove) or (turn == 'b' and not self.whiteMove):
                    piece = self.board[r][c][1]
                    self.movePieces[piece](r, c, moves)
        return moves
    """
    generate all pawn moves
    """
    def getPawnMoves(self, r, c, moves):
        if self.whiteMove:  #white pawn moves
            if self.board[r-1][c] == "--":  #square in front of pawn is empty
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:  #left captures
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7:  #right captures
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))

        else:  #black pawn moves
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:  #left capture
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if c+1 <= 7:  #right capture
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))






    """
    generate rook moves
    """
    def getRookMoves(self, r, c, moves):

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  #empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  #valid to capture enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  #friendly piece cannot be captured
                        break
                else:  # off the board
                    break



    #generate knight moves
    def getKnightMoves(self, r, c, moves):
        knight_squares = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.whiteMove else 'b'
        for m in knight_squares:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != ally_color:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    #generate bishop moves
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.whiteMove else 'w'
        for d in directions:
            for i in range(1, 8): #moves a max of seven squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  #empty space
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemy_color:  #valid to capture enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  #friendly piece cannot be captured
                        break
                else:  # off the board
                    break

    #generate queen moves
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    #generate king moves
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteMove else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
    """
    Generate all castling moves
    """
    def getCastleMoves(self, r, c, moves):
        if self.isAttacked(r, c):
            return  #never can castle while in check
        if (self.whiteMove and self.currentCastlingRights.wks) or (not self.whiteMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteMove and self.currentCastlingRights.wqs) or (not self.whiteMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.isAttacked(r, c + 1) and not self.isAttacked(r, c + 2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.isAttacked(r, c - 1) and not self.isAttacked(r, c - 2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3,
                   "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.row1 = startSq[0]
        self.col1 = startSq[1]
        self.row2 = endSq[0]
        self.col2 = endSq[1]
        self.pieceMoved = board[self.row1][self.col1]
        self.pieceCaptured = board[self.row2][self.col2]
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.row2 == 0) or (self.pieceMoved == "bp" and self.row2 == 7)
        self.isEnpassantMove = isEnpassantMove

        #en passant
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"

        #castling
        self.isCastleMove = isCastleMove

        self.isCapture = self.pieceCaptured != "--"
        self.moveID = self.row1 * 1000 + self.col1 * 100 + self.row2 * 10 + self.col2

    """
    Overriding the equals operator
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):

        return self.getRankFile(self.row1, self.col1) + self.getRankFile(self.row2, self.col2)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    #overriding the str() function
    def __str__(self):
        moveString = ""
        #castle
        if self.isCastleMove:
            return "O-O" if self.col2 == 6 else "O-O-O"

        endSquare = self.getRankFile(self.row2, self.col2)
        #pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                 moveString += self.colsToFiles[self.col1] + "x" + endSquare
            else:
                moveString += endSquare

            #pawn promotions
            if self.isPawnPromotion:
                moveString += "=Q"
            return moveString


        #piece moves other than pawn
        moveString = self.pieceMoved[1]


        if self.isCapture:
                moveString += 'x'




        return moveString + endSquare