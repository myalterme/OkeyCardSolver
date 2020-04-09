#execfile('or.py')


# Okey-game simulator:
# To execute it, you can use the command execfile('or.py') in the python shell,
# that way, the variables are kept after each execution of the script

# You can use DEBUG = True to get play infos,
# but you should only do that if you only play a small number of games

# At the bottom you find a for-loop, you can use this to simulate many games at once
# and see how your version of the bot performs, just keep in mind to turn DEBUG off for this
# otherwise the print output eats up all the runtime

# or.py is the simple version of the game,
# o.py is the version containing all the current optimizations
import MCTS
global HOOKED
global COLORS
global HAND
global CARDS
global CARDS_LEFT
global SCORE
global FINISH
global USED_CARDS

def getRnd(min, max):
	import random
	return random.randint(min,max)


RESULTS = [0,0,0]
DEBUG = False
SCORE_SUM = 0
SIMULATIONS = 1
YELLOW = 30
RED = 10
BLUE = 20
COLORS = {
	10: "Red",
	20: "Blue",
	30: "Yellow"
}
TIME = 1

import random, math, itertools, time

class Card:
    def __init__(self,number,color):
        self.color = color
        self.number = number

    def __hash__(self):
        return self.color ^ self.number
    
    def __eq__(self, other):
        if not isinstance(other,Card):
            return False
        return self.color == other.color and self.number == other.number
    
    def __repr__(self):
        return str("("+ str(self.number) + ", " + COLORS[self.color] +")")

#class LayoutInterface:
#    @abstractmethod
#    def getCost()
#
#   @abstractmethod
#    def getChildNodes()
#    
#    @abstractmethod
#    def hasRandomChilds()
#    
#    @abstractmethod
#    def isFinalNode()
#
#    @abstractmethod
#    def getOneRandomChild()


def GetPointsForSequence(sequence):
    if len(sequence) < 3:
        return 0
    num1 = sequence[2].number
    num2 = sequence[1].number
    num3 = sequence[0].number
    col1 = sequence[2].color
    col2 = sequence[1].color
    col3 = sequence[0].color
    if num1 == num2 and num2 == num3:
		n = num1
		if n == 1: return 20
		if n == 2: return 30
		if n == 3: return 40
		if n == 4: return 50
		if n == 5: return 60
		if n == 6: return 70
		if n == 7: return 80
		if n == 8: return 90
    sameColor = False
    if col1 == col2 and col2 == col3:
		sameColor = True
    if num1 == 1 and num2 == 2 and num3 == 3:
		if sameColor == True:
			return 50
		else:
			return 10
    if num1 == 2 and num2 == 3 and num3 == 4:
		if sameColor == True:
			return 60
		else:
			return 20
    if num1 == 3 and num2 == 4 and num3 == 5:
		if sameColor == True:
			return 70
		else:
			return 30
    if num1 == 4 and num2 == 5 and num3 == 6:
		if sameColor == True:
			return 80
		else:
			return 40
    if num1 == 5 and num2 == 6 and num3 == 7:
		if sameColor == True:
			return 90
		else:
			return 50
    if num1 == 6 and num2 == 7 and num3 == 8:
		if sameColor == True:
			return 100
		else:
			return 60
    return 0

################################ END MCTS #######################################



