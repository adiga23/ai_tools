import os
import sys
import numpy as np
from numpy.lib.function_base import disp
import time
import math
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense,Input
from pprint import pprint
import json
import pandas as pd
import matplotlib.pyplot as plt


### The experience replay memory ###
class ReplayBuffer:
    def __init__(self, obs_dim, act_dim, size,current_train_pri=True):
        self.obs1_buf = np.zeros([size, obs_dim], dtype=np.uint8)
        self.obs2_buf = np.zeros([size, obs_dim], dtype=np.uint8)
        self.acts_buf = np.zeros(size, dtype=np.uint8)
        self.rews_buf = np.zeros(size, dtype=np.float32)
        self.done_buf = np.zeros(size, dtype=np.uint8)
        self.ptr, self.size, self.max_size = 0, 0, size
        self.obs_dim = obs_dim
        self.current_train_vars = []
        self.current_train_pri = current_train_pri


    def store(self, obs, act, rew, next_obs, done):
        self.obs1_buf[self.ptr] = obs
        self.obs2_buf[self.ptr] = next_obs
        self.acts_buf[self.ptr] = act
        self.rews_buf[self.ptr] = rew
        self.done_buf[self.ptr] = done
        self.current_train_vars.append(self.ptr)
        self.ptr = (self.ptr+1) % self.max_size
        self.size = min(self.size+1, self.max_size)

    def new_game(self):
        self.current_train_vars = []

    def sample_batch(self, batch_size=32):
        if self.size > batch_size:
            idxs = np.arange(0, self.size, 1)
            np.random.shuffle(idxs)
            if self.current_train_pri:
                idxs = idxs[0:batch_size-len(self.current_train_vars)]
                idxs = np.concatenate([idxs,self.current_train_vars])
            else:
                idxs = idxs[0:batch_size]
        else:
            idxs = np.arange(0, self.size, 1)

        return dict(s=self.obs1_buf[idxs],
                    s2=self.obs2_buf[idxs],
                    a=self.acts_buf[idxs],
                    r=self.rews_buf[idxs],
                    d=self.done_buf[idxs])

    def save_buffer(self,file):
        mod_replay_buffer = []
        for i in range(0,self.size):
            curr_state = self.obs1_buf[i].tolist()
            next_state = self.obs2_buf[i].tolist()

            for j in range(0,self.obs_dim):
                curr_state[j] = int(curr_state[j])
                next_state[j] = int(next_state[j])
            
            action = int(self.acts_buf[i])

            rewards = int(self.rews_buf[i])

            done = int(self.done_buf[i])
            mod_sample = {"curr_state" : curr_state,
                          "next_state" : next_state,
                          "action"     : action,
                          "rewards"    : rewards,
                          "done"       : done}

            mod_replay_buffer.append(mod_sample)
        dict_local = {"data":mod_replay_buffer}
        
        f = open(file,"w")
        json.dump(dict_local,f)
        f.close()

    def load_data(self,file):
        
        if os.path.exists(file):
            f = open(file,"r")
            data = json.load(f)
            for sample in data["data"]:
                state = np.array(sample["curr_state"])
                next_state = np.array(sample["next_state"])
                action = sample["action"]
                rewards = sample["rewards"]
                done = sample["done"]
                self.store(state,action,rewards,next_state,done)
            f.close()

    def __len__(self):
        return(self.size)



def mlp(input_dim, n_action, n_hidden_layers=1, hidden_dim=32):
  """ A multi-layer perceptron """
  # input layer
  i = Input(shape=(input_dim,))
  x = i
  # hidden layers
  for _ in range(n_hidden_layers):
    x = Dense(hidden_dim, activation='relu')(x)
  # final layer
  x = Dense(n_action)(x)
  # make the model
  model = Model(i, x)
  model.compile(loss='mse', optimizer='adam')
  return model

