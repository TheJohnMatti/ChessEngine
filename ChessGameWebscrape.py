from bs4 import BeautifulSoup as bs
import requests
def getCurrentMove(gs, analysisColor, moveColor, gameLink, validMoves):
    moveToPlay = False
    page = requests.get(gameLink)
    soup = bs(page.content, 'html.parser')
    moveLog = gs.moveLog
    moveNum = len(moveLog)//2
    movesToPlay = []
    moveTextList = []
    if moveColor == 'w' and (analysisColor == 'wb' or analysisColor == 'w'):
        movesToPlay = soup.find_all('div', class_="white node")
        movesToPlay.append(soup.find('div', class_="white node selected"))
    elif moveColor == 'b' and (analysisColor == 'wb' or analysisColor == 'b'):
        movesToPlay = soup.find_all('div', class_="black node")
        movesToPlay.append(soup.find('div', class_="white node selected"))
    for move in movesToPlay:
        if move != None:
            moveTextList.append(move.text)
    moveNotationToPlay = None
    if moveNum < len(movesToPlay):
        moveNotationToPlay = movesToPlay[moveNum]
    for move in validMoves:
        if moveNotationToPlay == str(move):
            moveToPlay = move
    if type(validMoves[0]) == type(moveToPlay):
        return moveToPlay
    else:
        return None