################################ OKEY LAYOUT NODE ##############################
class OkeyLayout:
    
    
    def __init__(self,inTable,cardsInDeck,cardsInGrave):
        self.cardsInGrave = cardsInGrave
        self.cardsInTable = inTable
        self.sortTable()
        self.cardsInDeck = cardsInDeck
        self.combinationUsed = []


    def copy(self):
        deck = list(self.cardsInDeck)
        table = list(self.cardsInTable)
        grave = list(self.cardsInGrave)
        return OkeyLayout(table,deck,grave)
    
    def sortTable(self):
        self.cardsInTable.sort(key = lambda x: x.number)

    def isFinalNode(self):
        if len(self.cardsInDeck) == 0:
            if len(self.getOkeyPossibleSequences()) == 0:
                return True
        return False
    
    def hasRandomChilds(self):
        if len(self.cardsInTable)<5 and len(self.cardsInDeck) != 0:
            return True

        return False

    def GetPointsForPossibility(self):
        global GetPointsForSequence
        return GetPointsForSequence(self.combinationUsed)


    #Get a list of all cards wich have the same number of the card in argument
    def getEqualNumbers(self,card):
        lst = []
        for i in xrange(0,len(self.cardsInTable)):
            curr_card = self.cardsInTable[i]
            if curr_card.number == card.number and card.color != curr_card.color:
                 lst.append(curr_card)
            if curr_card.number > card.number:
                return lst 
        return lst
    
    def removeRepeated(self,arr):
        result = []
        if(len(arr)<2):
            return result
        result.append(arr[0])
        
        for i in xrange(1,len(arr)):
            if arr[i].number != arr[i-1].number:
                result.append(arr[i])
        return result

    def setCardsSequenceDone(self,sequence):
        self.combinationUsed.append(sequence[0])
        self.combinationUsed.append(sequence[1])
        self.combinationUsed.append(sequence[2])
    
    #Gets every possible Sequence
    def getOkeyPossibleSequences(self):
        tableNoRepeated = self.removeRepeated(self.cardsInTable)
        tableSize = len(tableNoRepeated)
        lst = []
        if len(self.cardsInTable) == 0:
            return lst
        
        #Sequences
        for i in xrange(2,tableSize):
            found = False
            curr_card = []
            curr_card.append(tableNoRepeated[i])
            last_card = tableNoRepeated[i].number

            for j in xrange(i-1,-1,-1):                
                if (last_card -1) == tableNoRepeated[j].number:
                    last_card = tableNoRepeated[j].number
                    curr_card.append(tableNoRepeated[j])  
                else:
                    break
                  
                if len(curr_card) == 3:
                    lst.append(curr_card)
                    found = True
                    break
                
            #Deal with sequences with equal numbers
            if(found == True):
                combinations = []
                for i in xrange(0,len(curr_card)):
                    sequences_left = []
                    equals = self.getEqualNumbers(curr_card[i])
                    for equal_card in equals:
                        result_list = list(curr_card)
                        result_list[i] = equal_card
                        sequences_left.append(result_list)
                        for comb_set in combinations:
                            result_list = list(comb_set)
                            result_list[i] = equal_card
                            sequences_left.append(result_list)
                    combinations.extend(sequences_left)
                lst.extend(combinations)
        
        #Equal Numbers
        tableSize = len(self.cardsInTable)
        
        curr_card = []
        currNumber = self.cardsInTable[0].number
        for x in xrange(1,len(self.cardsInTable)):
            card = self.cardsInTable[x]
            if card.number == self.cardsInTable[x-1].number:
                if len(curr_card) == 0:
                    curr_card.append(self.cardsInTable[x-1])
                curr_card.append(card)
            else:
                curr_card = []
                
            if len(curr_card) == 3:
                lst.append(curr_card)
                break
            
        return lst

    #by object
    def RemoveFromDeckByObject(self, card):
        if len(self.cardsInTable) >= 5:
            raise Exception("Table full")
        self.cardsInDeck.remove(card)
        self.cardsInTable.append(card)
        self.sortTable()


    
    #by index
    def RemoveFromDeck(self, index_deck):
        card = self.cardsInDeck[index_deck]
        del self.cardsInDeck[index_deck]
        if(len(self.cardsInTable) >= 5):
            raise Exception('Cannot Remove Card')
        self.cardsInTable.append(card)
        self.sortTable()
    
    #by object
    def DiscardFromTable(self, card):
        self.cardsInTable.remove(card)
    
    #IMPORTANT FUNCTION: this function chose the next move for each simulation
    def getOneRandomChild(self):
        global heuristic

        numCardsInDeck = len(self.cardsInDeck)
        numCardsInTable = len(self.cardsInTable)
        cardsToDraw = numCardsInDeck
        if(5-numCardsInTable <cardsToDraw ):
            cardsToDraw = 5-numCardsInTable
        layout = self.copy()
        for x in xrange(0,cardsToDraw):
            rand = random.randint(0,len(layout.cardsInDeck)-1)
            layout.RemoveFromDeck(rand)
        
        mapping = {}
        #Changes here may have a significant improvement
        #Do Sequence Generation
        childNodes = layout.getSequenceChildNodes()
        if len(childNodes) <= 0:
            if len(layout.cardsInDeck) == 0:
                layout.final = True
                return layout

        
        childNodes.extend(layout.getDiscardChildNodes())
        childNodes.sort(key = lambda x: heuristic(x))
        #rand = random.random()
        #if rand >0.9:
        #    return childNodes.pop()

        return childNodes.pop()

        _sum = 0
        for child in childNodes:
            value = abs(heuristic(child))
            _sum+=value
            mapping[child] = value
        
        rand = random.randint(0,math.floor(_sum))
        #print(childNodes)
        #print(_sum)
        #print(rand)

        accumulate = 0
        for child in childNodes:
            accumulate += mapping[child]
            if rand <= accumulate:
                return child 
        #childNodes.sort(key = lambda x: heuristic(x))
        #print("Printing Sorted\n")
        #for node in childNodes:
        #    print(str(node) + " Fitness: " + str(heuristic(node)))

        raise Exception("Something went wrong")
    
    def getDiscardChildNodes(self):
        resultList = []
        for card in self.cardsInTable:
            layout = self.copy()
            layout.DiscardFromTable(card)
            layout.combinationUsed.append(card)
            resultList.append(layout)        
        return resultList
            

    def getSequenceChildNodes(self):
        resultList = []
        tableSequences = self.getOkeyPossibleSequences()
        for sequence in tableSequences:
            layout = self.copy()
            for card in sequence:
                layout.DiscardFromTable(card)

            layout.setCardsSequenceDone(sequence)
            resultList.append(layout)
        return resultList

    def getFillHandChildNodes(self):
        resultList = []
        numCardsInDeck = len(self.cardsInDeck)
        numCardsInTable = len(self.cardsInTable)
        cardsToDraw = numCardsInDeck
        if(5-numCardsInTable <cardsToDraw ):
            cardsToDraw = 5-numCardsInTable

        arr = itertools.combinations(self.cardsInDeck,cardsToDraw)

        for comb in arr:
            layout = self.copy()
            for card in comb:
                layout.RemoveFromDeckByObject(card)
            resultList.append(layout)
        
        return resultList


    def getCost(self):
        return self.GetPointsForPossibility()
    
    
    def getChildNodes(self):
        
        #sequences
        if self.hasRandomChilds() == True:
            return self.getFillHandChildNodes()
        else:
            result = self.getDiscardChildNodes()
            result.extend(self.getSequenceChildNodes())
            return result
        


    def __repr__(self):
        return str("Table"+ str(self.cardsInTable) + " Move" + str(self.combinationUsed)+" Cost: " + str(self.getCost()))