class board():
    def __init__(self,size=3):
        ## Fill the board with no moves
        self.board_data = np.zeros((size,size),dtype=int)
        self.size = size

    def display_board(self):
        top_bot = "=" * (4 + self.size*8)
        board_str = top_bot + "\n"
        for i in range(0,self.size):
            for j in range(0,self.size):
                if self.board_data[i,j] == 0:
                    disp_str = ""
                elif self.board_data[i,j] == 1:
                    disp_str = "o"
                else:
                    disp_str = "x"
                board_str += f"|{disp_str:^8}"

            board_str += "|\n"
        board_str += top_bot + "\n"
        os.system("clear")
        print(board_str)
    
    def set(self,x,y,user=0):
        assert(user in [0,1])
        self.board_data[x,y] = user + 1


    def reset(self):
        self.board_data = np.zeros((self.size,self.size),dtype=int)
    
    def get_board_data(self):
        return(self.board_data)

class env():
    def __init__(self,size=3):
        self.board_size = size
        self.board_inst = board(size)
        self.state = self.board_inst.get_board_data()
        
        ##REVISIT
        self.first_move = True
        self.prev_user = 0

    def reset(self):
        self.board_inst.reset()
        self.state = self.board_inst.get_board_data() 

        ## REVISIT
        self.first_move = True   
        self.prev_user = 0

    def is_user_win(self,user):
        assert(user in [0,1])
        for i in range(0,self.board_size):
            curr_col = self.state[:,i]
            curr_row = self.state[i,:]
            if len(curr_col[curr_col == (user + 1)]) == self.board_size:
                return(True)
            if len(curr_row[curr_row == (user + 1)]) == self.board_size:
                return(True)
        diag = self.state.diagonal()
        if len(diag[diag == (user + 1)]) == self.board_size:
            return(True)
        diag = np.rot90(self.state).diagonal()
        if len(diag[diag == (user + 1)]) == self.board_size:
            return(True)
        return(False)
            

    def perform_action(self,x=0,y=0,user=0):

        if self.is_user_win(0) or self.is_user_win(1):
            pprint(f"Got action after winning the game x : {x} y : {y} user : {user}")
            exit()

        if not self.first_move:
            if user == self.prev_user:
                pprint(f"Same user played the move twice user : {user}")
                exit()

        self.prev_user = user
        self.first_move = False
        assert(x in range(0,self.board_size))
        assert(y in range(0,self.board_size))
        assert(user in [0,1])
        rewards0 = 0
        rewards1 = 0
        curr_state = np.array(self.state)
        self.board_inst.set(x,y,user)
        self.state = self.board_inst.get_board_data()

        ## If someone make wrong move then return done and -2 reward
        if curr_state[x,y] > 0:
            if user==0:
                rewards0 = -100
                rewards1 = 0
            else:
                rewards0 = 0
                rewards1 = -100
            dict_local = {"curr_state" : curr_state,
                    "action" : (x,y,user),
                    "next_state" : self.state,
                    "rewards0" : rewards0,
                    "rewards1" : rewards1,
                    "done" : True,
                    "win" : False,
                    "draw" : False,
                    "wrong" : True}
            return(dict_local)

        ## If user wins return done and reward of +100
        if self.is_user_win(user):
            if user == 0:
                rewards0 = 100
                rewards1 = -100
            else:
                rewards0 = -100
                rewards1 = 100
            dict_local = {"curr_state" : curr_state,
                    "action" : (x,y,user),
                    "next_state" : self.state,
                    "rewards0" : rewards0,
                    "rewards1" : rewards1,
                    "done" : True,
                    "win" : True,
                    "draw" : False,
                    "wrong" : False}
            return(dict_local)

        ## If all moves are completed then its a draw
        if len(self.state[self.state > 0]) == (self.board_size * self.board_size):
            rewards0 = -40
            rewards1 = -40
            dict_local = {"curr_state" : curr_state,
                    "action" : (x,y,user),
                    "next_state" : self.state,
                    "rewards0" : rewards0,
                    "rewards1" : rewards1,
                    "done" : True,
                    "win" : False,
                    "draw" : True,
                    "wrong" : False}
            return(dict_local)           

        ## If user does not win return rewards of -1

        rewards0 = -10
        rewards1 = -10
        dict_local = {"curr_state" : curr_state,
                "action" : (x,y,user),
                "next_state" : self.state,
                "rewards0" : rewards0,
                "rewards1" : rewards1,
                "done" : False,
                "win" : False,
                "draw" : True,
                "wrong" : False}
        return(dict_local)

    def display_board(self):
        self.board_inst.display_board()

