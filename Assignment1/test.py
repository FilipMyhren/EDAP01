import numpy as np

# Code taken from https://gist.github.com/chiatsekuo/14934705b6baacb64a07bc7ac7ff81c3#file-connect4_evaluate_window-py
def evaluate_window(window, piece):
   score = 0
   opp_piece = -1*piece

   if window.count(piece) == 4:
      score += 100
   elif window.count(opp_piece) == 4:
      score -= 100
   elif window.count(piece) == 3 and window.count(0) == 1:
      score += 5
   elif window.count(piece) == 2 and window.count(0) == 2:
      score += 2
   if window.count(opp_piece) == 3 and window.count(0) == 1:
      score -= 4

   return score

# Code taken from https://gist.github.com/chiatsekuo/58d2fb6d16d4b77ca728ba23846b8cfb#file-connect4_score_position-py
def score_position(board, piece):
    nbr_rows = 6#env.board_shape[0]
    nbr_cols = 7#env.board_shape[1]
    score = 0
   
    ## Score center column
    center_array = [i for i in list(board[:, nbr_cols//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

	## Score Horizontal
    for r in range(nbr_rows):
    row_array = [i for i in list(board[r,:])]
    for c in range(nbr_cols-3):
    	window = row_array[c:c+4]
    	score += evaluate_window(window, piece)

	## Score Vertical
    for c in range(nbr_cols):
        col_array = [i for i in list(board[:,c])]
        for r in range(nbr_rows-3):
            window = col_array[r:r+4]
   		    score += evaluate_window(window, piece)

	## Score posiive sloped diagonal
    for r in range(nbr_rows-3):
        for c in range(nbr_cols-3):
   		    window = [board[r+i][c+i] for i in range(4)]
   		    score += evaluate_window(window, piece)
   
    for r in range(nbr_rows-3):
        for c in range(nbr_cols-3):
   		    window = [board[r+3-i][c+i] for i in range(4)]
   	        score += evaluate_window(window, piece)
   
    #print(score)
    return score

def score_position2(board, piece):

    nbr_rows = 6#env.board_shape[0]
    nbr_cols = 7#env.board_shape[1]
    score = 0

    score += [i for i in list(board[:, nbr_cols//2])].count(piece)*3
    print(f'center row {score}')

    # Test rows
    for r in range(nbr_rows):
        for c in range(nbr_cols - 3):
            score += evaluate_window(list(board[r][c:c + 4]), piece)
    
    print(f'rows {score}')
    # Test columns on transpose array
    reversed_board = [list(i) for i in zip(*board)]
    for c in range(nbr_cols):
        for r in range(nbr_rows - 3):
        score += evaluate_window(reversed_board[c][r:r + 4], piece)
    print(f'cols {score}')
    # Test diagonal
    for r in range(nbr_rows - 3):
        for c in range(nbr_cols - 3):
            score += evaluate_window([board[r+i][c+i] for i in range(4)], piece)
    print(f'dig 1 {score}')
    reversed_board = np.fliplr(board)
    # Test reverse diagonal
    for r in range(nbr_rows - 3):
        for c in range(nbr_cols - 3):
            score += evaluate_window([reversed_board[r+i][c+i] for i in range(4)], piece)
    print(f'dig 2 {score}')
    return score

def alphabeta(depth, alpha, beta, max_search, player):
    avmoves = env.available_moves()
    if depth == 0 or env.is_win_state():
        if debbug: print('no more depth')
        # print(f'max_search = {max_search}')
        # print(env.board)
            return (None, board_value(env.board, player))
    else:
        start_board = env.board
        #print(f'start_board = {start_board} depth = {depth}')
        if debbug: print(f'start_board = {start_board} depth = {depth}')
        best_action = -1 
        if max_search:
            current_high = -100000000
            for action in avmoves:
                #print('in max')
                env.set_player(1)
                env.step(action)
                current_score = alphabeta(depth-1, alpha, beta, not max_search, player)[1]
                if current_score > current_high:
                    current_high = current_score
                    best_action = action
                #print('Reset board')
                alpha = max(alpha, current_high)
                #if alpha >= beta:
                #   break
                env.reset(board=start_board.copy())
            return best_action, current_high
        else:
            current_low = 100000000
            for action in avmoves:
                #print(f'in min action = {action}')
                env.set_player(-1)
                #print(f'start_borad before step {start_board}')
                env.step(action)
                #print(f'start_borad after step {start_board}')
                current_score = alphabeta(depth-1, alpha, beta, not max_search, player)[1]
                if current_score < current_low:
                    current_low = current_score
                    best_action = action
                #print(f'Reset board to start_board {start_board}')
                beta = min(beta, current_low)
                if beta <= alpha:
                    break
                env.reset(board=start_board.copy())
                #print(f'board after reset {env.board}')
            return best_action, current_low
      
# [[ 1 -1  1  0  0  0  0]
#  [-1  1  1  0 -1  0  0]
#  [ 1  1 -1  0 -1  0  0]
#  [-1  1  1  1 -1 -1 -1]
#  [ 1 -1  1 -1  1 -1 -1]
#  [ 1  1  1 -1  1 -1 -1]]
def f1(board, piece):
    score = 0
    for r in range(6 - 3):
      for c in range(7 - 3):
         score += evaluate_window([board[r+i][c+i] for i in range(4)], piece)
    return score

t0 = np.array([[ 1, -1,  1,  0,  0,  0,  0],
               [-1,  1,  1,  0, -1,  0,  0],
               [ 1,  1, -1,  0, -1,  0,  0],
               [-1,  1,  1,  1, -1, -1, -1],
               [ 1, -1,  1, -1,  1, -1, -1],
               [ 1,  1,  1, -1,  1, -1, -1]])


t1 = np.array([[ 1, -1,  1,  0,  0,  0,  0],
               [-1,  1,  1,  0, -1,  0,  0],
               [ 1,  1, -1,  0, -1,  0,  -1],
               [-1,  1,  1,  1, -1, -1, -1],
               [ 1, -1,  1, -1,  1, -1, -1],
               [ 1,  1,  1, -1,  1, -1, -1]])

t2 = np.array([[ 1, -1,  1,  0,  0,  0,  0],
               [-1,  1,  1,  0, -1,  0,  0],
               [ 1,  1, -1,  1, -1,  0,  0],
               [-1,  1,  1,  1, -1, -1, -1],
               [ 1, -1,  1, -1,  1, -1, -1],
               [ 1,  1,  1, -1,  1, -1, -1]])
t3 = np.array([[0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 1, 0, 0, 0],
               [0, 0, 1, 0, 0, 0, 0],
               [0, 1, 0, 0, 0, 0, 0],
               [1, 0, 0, 0, 0, 0, 0]])

t4 = np.array([[0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0],
               [1, 0, 0, 0, 0, 0, 0],
               [0, 1, 0, 0, 0, 0, 0],
               [0, 0, 1, 0, 0, 0, 0],
               [0, 0, 0, 1, 0, 0, 0]])

t5 = np.array([[0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 1, 1, 0],
               [0, 0, 0, 1, 1, 1, 1]])

print(score_position2(t5, 1))
# print(t5)
# print(f1(t5, 1))
# t6 = np.fliplr(t5)
# print(t6)

