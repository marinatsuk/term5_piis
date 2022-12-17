import chess
import chess.engine
import time

chessEngine = chess.engine.SimpleEngine.popen_uci(r"stockfish_15_win_x64_avx2\stockfish_15_x64_avx2.exe")

def evaluate(board, isMax):
    info = chessEngine.analyse(board, chess.engine.Limit(depth=1))
    side =  (chess.BLACK, chess.WHITE)[isMax]
    result = chess.engine.PovScore(info['score'], side).pov(side).relative.score()
    return (result, 0)[result is None]


def negaMax(board, depth, isMax):
    if depth == 0:
        return evaluate(board, isMax)
    maxValue = -float('inf')
    for move in board.legal_moves:
        move = chess.Move.from_uci(str(move))
        newBoard = board.copy()
        newBoard.push(move)
        value = -negaMax(newBoard, depth - 1, 1 - isMax)
        if value > maxValue:
            maxValue = value
    return maxValue

def negamax_move(board, depth):
    maxValue = -float('inf')
    bestMove = None
    for move in board.legal_moves:
        move = chess.Move.from_uci(str(move))
        newBoard = board.copy()
        newBoard.push(move)
        value = -negaMax(newBoard, depth, 1 - newBoard.turn)
        if value > maxValue:
            maxValue = value
            bestMove = move

    return bestMove

def negaScout(board, depth, alpha, beta):
    if depth == 0:
        return evaluate(board, board.turn)
    score = -float('inf')
    n = beta
    for move in board.legal_moves:
        move = chess.Move.from_uci(str(move))
        newBoard = board.copy()
        newBoard.push(move)
        current = -negaScout(newBoard, depth - 1, -n, -alpha)
        if current > score:
            if n == float('inf') or depth <= 2:
                score = current
            else:
                score = -negaScout(newBoard, depth - 1, -beta, -current)
        if score > alpha:
            alpha = score
        if alpha >= beta:
            return alpha
        n = alpha + 1
    return score

def negascout_move(board, depth):
    score = -float('inf')
    bestMove = None
    for move in board.legal_moves:
        move = chess.Move.from_uci(str(move))
        newBoard = board.copy()
        newBoard.push(move)
        value = -negaScout(newBoard, depth, -float('inf'), float('inf'))
        if value > score:
            score = value
            bestMove = move

    return bestMove

def principal_value(board, depth, alpha, beta):
    if depth == 0:
        return evaluate(board, board.turn)
    bSearchPv = True
    for move in board.legal_moves:
        move = chess.Move.from_uci(str(move))
        newBoard = board.copy()
        newBoard.push(move)
        if bSearchPv:
            current = -principal_value(newBoard, depth - 1, -beta, -alpha)
        else:
            current = -principal_value(newBoard, depth - 1, -alpha - 1, -alpha)
            if alpha < current < beta:
                current = -principal_value(newBoard, depth - 1, -beta, -alpha)
        if current >= beta:
            return beta
        if current > alpha:
            alpha = current
            bSearchPv = False
    return alpha

def principal_value_move(board, depth):
    score = -float('inf')
    bestMove = None
    for move in board.legal_moves:
        move = chess.Move.from_uci(str(move))
        newBoard = board.copy()
        newBoard.push(move)
        value = -principal_value(newBoard, depth, -float('inf'), float('inf'))
        if value > score:
            score = value
            bestMove = move

    return bestMove

def start(algorithm, depth = 1):
    board = chess.Board()
    turnCounter = 0

    while not (board.is_checkmate() or board.is_fivefold_repetition()):
        timeAtTurnStart = time.time()
        move = algorithm(board, depth)
        timeAtTurnEnd = time.time()

        if move is None:
            print("Checkmate | ",('White wins','Black wins')[turnCounter % 2 == 0])
            break
        else:
            if turnCounter % 2 == 0:
                print("---White Turn---")
            else:
                print("---Black Turn---")

        print("Move:", move)
        print("Turn time:", timeAtTurnEnd - timeAtTurnStart)

        board.push(move)
        print(board, "\n")
        turnCounter = turnCounter + 1
    if board.is_fivefold_repetition():
        print("Fivefold")

if __name__ == '__main__':
    start(principal_value_move)
    chessEngine.quit()