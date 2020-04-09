import random, math
import OkeySimulator_Improve as game
MUTATION_CHANCE = 0.07
CROSSHOVER_CHANCE = 0.80
KEEP_BEST = True
RECALC = True
VARIATION_INCREASE = 0.03

MAX_VALUE = 20.0
MIN_VALUE = 0.0


def getNormalFitness(value):
    #return 100 + math.log(value)/VARIATION_INCREASE
    return value

class Population:
    def __init__(self,population,size_population=0,size_individual=0):
        if population == 0:
            self.population = self.generateRandomPopulation(size_population,size_individual)
            self.population = sorted(self.population,key = lambda x:x.fitness)
            return
        self.population = population
        self.population = sorted(self.population,key = lambda x:x.fitness)
        
        
    
    def generateRandomPopulation(self, size_pop,size_indiv):
        population = []
        for x in xrange(0,size_pop):
            population.append(Individual(0,size_indiv))
        return population

    def getFitnessSum(self):
        result = 0
        for indiv in self.population:
            result += indiv.fitness

        return result

    def roulleteSelection(self):
        sumF = self.getFitnessSum()
        incrementalSum = 0
        randomValue = random.uniform(0,sumF)
        #selection
        for indiv in self.population:
            incrementalSum+=indiv.fitness
            if randomValue <= incrementalSum:
                return indiv
        
        raise Exception("Error ocurred, selection is wrong")

    #Crosshover with same individual possible
    #Can be faster
    def getPopulationByCrosshover(self):
        global KEEP_BEST
        global RECALC
        population = []
        if KEEP_BEST == True:
            population.append(Individual(self.getBestIndividual().data))
            #print("Best New -> " + str(getNormalFitness(population[0].fitness)))
            #print("Best Old -> " + str(getNormalFitness(self.getBestIndividual().fitness)))

        while(len(population) != len(self.population)):
            ind1 = self.roulleteSelection()
            ind2 = self.roulleteSelection()
            if(RECALC == True):
                needRecalc_1 = True
                needRecalc_2 = True
            else:
                needRecalc_1 = False
                needRecalc_2 = False

            rand_crosshover = random.random()
            rand_mutation_1 = random.random()
            rand_mutation_2 = random.random()
            if rand_crosshover <= CROSSHOVER_CHANCE:
                (ind1,ind2) = ind1.uniformCrosshover(ind2)
                needRecalc_1 = False
                needRecalc_2 = False
                #print("Crosshover Happening")

            if rand_mutation_1<MUTATION_CHANCE:
                ind1 = ind1.singlePointMutation()
                needRecalc_1 = False
                #print("Mutation Happening")

            if rand_mutation_2<MUTATION_CHANCE:
                ind2 = ind2.singlePointMutation()
                needRecalc_2 = False
                #print("Mutation Happening")

            if(needRecalc_1):
                ind1 = Individual(ind1.data)
            
            if(needRecalc_2):
                ind2 = Individual(ind2.data)

            population.append(ind1) #May need fitness recalculation

            if len(population) <len(self.population):
                population.append(ind2) #May need fitness recalculation

        return Population(population)

    def getStatistics(self):
        result = "Best Individual: " + str(self.getBestIndividual()) + "\n"
        result += "Worst Individual: " + str(self.getWorstIndividual()) + "\n"
        result += "Average Fitness " + str(self.getAverageFitness()) + "\n"

        return result

    def getBestIndividual(self):
        return self.population[len(self.population)-1]
    def getWorstIndividual(self):
        return self.population[0]

    def getAverageFitness(self):
        count = len(self.population)
        _sum = self.getFitnessSum()

        return getNormalFitness(_sum/count)


    
    def __repr__(self):
        result = ""
        io = 0
        for i in self.population:
            each = ""
            io+=1
            each += str(io)
            each += ": " 
            each += str(i)
            each += "\n"
            result += each
        return result



#CANNOT BE NEGATIVE
def fitness(individual):
    game.setWeights(individual.data)
    game.RunSimulations(5)
    #print(game.resultMean())
    value = game.resultMean()
    #print(value)
    #value = math.exp((value-100)*VARIATION_INCREASE)
    #print(getNormalFitness(value))
    #print(game.CARD_WEIGHTS)
    #print(game.POSITION_WEIGHTS)
    #print(individual.data)
    #print("\n")
    #print(value)
    return value
            


