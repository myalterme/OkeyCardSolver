import time,math,random

SIMULATION_NUM = 1
MAX_WIN_VALUE = 500 #Maximum theoretcal value to be divided by each win
UCT_CONSTANT = 0.5 #Constant from uct formula to balnce exploration and exploitation
#TIME = 0.5 #sec per round
DEBUG = False

def Log(message):
    if DEBUG:
        print(message)


def solve(layout,time):
    mcts = MCTS()
    return mcts.solve(layout,time)

class MCTS:
    class Node:
        def __init__(self,layout,father):
            self.childs = []
            self.father = father
            self.numSimulations = 0
            self.numPoints = 0
            if father != 0:
                self.costFromRoot = father.costFromRoot + layout.getCost()
            else:
                self.costFromRoot = 0            
            self.layout = layout
            
        def addChild(self,layout):
            node = MCTS.Node(layout,self)
            self.childs.append(node)
            
        #Add all childs to current node if there are no childs yet
        def addAllChilds(self):
            if len(self.childs) != 0:
                return
            arr = self.layout.getChildNodes()
            for layout in arr:
                self.addChild(layout)
        
        #Add wins and simulations to the current node
        def addWins(self, value,numSimulations):
            self.numPoints += value
            self.numSimulations +=numSimulations
        
        def getLayoutCost(self):
            return self.layout.getCost()

        #If the childs are from a random turn return a random child, else return a child based on the UCT formula 
        def getBestChild(self):

            best_child = 0
            best_value =-1

            arr_len = len(self.childs)

            if arr_len == 0:
                return 0

            if self.layout.hasRandomChilds() == True:
                randInt = random.randint(0,arr_len-1)
                return self.childs[randInt]

            for child in self.childs:
                value = child.UCTFormula()
                if value > best_value:
                    best_value = value
                    best_child = child
            
            return best_child
        
        
        def UCTFormula(self):
            first_argument = float(self.numPoints)/float(self.numSimulations * MAX_WIN_VALUE)
            second_argument = float(UCT_CONSTANT)*math.sqrt((math.log(self.father.numSimulations)/float(self.numSimulations)))
            return first_argument + second_argument
        
        def __repr__(self):
            form_result = 0
            if self.father != 0:
                form_result = self.UCTFormula()
            result = "Simulations: " + str(self.numSimulations)+"\nNumPoints: "+str(self.numPoints)+"\nSelection Value: " + str(form_result) + "\nNumber of childs: " + str(len(self.childs)) + "\nCost From Root: " + str(self.costFromRoot) + "\nNode: " + str(self.layout)
            return result


    def solve(self,startLayout,timeoutSec):
        self.rootNode = MCTS.Node(startLayout,0)
        if self.rootNode.layout.isFinalNode() == True:
            Log("[MCTS] -Root Node is final node")
            return self.rootNode.layout
        
        currentTime = time.time()
        endTime = currentTime+timeoutSec

        self.selectionTime = 0.0
        self.selectionTimes = 0
        self.simulationTime = 0.0
        self.simulationsDone = 0
        self.depth = 0

        self.expansion(self.rootNode)
        if len(self.rootNode.childs) == 0:
            Log("[MCTS] - Error - Root Node has no childs")
            return self.rootNode.layout

        while(time.time()<endTime):
            currNode = self.selection()
            #self.expansion(currNode)
            result = self.simulation(currNode)
            self.simulationsDone+=1
            self.backPropagation(currNode,result,1)
        #print(self.rootNode.childs)
        #print("\n")
        
        best_child = self.rootNode.childs[0]
        value =best_child.numPoints/best_child.numSimulations
        for child in self.rootNode.childs:
            curr_value = float(child.numPoints)/float(child.numSimulations)
            if curr_value > value:
                value = curr_value
                best_child = child
        Log("[MCTS] - Depth Searched: " + str(self.depth) + " Simulations Done: " + str(self.simulationsDone))
        Log("[MCTS] - Selection Time: " + str(self.selectionTime) + " s")
        Log("[MCTS] - Simulation Time: " + str(self.simulationTime) + " s")
        Log("[MCTS] - Selection Times Executed: " + str(self.selectionTimes))
        Log("[MCTS] - Time elapsed: " + str(time.time() - currentTime) + " seconds \n[MCTS] - Best Child: " + str(best_child))
        Log("\n")
        return best_child.layout
        
            
    
    def backPropagation(self, node , points, numSimulations):
        node.addWins(points,numSimulations)
        if node.father != 0:
            self.backPropagation(node.father , points+node.getLayoutCost(), numSimulations)
    
    def expansion(self, node):
        node.addAllChilds()
        arr = node.childs
        for node_child in arr:     
            sim_points = 0     
            for n in xrange(0,SIMULATION_NUM):
                sim_points +=self.simulation(node_child)
            self.backPropagation(node_child,sim_points,SIMULATION_NUM)

    def simulation(self,node):
        curr = time.time()
        lastLayout = node.layout
        cost = node.costFromRoot
        while lastLayout.isFinalNode() == False:
            lastLayout = lastLayout.getOneRandomChild()
            cost += lastLayout.getCost()
        self.simulationsDone += 1
        self.simulationTime += (time.time()-curr)
        return cost
        
        
    def selection(self):
        curr = time.time()
        currentNode = self.rootNode
        self.selectionTimes += 1
        i = 0
        while len(currentNode.childs)>0:
            i+=1
            currentNode = currentNode.getBestChild()
        if i > self.depth:
            self.depth = i
        self.selectionTime += (time.time() - curr)
        return currentNode
                
