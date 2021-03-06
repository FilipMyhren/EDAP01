import gym
import random
import requests
import numpy as np
import argparse
import sys
from gym_connect_four import ConnectFourEnv
import os
sys.path.append(os.path.abspath("gym_connect_four/envs"))
from render import *


env: ConnectFourEnv = gym.make("ConnectFour-v0")
debbug = False

#SERVER_ADRESS = "http://localhost:8000/"
SERVER_ADRESS = "https://vilde.cs.lth.se/edap01-4inarow/"
API_KEY = 'nyckel'
STIL_ID = ["fi8057my-s"] # TODO: fill this list with your stil-id's

def call_server(move):
   res = requests.post(SERVER_ADRESS + "move",
                       data={
                           "stil_id": STIL_ID,
                           "move": move, # -1 signals the system to start a new game. any running game is counted as a loss
                           "api_key": API_KEY,
                       })
   # For safety some respose checking is done here
   if res.status_code != 200:
      print("Server gave a bad response, error code={}".format(res.status_code))
      exit()
   if not res.json()['status']:
      print("Server returned a bad status. Return message: ")
      print(res.json()['msg'])
      exit()
   return res

def check_stats():
   res = requests.post(SERVER_ADRESS + "stats",
                       data={
                           "stil_id": STIL_ID,
                           "api_key": API_KEY,
                       })

   stats = res.json()
   return stats

"""
You can make your code work against this simple random agent
before playing against the server.
It returns a move 0-6 or -1 if it could not make a move.
To check your code for better performance, change this code to
use your own algorithm for selecting actions too
"""
def opponents_move(state):
   env.change_player() # change to oppoent
   avmoves = env.available_moves()
   if not avmoves:
      env.change_player() # change back to student before returning
      return -1

   # TODO: Optional? change this to select actions with your policy too
   # that way you get way more interesting games, and you can see if starting
   # is enough to guarrantee a win
   # action = random.choice(list(avmoves))
   env.reset(board=state.copy())
   temp_board = env.board.copy()
   action, score = maximizer(2, -100000000, 100000000, -1)
   env.reset(board=temp_board)
   env.set_player(-1)
   state, reward, done, _ = env.step(action)
   if done:
      if reward == 1: # reward is always in current players view
         reward = -1
   env.change_player() # change back to student before returning
   return state, reward, done

def student_move(state):
   """
   TODO: Implement your min-max alpha-beta pruning algorithm here.
   Give it whatever input arguments you think are necessary
   (and change where it is called).
   The function should return a move from 0-6
   """
   env.reset(board=state.copy())
   temp_board = env.board.copy()
   action, score = maximizer(4, -100000000, 100000000, 1)
   env.reset(board=temp_board)
   env.set_player(1) 
   return action
   

# Code taken from https://gist.github.com/chiatsekuo/14934705b6baacb64a07bc7ac7ff81c3#file-connect4_evaluate_window-py
def evaluate_window(window, piece):
   score = 0
   opp_piece = -1*piece
   score += (window.count(piece) == 4)*100
   score -= (window.count(opp_piece) == 4)*100
   score += (window.count(piece) == 3 and window.count(0) == 1)*5
   score += (window.count(piece) == 2 and window.count(0) == 2)*2
   score -= (window.count(opp_piece) == 3 and window.count(0) == 1)*4
   return score