class Individual:
    def __init__(self, binary_string, size = 0):
        if binary_string == 0:
            self.randomIndividual(size)
            self.fitness = fitness(self)
            return
        if len(binary_string) <= 0:
            raise Exception("No data")
        self.data = binary_string
        self.fitness = fitness(self)
    
    def randomIndividual(self,size):
        if size == 0:
            raise Exception("Error no data to individual")
        self.data = []
        for x in xrange(0,size):
            rand_value = random.uniform(MIN_VALUE,MAX_VALUE)
            self.data.append(rand_value)
        return self.data

    def uniformCrosshover(self, parent):
        new_individual1 = []
        new_individual2 = []
        for x in xrange(0,len(self.data)):
            rand = random.randint(0,1)
            if rand == 1:
                new_individual1.append(self.data[x])
                new_individual2.append(parent.data[x])
            else:
                new_individual2.append(self.data[x])
                new_individual1.append(parent.data[x])
        
        in1 = Individual(new_individual1)
        in2 = Individual(new_individual2)
        
        
        return (in1,in2)

    #CHeck End points
    def singlePointCrosshover(self, parent):
        rand = random.randint(1,len(self.data)-1)
        new_individual1 = []
        new_individual2 = []
        for x in xrange(0,rand):
            new_individual1.append(self.data[x])
            new_individual2.append(parent.data[x])
        
        for x in xrange(rand,len(self.data)):
            new_individual1.append(parent.data[x])
            new_individual2.append(self.data[x])

        in1 = Individual(new_individual1,0)
        
        in2 = Individual(new_individual2,0)
        
        
        return (in1,in2)

    def singlePointMutation(self):
        randInt = random.randint(0,len(self.data)-1)
        arr = list(self.data)
        value = arr[randInt]
        rand = random.gauss(0,value)
        arr[randInt] = value + rand
        return Individual(arr)

    def uniformMutation(self):
        arr = []
        for value in self.data:
            rand = random.gauss(0,value)
            arr.append(value + rand)
        return Individual(arr)
    
    def __repr__(self):
        result = 0
        result = "Data: ("
        for value in self.data:
            result += str(round(value,3))
            result += ", "
        result += ") Fitness: "
        result += str(getNormalFitness(self.fitness))
        
        return str(result)
                


#main

def testIndividual():
    i = Individual(0,10)
    print(i)

def testMutation():
    i = Individual(0,10)
    mut = i.mutation()
    print("Original: " + str(i))
    print("Mutation: " + str(mut))

def testUniformCrossHover():
    i1 = Individual(0,2)
    i2 = Individual(0,2)

    (c1,c2) = i1.uniformCrosshover(i2)

    print("Original 1-> " + str(i1))
    print("Original 2-> " + str(i2))
    
    print("Crosshover 1-> " + str(c1))
    print("Crosshover 2-> " + str(c2))

def testCrosshover():
    i1 = Individual(0,2)
    i2 = Individual(0,2)

    (c1,c2) = i1.singlePointCrosshover(i2)

    print("Original 1-> " + str(i1))
    print("Original 2-> " + str(i2))
    
    print("Crosshover 1-> " + str(c1))
    print("Crosshover 2-> " + str(c2))


def testPopulation():
    p = Population(0,10,10)
    print(str(p))


def testPopulationRoullete():
    p = Population(0,6,2)
    print(str(p))
    print("Selection: \n\n")
    arr = []
    for x in xrange(0,10000):
        arr.append(p.roulleteSelection())
    arr = sorted(arr, key = lambda x:x.fitness) 

    i = 0
    last = arr[0]
    for x in arr:
        i+=1
        if x.fitness != last.fitness:
            print("Fitness " + str(last.fitness) + " Count: " + str(i))
            i = 0
            last = x

        #print(str(x))
    print("Fitness " + str(last.fitness) + " Count: " + str(i))

def testNewGeneration():
    p = Population(0,10,4)
    print("Original Population\n" + str(p))
    a = p.getPopulationByCrosshover()
    print("New Generation\n" + str(a))


p = Population(0,50,3)
print("Generation 0")
print(str(p.getStatistics()))
for x in xrange(0,10000):
    p = p.getPopulationByCrosshover()
    print("Generation " + str(x+1))
    print(str(p.getStatistics()))

#Test 