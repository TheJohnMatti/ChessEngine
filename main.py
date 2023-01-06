"""
this is the file responsible for user input
"""
import pygame as p
import engine
import ChessAI
import ChessGameWebscrape
from multiprocessing import Process, Queue

GAME_W = GAME_H = 650
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = GAME_H
DIMENSION = 8
LINE_THICKNESS = 2
SQ_SIZE = GAME_H // DIMENSION
MAX_FPS = 25
IMAGES = {}
"""
make images dictionary
"""
def loadPiecePNGs():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.image.load("chess_images_3d/" + piece + ".png")
        IMAGES[piece] = p.transform.scale(IMAGES[piece], (2*SQ_SIZE/3, SQ_SIZE))
    #access image by using this dictionary

def main():
    p.init()
    screen = p.display.set_mode((GAME_W + MOVE_LOG_PANEL_WIDTH, GAME_H))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Calibri", 14, False, False)
    gs = engine.CurrentBoard()
    availableMoves = gs.getValidMoves()
    animation = False  #flag variable for when to animate a move
    moveMade = False  # flag variable for when a move is made
    loadPiecePNGs()
    running = True
    squareSelected = () #user's last click
    userPresses = [] #keep track of clicks
    endGame = False
    whiteIsHuman = True  #If a human is playing white, this is true
    blackIsHuman = True  #same but for black
    AIThinking = False  #flag variable used to control the AI
    moveFinderProcess = None
    analysisMode = False    #flag variable used to initialize analysis mode
    gameLink = ""  #analysis mode input
    analysisColor = ""  #analysis mode input
    resign = False  #flag variable for resignation



    while running:
        humanTurn = (gs.whiteMove and whiteIsHuman) or (not gs.whiteMove and blackIsHuman)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animation = False
                    endGame = False
                if e.key == p.K_r:
                    gs = engine.CurrentBoard()
                    availableMoves = gs.getValidMoves()
                    squareSelected = ()
                    userPresses = []
                    moveMade = False
                    animation = False
                    endGame = False
                if e.key == p.K_a: #enter analysis mode
                    gs = engine.CurrentBoard()
                    availableMoves = gs.getValidMoves()
                    squareSelected = ()
                    userPresses = []
                    moveMade = False
                    animation = False
                    endGame = False
                    analysisMode = True
                    gameLink = input("Game Link: ")
                    while analysisColor != 'w' and analysisColor != 'b' and analysisColor != 'wb':
                        analysisColor = input("Which color's moves will you extract "
                                              "('w' for white, 'b' for black, or 'wb' for both)?")

            elif e.type == p.MOUSEBUTTONDOWN:
                if not endGame:
                    mouseLocation = p.mouse.get_pos() #x, y coords of mouse
                    col = mouseLocation[0]//SQ_SIZE
                    row = mouseLocation[1]//SQ_SIZE
                    if squareSelected == (row, col) or col >= 8: #deselecting
                        squareSelected = () #empty selected
                        userPresses = []
                    else:
                        squareSelected = (row, col)
                        userPresses.append(squareSelected) #append for both clicks
                    if len(userPresses) == 2 and humanTurn: #after second click
                        move = engine.Move(userPresses[0], userPresses[1], gs.board)
                        for i in range(len(availableMoves)):
                            if move == availableMoves[i]:
                                gs.move(availableMoves[i])
                                moveMade = True
                                animation = True
                                squareSelected = ()
                                userPresses = [] #reset clicks
                        if not moveMade:
                            userPresses = [squareSelected]






        #AI move finder
        if analysisMode:
            moveToPlay = ChessGameWebscrape.getCurrentMove(gs, analysisColor, 'w' if gs.whiteMove else 'b', gameLink, availableMoves)
            if moveToPlay != None:
                gs.move(moveToPlay)
                moveMade = True
                animation = True


        if not endGame and not humanTurn:
            if not AIThinking:
                AIThinking = True
                print("thinking")
                returnQueue = Queue() #used for data transfer between threads
                moveFinderProcess = Process(target=ChessAI.findBestMove, args=(gs, availableMoves, returnQueue))
                moveFinderProcess.start() #calls bestmovefinder

            if not moveFinderProcess.is_alive():
                print("best move found")
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = ChessAI.findRandomMove(availableMoves)
                gs.move(AIMove)
                moveMade = True
                animation = True
                AIThinking = False

        if moveMade:
            if animation:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            availableMoves = gs.getValidMoves()
            moveMade = False
            animation = False

        drawAll(screen, gs, availableMoves, squareSelected, move_log_font)

        if gs.checkmate or gs.stalemate:
            endGame = True
            if gs.stalemate:
                text = "Stalemate"
            else:
                text = "Black wins by checkmate" if gs.whiteMove else "White wins by checkmate"
            drawEndgameText(screen, text)


        clock.tick(MAX_FPS)
        p.display.flip()



"""
Highlight function
"""
def highlight(screen, gs, validMoves, square):
    if square != ():
        r, c = square
        if gs.board[r][c][0] == ('w' if gs.whiteMove else 'b'): #sqSelected can be moved
            #highlight
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  #transparency scale: 0 (transparent) - 255 (opaque)
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.row1 == r and move.col1 == c:
                    screen.blit(s, (SQ_SIZE * move.col2, SQ_SIZE * move.row2))
"""
graphics
"""
def drawAll(screen, gs, availableMoves, squareSelected, moveLogFont):
    drawBoard(screen)  #board squares
    drawLines(screen)  #draw separation lines between each square
    drawPieces(screen, gs.board)  #board pieces
    highlight(screen, gs, availableMoves, squareSelected)
    drawMoveLog(screen, gs, moveLogFont)


#squares - top-left is light
def drawBoard(screen):
    global colors
    colors = [p.Color("light gray"), p.Color("dark green")]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[(i+j)%2]
            p.draw.rect(screen, color, p.Rect(j*SQ_SIZE, i*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawLines(screen):
    lineColor = p.Color('black')
    for i in range(DIMENSION):
        p.draw.line(screen, lineColor, (i*SQ_SIZE, 0), (i*SQ_SIZE, DIMENSION*SQ_SIZE), LINE_THICKNESS)  #vertical line
        p.draw.line(screen, lineColor, (0, i*SQ_SIZE), (DIMENSION*SQ_SIZE, i*SQ_SIZE), LINE_THICKNESS)  #horizontal line

#draw pieces according to gs
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # indicating there is a piece there
                screen.blit(IMAGES[piece], p.Rect((c + 1/6) * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Draws move log
"""
def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(GAME_W, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("dark gray"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)

    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color("black"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

"""
Animations
"""
def animateMove(move, screen, board, clock):
    global colors
    dR = move.row2 - move.row1  #row difference
    dC = move.col2 - move.col1  #column difference
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount+1):
        r, c = (move.row1 + dR * frame / frameCount, move.col1 + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        drawLines(screen)
        #erase the piece moved from its ending square
        color = colors[(move.row2 + move.col2) % 2]
        endSquare = p.Rect(move.col2 * SQ_SIZE, move.row2 * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = move.row2 + 1 if move.pieceCaptured[0] == 'b' else move.row2 - 1
                endSquare = p.Rect((move.col2+1/6) * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            else:
                screen.blit(IMAGES[move.pieceCaptured], p.Rect((move.col2+1/6)*SQ_SIZE, move.row2*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect((c+1/6)*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(120)

def drawEndgameText(screen, text):
    font = p.font.SysFont("Helvitca", 50, True, False)
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, GAME_W, GAME_H).move(GAME_W / 2 - textObject.get_width() / 2,
                                                     GAME_H / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()
