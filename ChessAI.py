import random as r
NPositionalRanking =   [
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]
                ]
QPositionalRanking =   [
                [1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 2, 4, 4, 4, 4, 2, 1],
                [1, 2, 4, 4, 4, 4, 2, 1],
                [1, 2, 4, 4, 4, 4, 2, 1],
                [1, 4, 4, 4, 4, 4, 2, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]
                ]
RPositionalRanking =    [
                [4, 3, 4, 4, 4, 4, 3, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 3, 4, 4, 4, 4, 3, 4]
                ]
wpPositionalRanking =   [
                    [10, 10, 10, 10, 10, 10, 10, 10],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [6, 6, 6, 6, 6, 6, 6, 6],
                    [4, 4, 4, 5, 5, 4, 4, 4],
                    [3, 3, 3, 4, 4, 3, 3, 3],
                    [2, 2, 2, 2, 2, 2, 2, 2],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0]
                    ]
bpPositionalRanking =   [
                    [0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [2, 2, 2, 2, 2, 2, 2, 2],
                    [3, 3, 3, 4, 4, 3, 3, 3],
                    [4, 4, 4, 5, 5, 4, 4, 4],
                    [6, 6, 6, 6, 6, 6, 6, 6],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [10, 10, 10, 10, 10, 10, 10, 10]
                    ]
BPositionalRanking =  [
                [2, 3, 4, 1, 1, 2, 3, 2],
                [3, 3, 3, 2, 2, 3, 3, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 3, 3, 2, 2, 3, 3, 3],
                [2, 3, 4, 1, 1, 2, 3, 2]
                ]

pieceScore = {'K': 0, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'p': 1}

piecePositionScores = {"N": NPositionalRanking, "Q": QPositionalRanking, "B": BPositionalRanking,
                       "R": RPositionalRanking, "bp": bpPositionalRanking, "wp": wpPositionalRanking}

CM = 1000  #define checkmate score
SM = 0  #define stalemate score
DEPTH = 4

#return random move
def findRandomMove(validMoves):
    return validMoves[r.randint(0, len(validMoves) - 1)]


#return best move based on greedy algorithm: minmax without recursion
def findBestMoveMinMaxNoRecursion(gs, validMoves):
    turnMultiplier = 1 if gs.whiteMove else -1
    opponentMinMaxScore = CM
    bestPlayerMove = None
    r.shuffle(validMoves)
    for playerMove in validMoves:
        gs.move(playerMove)
        opponentsMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentMaxScore = SM
        elif gs.checkmate:
            opponentMaxScore = -CM
        else:
            opponentMaxScore = -CM
            for opponentsMove in opponentsMoves:
                gs.move(opponentsMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CM
                elif gs.stalemate:
                    score = SM
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove


"""
Helper method for recursion
"""
def findBestMove(gs, validMoves, returnQueue):
    global nextMove, counter
    nextMove = None
    r.shuffle(validMoves)
    counter = 0
    #findMoveNegaMax(gs, validMoves, DEPTH, gs.whiteToMove)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CM, CM, 1 if gs.whiteMove else -1)
    print(counter)
    returnQueue.put(nextMove)

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)

    if whiteToMove:
        maxScore = -CM
        for move in validMoves:
            gs.move(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        minScore = CM
        for move in validMoves:
            gs.move(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CM
    for move in validMoves:
        gs.move(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    #move ordering - prioritize checks and captures
    maxScore = -CM
    for move in validMoves:
        gs.move(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(move, score)
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

"""
pos score is good for white
"""
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteMove:
            return -CM  #black wins
        else:
            return CM  #white wins
    elif gs.stalemate:
        return SM

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                #use positional scoring
                piecePositionScore = 0
                if square[1] != 'K':
                    if square[1] == 'p': #for pawns
                        piecePositionScore = piecePositionScores[square][row][col]
                    else: #for other pieces
                        piecePositionScore = piecePositionScores[square[1]][row][col]


                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * .1
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * .1

    return score






"""
Score the board based on material
"""
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score