#GENETIC ATTEMPT
def GetAllSequencePoints(cards1,cards2,cards3):
    global YELLOW
    global BLUE
    global RED

    num = 0
    sequenceNum = 1
    if len(cards1)==0 or len(cards2)==0 or len(cards3)==0:
        raise Exception("Error")

    
    colorNum = {
        YELLOW : 0,
        BLUE : 0,
        RED : 0
    }
    
    for card in cards1:
        colorNum[card.color] +=1

    for card in cards2:
        colorNum[card.color] +=1

    for card in cards3:
        colorNum[card.color] +=1

    if colorNum[YELLOW] == 3:
        num+=1
    if colorNum[RED] == 3:
        num+=1
    if colorNum[BLUE] == 3:
        num+=1
    
    sequenceNum *= len(cards1)
    sequenceNum *= len(cards2)
    sequenceNum *= len(cards3)

    sequenceNum -= num

    yellow1 = Card(cards1[0].number,YELLOW)
    red1 = Card(cards1[0].number,RED)
    red2 = Card(cards2[0].number,RED)
    red3 = Card(cards3[0].number,RED)

    seq = [red3,red2,red1]

    pointsEqual = num*GetPointsForSequence(seq)
    seq[2] = yellow1
    pointsDifferent = sequenceNum*GetPointsForSequence(seq)
    #print("\nSequence Num: " + str(sequenceNum))
    #print("Equal Num: " + str(num))
    #print("Sequence: " + str(seq))
    #print("Points: " + str(pointsEqual+pointsDifferent))

    return pointsEqual+pointsDifferent


