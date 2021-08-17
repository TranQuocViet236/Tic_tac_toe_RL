import numpy as np
import pickle

BOARD_ROWS = 3
BOARD_COLS = 3
class State:
    def __init__(self, p1, p2):
        self.board = np.zeros((BOARD_ROWS,  BOARD_COLS))
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        #init p1 player first
        self.playerSymbol = 1

    #get unique hash of current board state
    def getHash(self):
        self.boardHash = str(self.board.reshape(BOARD_ROWS*BOARD_COLS))
        return self.boardHash
    #Trả về danh sách các nước có thể đi
    def availablePositions(self):
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if self.board[i,j] == 0:
                    positions.append((i,j)) # need to be tuple

        return positions

    #Cập nhật lại lên bàn cờ vị trí của người đặt quân
    def updateState(self, position):
        self.board[position] = self.playerSymbol
        #switch to another player
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1

    def winner(self):
        #kiểm tra theo dòng
        for i in range(BOARD_ROWS):
            if sum(self.board[i,:]) == 3:
                self.isEnd = True
                return 1
            if sum(self.board[i,:]) == -3:
                self.isEnd = True
                return -1
        #Kiểm tra theo cột
        for i in range(BOARD_COLS):
            if sum(self.board[i, :]) == 3:
                self.isEnd = True
                return 1
            if sum(self.board[i, :]) == -3:
                self.isEnd = True
                return -1
        #Kiểm tra theo đường chéo chính và đường chéo phụ
        diag_sum1 = sum([self.board[i,i] for i in range(BOARD_COLS)])
        diag_sum2 = sum([self.board[i, BOARD_COLS - i -1] for i in range(BOARD_COLS)])

        diag_sum = max(abs(diag_sum2), abs(diag_sum1))
        #Lấy trị tuyệt đối của các nước đi, nếu bằng 3 nghĩa là có người chơi chiến thắng
        if diag_sum == 3:
            self.isEnd = True
            if diag_sum1 == 3 or diag_sum2 == 3:
                return 1
            else:
                return -1

        #Kiểm tra xem còn nước đi hay không
        if len(self.availablePositions()) == 0:
            self.isEnd = True
            return 0
        #not end
        self.isEnd = False
        return None
    # only when game ends
    def giveReward(self):
        result = self.winner()
        # backpropagate reward
        if result == 1:
            self.p1.feedReward(1)
            self.p2.feedReward(0)
        elif result == -1:
            self.p1.feedReward(0)
            self.p2.feedReward(1)
        else:
            self.p1.feedReward(0.1)
            self.p2.feedReward(0.5)

        #Khi cờ hòa xem như người đi trước thua, nên hệ số lúc này có thể là
        # 0.1 - 0.5 hoặc tùy ý
    def reset(self):
        self.board = np.zeros((BOARD_ROWS,BOARD_COLS))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol =1

    def play(self, rounds = 100):
        for i in range(rounds):
            if i % 1000 ==0:
                print(f"Rounds {i}")
            while not self.isEnd:
                #Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
                #take action and update board state
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                #check board status if it is end

                win = self.winner()
                if win is not None:
                    #self.showBoard()
                    #ended with p1 either win or draw
                    self.giveReward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break
                else:
                    #player 2
                    positions = self.availablePositions()
                    p2_action = self.p2.chooseAction(positions, self.board, self.playerSymbol)
                    self.updateState(p2_action)
                    self.board_hash = self.getHash()
                    self.p2.addState(board_hash)

                    win = self.winner()
                    if win is not None:
                        #self.showBoard()
                        #ended with p2 either win or draw
                        self.giveReward()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break
    def play2(self):
        while not self.isEnd:
        #Player 1
            positions = self.availablePositions()
            p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
            #take action and update board state
            self.updateState(p1_action)
            self.showBoard()
            #check the board status if it is end
            win = self.winner()
            if win is not None:
                if win == 1:
                    print(self.p1.name, "win!")
                else:
                    print("tie!")
                self.reset()
            else:
                #Player
                positions = self.availablePositions()
                p2_action = self.p2.chooseAction(positions)

                self.updateState(p2_action)
                self.showBoard()
                win = self.winner()

                if win is not None:
                    if win == -1:
                        print(self.p2.name, "win")
                    else:
                        print("tie!")
                    self.reset()
                    break
    def showBoard(self):
        #p1: x p2: o
        for i in range(0, BOARD_ROWS):
            print('--------------')
            out = '| '
            for j in range(0, BOARD_COLS):
                token = ""
                if self.board[i,j] == 1:
                    token = 'x'
                if self.board[i,j] == -1:
                    token = 'o'
                if self.board[i,j] == 0:
                    token = " "
                out += token + " | "
            print(out)
        print('--------------')
    # def chooseAction(self, positions, currents_board, symbol):
    #     randValue = np.random.uniform(0, 1)
    #     value_max = value = -999
    #     if randValue > self.exp_rate:
    #
    #         for p in positions:
    #             next_board = currents_board.copy()
    #             next_board[p] = symbol
    #             next_boardHash = self.getHash(next_board)
    #             value = -999 if \
    #                 self.states_values.get(next_boardHash) is None else \
    #                 self.states_values.get(next_boardHash)
    #             # print("Value", value)
    #             if value >= value_max:
    #                 value_max = value
    #                 action = p
    #     if value_max == -999:
    #         # take random action
    #         idx = np.random.choice(len(positions))
    #         action = positions[idx]
    #     return action


    # Thiết lập trạng thái người chơi. Người chơi cần có các phương thức sau:
    # - Chọn nước đi dựa trên trạng thái hiện tại của bàn cờ
    # - Lưu lại trạng thái ván cờ
    # - Cập nhật lại giá trị trạng thái sau mỗi ván
    # - Lưu và load các trọng số lên
