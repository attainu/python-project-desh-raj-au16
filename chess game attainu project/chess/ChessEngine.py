"""
this class is responsible for storing info. about the current state of a chess game.
it will also be responsible for determining the valid move at the current state. it will keep move log.
"""


class GameState:
    def __init__(self):
        # board is an 8x8 2d list, each element of the list has 2 char.
        # The first char represents the color of the piece, 'b' or 'w' .
        # The second char represents the type of the piece, 'K', 'Q', 'R', 'B', 'N', OR 'P'.
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"P": self.getPawnMoves, "R": self.getPawnMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()  # coordinates for the square where en passant capture is possible.
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            i = input(" Promote to Q, R, B OR N :")
            # self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedpiece
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + i
        # en passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # update enpassant possible variable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:  # only on two square pawn advance
            # if move.pieceMoved[1]=="p" and abs(move.startRow - move.endCol)==2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()
        # castling
        if move.isCastleMove:
            if abs(move.endCol - move.startCol) == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # moves the rook
                self.board[move.endRow][move.endCol + 1] = "--"
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # moves the Rook
                self.board[move.endRow][move.endCol - 2] == "--"

        # update castling right - whenever it is a rook or a king undo
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back,
            # update the king's position if needed.
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo enpassant move.
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # leave landing square blank.
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            # undo a 2 square pawn possible.
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # undo castling rights.
            self.castleRightsLog.pop()  # get rid of the new castle rights from the move we are undoing.
            self.currentCastlingRight = self.castleRightsLog[-1]  # set the current castle rights to the one in the list
            # undo castle move.
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side.
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # queen side.
                    self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn move.
            if self.board[r - 1][c] == "--":  # 1 square pawn advance.
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance.
                    moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:  # capture to the left.
                if self.board[r - 1][c - 1][0] == "b":  # enemy piece to capture.
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # capture to the right.
                if self.board[r - 1][c + 1][0] == "b":  # enemy piece to capture.
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:  # black pawn moves.
            if self.board[r + 1][c] == "--":  # 1 square move.
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square moves.
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # captures
            if c - 1 >= 0:  # capture to left.
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:  # capture to right.
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))
        # add pawn promotion later.

    """
    get all the rook moves for the rook located at row , col and add these moves to the list.
    """

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board.
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid.
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece valid.
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece invalid.
                        break
                else:  # off board.
                    break

    """
        get all the knight moves for the rook located at row , col and add these moves to the list.
        """

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allycolor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allycolor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
        get all the bishop moves for the rook located at row , col and add these moves to the list.
        """

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemycolor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemycolor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    """
        get all the queen moves for the rook located at row , col and add these moves to the list.
        """

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    """
    get all the King moves for the rook located at row , col and add these moves to the list.
    """

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allycolor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endpiece = self.board[endRow][endCol]
                if endpiece[0] != allycolor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    update the castle rights given the move.
    """

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:  # left root
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right root
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    """
    All moves considering checks
    """

    def getValidMoves(self):
        for log in self.castleRightsLog:
            print(log.wks, log.wqs, log.bqs, log.bks, end="")
        print()
        tempEnpassantPossible = self.enpassantPossible
        # copy the current castling rights
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)

        # 1> generate all possible moves.
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        # 2> for each move, make the moves.
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # 3> generate all opponent's moves.
            # 4> for each of your opponent"s moves, see if they attack your king.
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  # 5> if they attack your king, not a valid move.
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  # either checkmate or stalemate.
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    """
    Determine if the current player is in check.
    """

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    Determine if the enemy can attack the square r, c.
    """

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    """
    All moves without considering checks.
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):  # number cof col in given row.
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)  # calls the appropriate move function based on piece type.
        return moves

    """
    generate all valid castle moves for the king at (r,c) and add them to the list of moves.
    """

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  # we cant castle while we are in check.
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # maps keys to values.
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion.
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (
                self.pieceMoved == "bP" and self.endRow == 7)
        # en passant.
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        # castling
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        # print(self.moveID)

    """
        overriding the equals method.
        """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFiles(self.startRow, self.startCol) + self.getRankFiles(self.endRow, self.endCol)

    def getRankFiles(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