def board_value(board, piece):
   nbr_rows = env.board_shape[0]
   nbr_cols = env.board_shape[1]
   score = 0

   # Center column
   score += [i for i in list(board[:, nbr_cols//2])].count(piece)*3
   # Rows score
   for r in range(nbr_rows):
      for c in range(nbr_cols - 3):
         score += evaluate_window(list(board[r][c:c + 4]), piece)
   # Column score
   reversed_board = [list(i) for i in zip(*board)]
   for c in range(nbr_cols):
      for r in range(nbr_rows - 3):
         score += evaluate_window(reversed_board[c][r:r + 4], piece)
   reversed_board = np.fliplr(board)
   # Diagonals score
   for r in range(nbr_rows - 3):
      for c in range(nbr_cols - 3):
         score += evaluate_window([board[r+i][c+i] for i in range(4)], piece)
         score += evaluate_window([reversed_board[r+i][c+i] for i in range(4)], piece)
   return score

def maximizer(depth, alpha, beta, player):
   avmoves = env.available_moves()
   if depth == 0 or env.is_win_state():
      #print(env.board)
      return (None, board_value(env.board, player))
   else:
      start_board = env.board
      best_action = None 
      current_high = -100000000
      for action in avmoves:
         env.set_player(player)
         env.step(action)
         current_score = minimizer(depth-1, alpha, beta, player)[1]
         if current_score > current_high:
            current_high = current_score
            best_action = action
         alpha = max(alpha, current_high)
         if alpha >= beta:
            break
         env.reset(board=start_board.copy())
      return best_action, current_high

def minimizer(depth, alpha, beta, player):
   avmoves = env.available_moves()
   if depth == 0 or env.is_win_state():
      #print(env.board)
      return (None, board_value(env.board, player))
   else:
      start_board = env.board
      best_action = None 
      current_low = 100000000
      for action in avmoves:
         env.set_player(-1*player)
         env.step(action)
         current_score = maximizer(depth-1, alpha, beta, player)[1]
         if current_score < current_low:
            current_low = current_score
            best_action = action
         beta = min(beta, current_low)
         if beta <= alpha:
            break
         env.reset(board=start_board.copy())
      return best_action, current_low
   
def play_game(vs_server = False):
   """
   The reward for a game is as follows. You get a
   botaction = random.choice(list(avmoves)) reward from the
   server after each move, but it is 0 while the game is running
   loss = -1
   win = +1
   draw = +0.5
   error = -10 (you get this if you try to play in a full column)
   Currently the player always makes the first move
   """

   # default state
   state = np.zeros((6, 7), dtype=int)

   # setup new game
   if vs_server:
      # Start a new game
      res = call_server(-1) # -1 signals the system to start a new game. any running game is counted as a loss

      # This should tell you if you or the bot starts
      print(res.json()['msg'])
      botmove = res.json()['botmove']
      state = np.array(res.json()['state'])
   else:
      # reset game to starting state
      env.reset(board=None)
      # determine first player
      student_gets_move = random.choice([True, False])
      if student_gets_move:
         print('You start!')
         print()
      else:
         print('Bot starts!')
         print()

   # Print current gamestate
   print("Current state (1 are student discs, -1 are servers, 0 is empty): ")
   print(state)
   print()

   done = False
   images = render_board(state)
   print(len(images))
   while not done:
      
      # Select your move
      stmove = student_move(state) # TODO: change input here
      print(f'move is = {stmove}')

      # make both student and bot/server moves
      if vs_server:
         # Send your move to server and get response
         res = call_server(stmove)
         print(res.json()['msg'])

         # Extract response values
         result = res.json()['result']
         botmove = res.json()['botmove']
         state = np.array(res.json()['state'])
      else:
         if student_gets_move:
            # Execute your move
            avmoves = env.available_moves()
            if stmove not in avmoves:
               print("You tried to make an illegal move! Games ends.")
               break
            state, result, done, _ = env.step(stmove)
            

         student_gets_move = True # student only skips move first turn if bot starts

         # print or render state here if you like

         # select and make a move for the opponent, returned reward from students view
         if not done:
            state, result, done = opponents_move(state)

      # Check if the game is over
      if result != 0:
         done = True
         if not vs_server:
            print("Game over. ", end="")
         if result == 1:
            print("You won!")
         elif result == 0.5:
            print("It's a draw!")
         elif result == -1:
            print("You lost!")
         elif result == -10:
            print("You made an illegal move and have lost!")
         else:
            print("Unexpected result result={}".format(result))
         if not vs_server:
            print("Final state (1 are student discs, -1 are servers, 0 is empty): ")
      else:
         print("Current state (1 are student discs, -1 are servers, 0 is empty): ")

      # Print current gamestate
      print(state)
      print()

def main():
   # Parse command line arguments
   parser = argparse.ArgumentParser()
   group = parser.add_mutually_exclusive_group()
   group.add_argument("-l", "--local", help = "Play locally", action="store_true")
   group.add_argument("-o", "--online", help = "Play online vs server", action="store_true")
   parser.add_argument("-s", "--stats", help = "Show your current online stats", action="store_true")
   args = parser.parse_args()

   # Print usage info if no arguments are given
   if len(sys.argv)==1:
      parser.print_help(sys.stderr)
      sys.exit(1)

   if args.local:
      play_game(vs_server = False)
   elif args.online:
      play_game(vs_server = True)

   if args.stats:
      stats = check_stats()
      print(stats)

   # TODO: Run program with "--online" when you are ready to play against the server
   # the results of your games there will be logged
   # you can check your stats bu running the program with "--stats"
# state = np.zeros((6, 7), dtype=int)
# env.reset(board=state)
# res = maximizer(4, 0, 100000000, 1)
# print(res[0], res[1])
if __name__ == "__main__":
    main()
