"""
this is the driver file. it will be responsible for handling user input and displaying the current GameState object.
"""

import pygame as p
from chess import ChessEngine, SmartMoveFinder


WIDTH = HEIGHT = 513  # 400 IS ANOTHER OPTION.
DIMENSION = 8  # DIMENSIONS OF CHESS BOARD ARE 8X8.
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
p.display.set_caption("CHESS_GAME_2_PLAYER")

"""
# INITIALIZE A GLOBAL DICT OF IMAGES. THIS WILL BE CALLED EXACTLY ONCE IN THE MAIN.
"""


def loadImages():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


"""
# The main driver for our code. This will handle user input and updating the graphics
"""


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    p.display.set_caption("Chess with Desh Raj")
    moveMade = False  # flag variable for when a move is made
    animate = False
    loadImages()
    print(gs.board)
    running = True
    sqSelected = ()  # no square is selected, keep track of the last click of the user(tuple: (row,col)
    playerClicks = []  # keep track  of player click(two tuple: [(6,4),(4,4)]
    gameOver = False
    # playerOne = True  # if human playing white, then this will be true. if an AI is playing, then False.
    # playerTwo = False   # Same as above.
    while running:
        # humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #  mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:  # and humanTurn:
                    location = p.mouse.get_pos()  # (x,y) location of mouse.
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):  # the player clicked the same square twice.
                        sqSelected = ()  # deselect
                        playerClicks = []  # clear player click
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # append for both first and second clicks.
                    if len(playerClicks) == 2:  # after 2nd click.
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # reset user clicks.
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when "z" is pressed.
                    gs.undoMove()
                    moveMade = True
                    # animate = False
                if e.key == p.K_r:  # reset the board.
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
        """
        # AI move finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True"""

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "white wins by checkmate")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "stalemate")
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Highlights square selected and moves for piece selected.
"""


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):
            # highlight selected square.
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value -> 0 transparent: 225 opaque.
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves from that square.
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # draw squares on the board.
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares.


# Draw the pieces on the board using the GameState.board.
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # not empty square.
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# Draw the squares on the board.
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("dark green")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Animating a move.
"""


def animateMove(move, screen, board, clock):
    global colors
    coords = []  # list of coords that the animation will move through.
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # frames to move one square.
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle.
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece.
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont(" Times New Roman", 28, True, False)
    textObject = font.render(text, 0, (25, 25, 0))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, (124, 55, 225))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == '__main__':
    main()