class agent():
    def __init__(self,board_size=3,user=0,batch_size=50,random_player=False,manual=False,perfect=False):
        self.batch_size = batch_size
        self.board_size = board_size
        self.model_folder = f"tick_tac_toe_models{self.board_size}_{user}"
        self.model_name = f"{self.model_folder}/tick_tac_toe_{user}"
        self.epsilon_path =f"{self.model_folder}/epsilon"
        self.replay_data_name = f"{self.model_folder}/replay_data"
        self.random_player = random_player
        self.manual = manual
        self.perfect = perfect

        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.gamma = 0.95 
        self.user = user
        self.replay_buffer = ReplayBuffer((board_size**2) * 2,board_size**2,100)

        if not (self.random_player or self.manual):
            self.init_neural_network()
            self.replay_buffer.load_data(self.replay_data_name)
        
    def new_game(self):

        self.replay_buffer.new_game()

    def init_neural_network(self):
        if (self.random_player or self.manual or self.perfect):
            return

        size_sq = self.board_size ** 2
        self.model = mlp(size_sq * 2,size_sq,2,200)

        if not os.path.exists(self.model_folder):
            os.makedirs(self.model_folder)
        else:
            self.model.load_weights(self.model_name)

        if os.path.exists(self.epsilon_path):
            f = open(self.epsilon_path,"r")
            self.epsilon = float(f.readline())
            f.close()

    def is_user_win(self,state,user):
        assert(user in [0,1])
        for i in range(0,self.board_size):
            curr_col = state[:,i]
            curr_row = state[i,:]
            if len(curr_col[curr_col == (user + 1)]) == self.board_size:
                return(True)
            if len(curr_row[curr_row == (user + 1)]) == self.board_size:
                return(True)
        diag = state.diagonal()
        if len(diag[diag == (user + 1)]) == self.board_size:
            return(True)
        diag = np.rot90(state).diagonal()
        if len(diag[diag == (user + 1)]) == self.board_size:
            return(True)
        return(False)

    def get_num_wins(self,state,user):
        count = 0
        local_state = np.copy(state)
        for x in range(0,self.board_size):
            for y in range(0,self.board_size):
                if local_state[x][y] == 0:
                    local_state[x][y] = user + 1
                    if self.is_user_win(local_state,user):
                        count += 1
                    local_state[x][y] = 0
        return(count)

    def get_my_fork(self,state):
        local_state = np.copy(state)
        for x in range(0,self.board_size):
            for y in range(0,self.board_size):
                if local_state[x][y] == 0:
                    local_state[x][y] = self.user + 1
                    if self.get_num_wins(local_state,self.user) > 1:
                        return([(x,y)])
                    local_state[x][y] = 0
        return([])

    def can_user_win(self,state,user):
        local_state = np.copy(state)
        for x in range(0,self.board_size):
            for y in range(0,self.board_size):
                if local_state[x][y] == 0:
                    local_state[x][y] = user + 1
                    if self.is_user_win(local_state,user):
                        return([(x,y)])
                    local_state[x][y] = 0
        return([])

    def get_other_fork(self,state):
        local_state = np.copy(state)
        prohibited_list = []
        for x in range(0,self.board_size):
            for y in range(0,self.board_size):
                if local_state[x][y] == 0:
                    local_state[x][y] = self.user + 1
                    other_user = (self.user + 1) % 2


                    wining_pos = self.can_user_win(local_state,self.user)
                    if len(wining_pos) > 0:
                        local_state[wining_pos[0][0]][wining_pos[0][1]] = other_user + 1
                        if self.get_num_wins(local_state,other_user) > 1:     
                            prohibited_list.append((x,y))
                        local_state[wining_pos[0][0]][wining_pos[0][1]] = 0
                    else:
                        for i in range(0,self.board_size):
                            for j in range(0,self.board_size):
                                if local_state[i][j] == 0:
                                    local_state[i][j] = other_user + 1
                                    if self.get_num_wins(local_state,other_user) > 1:     
                                        prohibited_list.append((x,y))  
                                    local_state[i][j] = 0                             
                    local_state[x][y] = 0
        return(prohibited_list)

    def get_action(self,state):
        if self.perfect:
            self_tile_code = 1 if (self.user == 0) else 2
            other_tile_code = 2 if (self.user == 0) else 1 

            prohibited_moves = []
            ## Can i win?
            winining_pos = self.can_user_win(state,self.user)


            if len(winining_pos) > 0:
                return(winining_pos[0])

            ## Can other person win?
            winining_pos = self.can_user_win(state,(self.user + 1)%2)
            if len(winining_pos) > 0:
                return(winining_pos[0])


            my_fork_list = self.get_my_fork(state)
            if len(my_fork_list)>0:
                return(my_fork_list[0])

            other_fork_list = self.get_other_fork(state)
            for other_fork in other_fork_list:
                if other_fork not in prohibited_moves:
                    prohibited_moves.append(other_fork)


            if np.count_nonzero(state) != 0:
                if state[1][1] == 0:
                    return(1,1)

            ## Get empty corners
            empty_corners = []
            for i in [0,2,6,8]:
                x = int(math.floor(i / self.board_size))
                y = i % self.board_size
                if (state[x][y] == 0) and ((x,y) not in prohibited_moves):
                    empty_corners.append(i)
            if len(empty_corners) > 0:
                choice = np.random.choice(empty_corners)
                x = int(math.floor(choice / self.board_size))
                y = choice % self.board_size  
                return(x,y)

            ## Get center if its free
            if state[1][1] == 0:
                return(1,1)

            ## move to sides
            empty_sides = []
            for i in [1,3,5,7]:
                x = int(math.floor(i / self.board_size))
                y = i % self.board_size
                if state[x][y] == 0 and ((x,y) not in prohibited_moves):
                    empty_sides.append(i)
            if len(empty_sides) > 0:
                choice = np.random.choice(empty_sides)
                x = int(math.floor(choice / self.board_size))
                y = choice % self.board_size  
                return(x,y)                     

            print("no moves left !!")
            exit()

        if self.manual:
            user_input = int(input("Enter a move "))
            y = user_input % self.board_size
            x = int(math.floor(user_input / self.board_size))
            return((x,y))


        self_tile_code = 1 if (self.user == 0) else 2
        other_tile_code = 2 if (self.user == 0) else 1
        state_raveled = state.ravel()
        self_tiles = list(map(lambda x : 1 if (x == self_tile_code) else 0,state_raveled))
        other_tiles = list(map(lambda x : 1 if (x == other_tile_code) else 0,state_raveled))
        state = np.concatenate((self_tiles,other_tiles)).reshape(1,-1)
        choose_random = np.random.rand() < self.epsilon or \
                        self.random_player
        
        choose_random = False
        if choose_random:

            ## Find out which part of the board is empty by checking for zeros
            action_int = np.argwhere(state_raveled == 0).ravel().tolist()
            ## Randomly choose one of the empty tile
            action_int = np.random.choice(action_int)
            action_y = action_int % self.board_size
            action_x = int(math.floor(action_int/self.board_size))
            return(action_x,action_y)
        else:
            ## Using Neural network to make the decision
            act_values = self.model.predict(state)
            amin = np.amin(act_values[0])
            if amin > 0:
                amin = amin*-1
            ## Mark the tiles which are not empty as illegal state to go
            for i in range(0,len(state_raveled)):
                if state_raveled[i] > 0:
                    act_values[0][i] = 2*amin

            ## Choose an action which maximises the q value
            action_int = np.argmax(act_values[0])
            action_y = action_int % self.board_size
            action_x = int(math.floor(action_int/self.board_size))
            return(action_x,action_y)


    def learn(self,done):
        
        if done and not (self.random_player or self.manual or self.perfect):

            minibatch = self.replay_buffer.sample_batch(self.batch_size)
            states = minibatch['s']
            actions = minibatch['a']
            rewards = minibatch['r']
            next_states = minibatch['s2']
            done = minibatch['d']

            # q_before_list = []
            # for state in states:
            #     q_before = self.model.predict(state.reshape(1,-1))
            #     q_before_list.append(q_before)
            #     mod_state = np.zeros((1,self.board_size**2)).ravel()
            #     for i in range(0,self.board_size**2):
            #         mod_state[i] = 2 if state[i] == 1 else 0
            #         mod_state[i] = 1 if state[(self.board_size**2)+i] == 1 else mod_state[i]

            

            # Calculate the tentative target: Q(s',a)

            ## Certain actions in next_states are invalid. Code below
            ## Traverses through next state predictions and makes the q value of
            ## illegal actions to twice the min value for a next state
            next_states_mod = next_states[:][:,0:(self.board_size**2)] | next_states[:][:,(self.board_size**2):(2*(self.board_size**2))]
            valid_next_states = (next_states_mod == 0)
            next_state_predictions = self.model.predict(next_states)
            next_state_amax = []
            for i in range(0,next_state_predictions.shape[0]):
                first_one = True 
                for j in range(0,next_state_predictions.shape[1]):
                    if valid_next_states[i][j]:
                        if first_one:
                            max_value = next_state_predictions[i][j]
                        elif next_state_predictions[i][j] > max_value:
                            max_value = next_state_predictions[i][j]
                        first_one = False
                if first_one and not done[i]:
                    print("no eligible moves !!")
                    exit()
                if first_one:
                    next_state_amax.append(0)
                else:
                    next_state_amax.append(max_value)

            next_state_amax = np.array(next_state_amax)
            target = rewards + (1 - done) * 0.95 * next_state_amax
                         
            target_full = self.model.predict(states)

            target_full[np.arange(target_full.shape[0]), actions] = target

            self.model.fit(states,target_full,verbose=0,epochs=50)
            # j = 0
            # for state in states:
            #     q_after = self.model.predict(state.reshape(1,-1))
            #     mod_state = np.zeros((1,self.board_size**2)).ravel()
            #     for i in range(0,self.board_size**2):
            #         mod_state[i] = 2 if state[i] == 1 else 0
            #         mod_state[i] = 1 if state[(self.board_size**2)+i] == 1 else mod_state[i]
            #     for i in range(0,self.board_size**2):
            #         if mod_state[i] > 0:
            #             q_before_list[j][0][i] = np.nan
            #             q_after[0][i] = np.nan
            #     print(f"state {mod_state} action : {actions[j]} q_value_before {q_before_list[j]} q_value_after {q_after}")
            #     j+=1

            self.epsilon = self.epsilon * self.epsilon_decay
            if self.epsilon < self.epsilon_min:
                self.epsilon = self.epsilon_min
        
    def save_model(self):
        if not (self.random_player or self.manual or self.perfect):
            self.model.save_weights(self.model_name)
            f=open(self.epsilon_path,"w")
            f.write(str(self.epsilon))
            f.close()     

    def update_replay_buffer(self,dict_local):
        
        if (dict_local["rewards"] > 100) or (dict_local["rewards"] < -100):
            print(f"{self.user} got reward {dict_local['rewards']}")
            exit(0)
        if not (self.random_player or self.manual or self.perfect):
            state_raveled = dict_local["curr_state"].ravel()

            self_tile_code = 1 if (self.user == 0) else 2
            other_tile_code = 2 if (self.user == 0) else 1

            self_tiles = list(map(lambda x : 1 if (x == self_tile_code) else 0,state_raveled))
            other_tiles = list(map(lambda x : 1 if (x == other_tile_code) else 0,state_raveled))
            state = np.concatenate((self_tiles,other_tiles)).reshape(1,-1)

            state_raveled = dict_local["next_state"].ravel()
            self_tiles = list(map(lambda x : 1 if (x == self_tile_code) else 0,state_raveled))
            other_tiles = list(map(lambda x : 1 if (x == other_tile_code) else 0,state_raveled))
            next_state = np.concatenate((self_tiles,other_tiles)).reshape(1,-1)

            bits_change = np.count_nonzero(next_state[0] & ~state[0])
            if (bits_change not in [1,2]):
                pprint(f"next state and curr state are wrong !!")
                pprint(curr_state)
                pprint(state)
                pprint(next_state)
                pprint(self.user)
                exit()

            reward = dict_local["rewards"]

            action = self.board_size * dict_local["action"][0] + dict_local["action"][1]
            done = 1 if dict_local["done"] else 0
            
            self.replay_buffer.store(state, action, reward, next_state, done)

    
    def save_buffer(self):
        if not (self.random_player or self.manual or self.perfect):
            self.replay_buffer.save_buffer(self.replay_data_name)

    