#Deck as to be ordered lowest to hightest
def getPointsFromCards(deck):
    points = 0
    sequence = []
    lastNum = 0
    index = 0
    i = 0
    while(i<len(deck)):
        card = deck[i]
        j = i
        cardEqual = []
        while(j < len(deck) and card.number == deck[j].number):
            cardEqual.append(deck[j])
            j+=1

        i = j
        if len(cardEqual)>0:
            sequence.append(cardEqual)
            if len(cardEqual)==3:
                points+=GetPointsForSequence(cardEqual)
        if len(sequence) >3:
            sequence.pop(0)
        
        if len(sequence) < 3:
            continue

        if sequence[0][0].number == sequence[1][0].number -1 and sequence[1][0].number == sequence[2][0].number -1:
            #print(sequence)
            points+=GetAllSequencePoints(sequence[0],sequence[1],sequence[2])
        else:
            sequence.pop(0)
    return points

#14.662, 0.402, 0.378

SEQUENCE_WEIGHT = 0.872
TABLE_WEIGHT = -0.02
DECK_WEIGHT =0.006

def setWeights(arr):
    global SEQUENCE_WEIGHT
    global DECK_WEIGHT
    global TABLE_WEIGHT

    SEQUENCE_WEIGHT = arr[0]
    TABLE_WEIGHT = arr[1]
    DECK_WEIGHT = arr[2]

def getCardPosition(card):
    for num in HAND:
        #print(num)
        if HAND[num] != None:
			if HAND[num]==card:
				return num
	
    raise Exception("Card doesn't exist in table")

def heuristic(layout):
    global SEQUENCE_WEIGHT
    global DECK_WEIGHT
    global TABLE_WEIGHT

    sequencePoints = GetPointsForSequence(layout.combinationUsed)
    tablePoints = getPointsFromCards(layout.cardsInTable)
    cards = []
    for card in layout.cardsInDeck:
        cards.append(card)
    for card in layout.cardsInTable:
        cards.append(card)

    cards.sort(key = lambda x: x.number)
    pointsAllCards = getPointsFromCards(cards)

    result = SEQUENCE_WEIGHT*sequencePoints  + DECK_WEIGHT*pointsAllCards + tablePoints*TABLE_WEIGHT
    
    #Log("[Heuristic] - Cards In Hand -> " + str(layout.cardsInTable))
    #Log("[Heuristic] - Cards In Sequence -> " + str(layout.combinationUsed))
    #Log("[Heuristic] - Points -> " + str(result))

    return result















def Log(message):
	if DEBUG:
		print(message)

def printField():
	global HAND
	Log('Hand:')
	for i in xrange(5):
		Log(str(i+1) + " : " + str(HAND[i+1]))
	#Log('Cards_Used: ' + str(USED_CARDS))
	#Log('Cards_Left: ' + str(CARDS_LEFT))

def fillHand():
	global HAND
	global CARDS_LEFT
	cardPulled = False
	for i in xrange(5):
		if None == HAND[i+1]:
			if len(CARDS_LEFT) == 0:
				return cardPulled
			HAND[i+1] = CARDS_LEFT.pop(0)
			cardPulled = True
	return cardPulled

def CardsLeft():
	global USED_CARDS
	global HAND
	global CARDS
	_cards = 0

	for _card in HAND.values():
		if not _card:
			continue

		_cards += 1

	return CARDS - len(USED_CARDS) - _cards

def resetGame():
	global FINISH
	global HAND
	global USED_CARDS
	global CARDS_LEFT
	global SCORE
	
	FINISH = False
	HAND = {
		1: None,
		2: None,
		3: None,
		4: None,
		5: None
	}
	if DEBUG:
		Log('Starting new game')
	CARDS_LEFT = []
	for i in xrange(8):
		CARDS_LEFT.append(Card(i+1,10))
		CARDS_LEFT.append(Card(i+1,20))
		CARDS_LEFT.append(Card(i+1,30))
	import random
	random.shuffle(CARDS_LEFT)
	USED_CARDS = []
	SCORE = 0
	fillHand()

def MoveCardHandToField(slot):
	global USED_CARDS
	global HAND
	Log('Using card: ' + str(slot))
	USED_CARDS.append(HAND[slot])
	HAND[slot] = None
	