class Player:
    def __init__(self, name, exp_rate=0.2):
        self.name = name
        self.states = []  # record all positions taken
        self.lr = 0.2
        self.exp_rate = exp_rate
        self.decay_gamma = 0.9
        self.states_values = {}  # state -> values

        # Chọn nước đi
    def getHash(self, board):
        boardHash = str(board.reshape(BOARD_ROWS*BOARD_COLS))
        return boardHash

    def chooseAction(self, positions, currents_board, symbol):
        randValue = np.random.uniform(0, 1)
        value_max = value = -999
        if randValue > self.exp_rate:

            for p in positions:
                next_board = currents_board.copy()
                next_board[p] = symbol
                next_boardHash = self.getHash(next_board)
                value = -999 if \
                    self.states_values.get(next_boardHash) is None else \
                    self.states_values.get(next_boardHash)
                # print("Value", value)
                if value >= value_max:
                    value_max = value
                    action = p
        if value_max == -999:
            # take random action
            idx = np.random.choice(len(positions))
            action = positions[idx]
        return action

    #append a hash state
    def addState(self, state):
        self.states.append(state)

    #at the end of game, backpropagate and update states value
    def feedReward(self, reward):
        for st in reversed(self.states):
            if self.states_values.get(st) is None:
                self.states_values[st] = 0
            self.states_values[st] += self.lr*(self.decay_gamma*reward - self.states_values[st])
            reward = self.states_values[st]

    def reset(self):
        self.states = []

    def savePolicy(self):
        fw = open('policy_'+ str(self.name), 'wb')
        pickle.dump(self.states_values, fw)

        fw.close()

    def loadPolicy(self, file):
        fr = open(file, 'rb')
        self.states_values = pickle.load(fr)
        fr.close()

class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def chooseAction(self, positions):
        while True:
            row = int(input("Input your action row: "))
            col = int(input("Input you action colum: "))
            action = (row, col)

            if action in positions:
                return action
    # append a hash state
    def addState(self, state):
        pass

    #at the end of game, backpropagate and update states values
    def feedReward(self, reward):
        pass
    def reset(self):
        pass

if __name__ == '__main__':
    #training
    p1 = Player("p1")
    p2 = Player("p2")

    st = State(p1, p2)
    print("trainning...")
    st.play(100000)

    p1.savePolicy()

    #play with human
    p1 = Player("computer", exp_rate=0)
    p1.loadPolicy("policy_p1")

    p2 = HumanPlayer('human')

    st = State(p1, p2)
    st.play2()