board_size = 3
env_inst = env(size=board_size) 
display = False

if display:
    env_inst.display_board()

agents = []
agents.append(agent(board_size=board_size,user=0,batch_size=100))
agents.append(agent(board_size=board_size,user=1,batch_size=100))



prev_results = None

draw = 0
user0_win = 0
user1_win = 0

first_user = 0
second_user = 1
state_dict = []
state_dict.append({})
state_dict.append({})

f = open("temp","r")
statistics = json.load(f)
f.close()
game_info = {}
for key in statistics.keys():
    game_info.update({key : {"user"       : statistics[key]["user"], 
                            "count"       : 0,
                            "board_data"  : np.array(statistics[key]["board_data"])}})

unique_games = 0
unique_games_list = []
for i in range(0,1):
    os.system("clear")
    pprint(f"Play count {i} epsilon {agents[0].epsilon:.3f} {agents[1].epsilon:.3f} {len(agents[0].replay_buffer)} {len(agents[1].replay_buffer)} unique_games : {unique_games}")
    agents[0].new_game()
    agents[1].new_game()


    if prev_results != None:
        draw_per = (draw/i)*100
        user0_per = (user0_win/i)*100
        user1_per = (user1_win/i)*100
        pprint(f"draw {draw_per:.3f} user0 {user0_per:.3f} user1 {user1_per:.3f}")
    first_move = True
    env_inst.reset()

    
    curr_game_info = {"user"       : first_user,
                      "board_data" : [np.zeros((board_size,board_size)).ravel()]}
    while True:
        if first_move:
            curr_state = np.zeros((board_size,board_size))
        else:
            curr_state = state_dict[second_user]["next_state"]

        (x,y) = agents[first_user].get_action(curr_state)
        state_dict[first_user] = env_inst.perform_action(x,y,first_user)
        curr_game_info["board_data"].append(np.copy(state_dict[first_user]["next_state"].ravel()))
        

        if display:
            os.system("clear")
            env_inst.display_board()
            #time.sleep(4)


        if state_dict[first_user]["done"]:
            dict_local = {"curr_state" : np.copy(state_dict[first_user]["curr_state"]),
                          "action"     : state_dict[first_user]["action"],
                          "next_state" : np.copy(state_dict[first_user]["next_state"]),
                          "rewards"    : state_dict[first_user][f"rewards{first_user}"],
                          "done"       : True}
            agents[first_user].update_replay_buffer(dict_local)
            agents[first_user].learn(True)

        if not first_move:
            dict_local = {"curr_state" : np.copy(state_dict[second_user]["curr_state"]),
                          "action"     : state_dict[second_user]["action"],
                          "next_state" : np.copy(state_dict[first_user]["next_state"]),
                          "rewards"    : state_dict[first_user][f"rewards{second_user}"],
                          "done"       : state_dict[first_user]["done"]}
            agents[second_user].update_replay_buffer(dict_local)
            agents[second_user].learn(state_dict[first_user]["done"])

        if state_dict[first_user]["done"]:
            prev_results = {"user"  : first_user,
                            "win"   : state_dict[first_user]["win"],
                            "draw"  : state_dict[first_user]["draw"],
                            "wrong" : state_dict[first_user]["wrong"]}
            if state_dict[first_user]["draw"]:
                draw += 1
            elif state_dict[first_user]["win"]:
                if first_user == 0:
                    user0_win += 1
                else:
                    user1_win += 1
            else:
                if second_user == 0:
                    user0_win += 1
                else:
                    user1_win += 1
            break

        first_move = False
        ## Machine move
        
        (x,y) = agents[second_user].get_action(state_dict[first_user]["next_state"])
        state_dict[second_user] = env_inst.perform_action(x,y,second_user)
        curr_game_info["board_data"].append(np.copy(state_dict[second_user]["next_state"].ravel()))


        if display:
            os.system("clear")
            env_inst.display_board()
            #time.sleep(4)

        if state_dict[second_user]["done"]:
            dict_local = {"curr_state" : np.copy(state_dict[second_user]["curr_state"]),
                          "action"     : state_dict[second_user]["action"],
                          "next_state" : np.copy(state_dict[second_user]["next_state"]),
                          "rewards"    : state_dict[second_user][f"rewards{second_user}"],
                          "done"       : True}
            agents[second_user].update_replay_buffer(dict_local)
            agents[second_user].learn(True)


        dict_local = {"curr_state" : np.copy(state_dict[first_user]["curr_state"]),
                      "action"     : state_dict[first_user]["action"],
                      "next_state" : np.copy(state_dict[second_user]["next_state"]),
                      "rewards"    : state_dict[second_user][f"rewards{first_user}"],
                      "done"       : state_dict[second_user]["done"]}
        agents[first_user].update_replay_buffer(dict_local)
        agents[first_user].learn(state_dict[second_user]["done"])

        if state_dict[second_user]["done"]:
            prev_results = {"user"  : 1,
                            "win"   : state_dict[second_user]["win"],
                            "draw"  : state_dict[second_user]["draw"],
                            "wrong" : state_dict[second_user]["wrong"]}
            if state_dict[second_user]["draw"]:
                draw += 1
            elif state_dict[second_user]["win"]:
                if second_user == 0:
                    user0_win += 1
                else:
                    user1_win += 1
            else:
                if first_user == 0:
                    user0_win += 1
                else:
                    user1_win += 1
            break
    # first_user = (first_user + 1) % 2
    # second_user = (second_user + 1) % 2
    found = False
    for key in game_info.keys():
        if game_info[key]["user"] == curr_game_info["user"]:
            if np.array_equal(game_info[key]["board_data"],np.array(curr_game_info["board_data"])):
                found = True
                break
    if found:
        if game_info[key]["count"] == 0:
            unique_games += 1
        game_info[key]["count"] += 1
    else:
        unique_games += 1
        game_info.update({f"{i}" : {"count" : 1,
                                   "user" : curr_game_info["user"],
                                   "board_data" : np.array(curr_game_info["board_data"])}})

    unique_games_list.append(unique_games)


count_frame = []
statistics = {}
i = 0
for key in game_info.keys():
    count_frame.append({"game_num" : key,"count" : game_info[key]["count"]})
    statistics.update({f"{i}" : {"game_num"   : key,
                                 "count"      : game_info[key]["count"],
                                 "user"       : game_info[key]["user"],
                                 "board_data" : game_info[key]["board_data"].tolist()}})
    i +=1

f=open("temp","w")
json.dump(statistics,f)
f.close()


# count_frame = pd.DataFrame(count_frame)
# count_frame.plot(kind = "bar")
# plt.show()

# unique_game_frame = pd.DataFrame(unique_games_list,columns=["unique_games"])
# unique_game_frame.plot()
# plt.show()

highest_game_count = 0

for key in game_info.keys():
    if game_info[key]["count"] > highest_game_count:
        highest_key = key 
        highest_game_count = game_info[key]["count"]

pprint(game_info[highest_key])



#agents[0].save_model()
#agents[1].save_model()
#agents[0].save_buffer()
#agents[1].save_buffer()