def MoveCardHandToGrave(slot):
	global USED_CARDS
	global HAND
	if DEBUG:
		Log("Discarded card at slot " + str(slot))

	USED_CARDS.append(HAND[slot])
	HAND[slot] = None

def gameFinished():
	global FINISH
	return FINISH

def moveCards(possSlots):
	global SCORE
	MoveCardHandToField(possSlots[0])
	MoveCardHandToField(possSlots[1])
	MoveCardHandToField(possSlots[2])
	SCORE += possSlots[3]

def TotalCardsLeft():
	global USED_CARDS
	global CARDS

	return CARDS - len(USED_CARDS)

def RunSimulations(value = 0):
    global HOOKED
    global COLORS
    global HAND
    global CARDS
    global CARDS_LEFT
    global SCORE
    global FINISH
    global USED_CARDS
    global SIMULATIONS
    global SCORE_SUM
    global RESULTS

    RESULTS = [0,0,0]
    SCORE_SUM = 0
    FINISH = False
    HOOKED = True
    if value != 0:
        SIMULATIONS = value
    COLORS = {
        10: "Red",
    	20: "Blue",
    	30: "Yellow"
    }

    HAND = {
    	1: None,
    	2: None,
    	3: None,
    	4: None,
    	5: None
    }
    CARDS = 24
    USED_CARDS = []
    Play()
	
def Play():
    global SCORE_SUM
    global HOOKED
    global COLORS
    global HAND
    global CARDS
    global CARDS_LEFT
    global SCORE
    global FINISH
    global USED_CARDS
    for i in xrange(0, SIMULATIONS):
        resetGame()
        printField()
        while gameFinished() == False:
            mcts=MCTS.MCTS()
            table = []
            deck = CARDS_LEFT
            used_cards = USED_CARDS
            #print(len(HAND.keys()))
            if HAND[1] != None:
                table.append(HAND[1])
            if HAND[2] != None:
                table.append(HAND[2])
            if HAND[3] != None:
                table.append(HAND[3])
            if HAND[4] != None:
                table.append(HAND[4])
            if HAND[5] != None:
                table.append(HAND[5])

            startLayout = OkeyLayout(table,deck,used_cards)
            #print(startLayout)
            #print("\nChild Nodes")


            #childs = startLayout.getChildNodes()
            #for x in childs:
                #print(str(x) + " Fitness: " + str(heuristic(x)))
            #print("\nChosen childs")
            #for x in xrange(0,10):
                #print(startLayout.getOneRandomChild())

            #return
            resultLayout = MCTS.solve(startLayout,TIME)
            #layoutList = startLayout.getChildNodes()
            #maxValue = -1
            #resultLayout = startLayout
            #for layout in layoutList:
                #print(layout)
                #print("Heuristica: -> " + str(heuristic(layout)))
            #    val = heuristic(layout)
            #    if val > maxValue:
            #        maxValue = val
            #        resultLayout = layout
            FINISH = resultLayout.isFinalNode()
            if len(resultLayout.combinationUsed) == 1:
                card = resultLayout.combinationUsed[0]
                MoveCardHandToGrave(getCardPosition(card))
            elif len(resultLayout.combinationUsed) == 3:
                pos = []
                for card in resultLayout.combinationUsed:
                    pos.append(getCardPosition(card))
                pos.append(resultLayout.GetPointsForPossibility())
                moveCards(pos)
            else:
                FINISH = True
                break
            fillHand()
            printField()    

        if gameFinished() == True:
            Log('Game finished')
            Log('Score: ' + str(SCORE))
    		#Normal
    		#if SCORE >= 400: RESULTS[2]+=1
    		#elif SCORE >= 250: RESULTS[1]+=1
    		#else: RESULTS[0]+=1
    
    		#Christmas
            if SCORE >= 400: RESULTS[2]+=1
            elif SCORE >= 300: RESULTS[1]+=1
            else: RESULTS[0]+=1
            SCORE_SUM += SCORE
            print(SCORE)
    print('END SCORE (bronze, silver, gold): ' + str(RESULTS))

def resultMean():
    return float(1 + RESULTS[2]*3 + RESULTS[1])

RunSimulations(20)