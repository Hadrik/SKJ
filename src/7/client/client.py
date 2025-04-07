import random
from xmlrpc.client import ServerProxy
import visualizer
import xml.etree.ElementTree as ET

class Agent:

    def __init__(self, filename):
        # TODO 1     - load data from the XML configuration file (filename is in the parameter)
        # TODO 2     - create instance variables (login, data, visualizer, gameserver)
        # login      - load from XML file (tag 'login')
        tree = ET.parse(filename)
        self.login = tree.find('login').text
        self.data = []
        self.visualizer = visualizer.Visualizer()
        self.gameserver = ServerProxy(tree.find('url').text)
        # data       - an empty list, where data from server will be stored
        # visualizer - instance of the visuzlizer.Visualizer class
        # gameserver - connect to the remote XML-RPC server (url is provided in the XML file, tag 'url')
        # TODO 3     - call method 'add_player' on the server with login as the parameter (use instance variable 'self.login')
        self.gameserver.add_player(self.login)

    def action(self):
        # TODO 4 - Call 'make_action' method on the XML-RPC server.
        # The method has 3 parameters (login, action_name, parameters).
        # All three parameters are strings. Call the 'look' method on the server,
        # to take a look around the player, without NY parameter (empty string).
        # Every action returns a list of strings, where each row represents one
        # row from the surrounding area of the player.
        # Each string is 11-characters in length and there are 22 rows.
        # First 11 elements of the list represent the agent's environment
        # and other 11 elements of his surroundings
        # (so far, only "p" character is present to represent other agents).
        # The player is in this surrounding at the position [5][5] (5th row, 5th character).
        # Objects on the same position can be sought at the coordinates [5 + 11] [5].
        # "~" water
        # " " grass
        # "*" road
        # "t" tree
        # "o" rock (wall)
        # "f" tiled floor
        # "p" player
        self.data = self.gameserver.make_action(self.login, 'look', '')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        for x in self.data:
            s += x + "\n"
        return s

    def save_data(self):
        # TODO 6 - Store data into the 'data.txt' filename.
        with open('data.txt', 'w') as f:
            for line in self.data:
                f.write(line + '\n')

class AgentRandom(Agent):
    # TODO 7 - This agent will extend from the previous agent and
    # reimplement (override) the 'action' method so that the action will be 'move' and
    # the passed parameter will be one the directions: 'north', 'west', 'south', 'east'.
    # These directions will be randomly selected
    # (find the appropriate method from the random package).
    def action(self):
        direction = random.choice(['north', 'west', 'south', 'east'])
        self.gameserver.make_action(self.login, 'move', direction)

class AgentLeftRight(Agent):
    # TODO 8 - This agent will be moving just to the left until it hits a barrier.
    # Then it rurn to the right and moves until it hits the barrier again.
    # It repeats such behavior.
    direction = 'east'
    def action(self):
        super().action()
        if self.direction == 'east':
            if self.data[5][6] == 'o' or self.data[5][6] == 't' or self.data[5][6] == '~':
                self.direction = 'west'
        else:
            if self.data[5][4] == 'o' or self.data[5][4] == 't' or self.data[5][4] == '~':
                self.direction = 'east'

        self.gameserver.make_action(self.login, 'move', self.direction)

def main():
    agent = None
    try:
        #agent = Agent(login, 'config.xml')
        #agent = AgentRandom(login, 'config.xml')
        agent = AgentLeftRight('config.xml')
        while agent.visualizer.running:
            agent.action()
            print(agent)
        else:
            agent.gameserver.make_action(agent.login, 'exit', '')

        agent.save_data()
    except KeyboardInterrupt:
        agent.gameserver.make_action(agent.login, 'exit', '')


if __name__ == '__main__':
    main()
