# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 17:40:13 2015

@author: ericbalkanski
"""

from cvxopt import matrix, solvers
import random
import copy

numSamples = 1000






############################
########### LP #############
############################

# Simple example to solve lp using cvx: 
# http://cvxopt.org/examples/tutorial/lp.html


# l: number of elements that can be picked in the first round
# k: number of elements that can be picked in the second round for each function
# children: 2D list [[children for cf 1], ..., [children for cf m]]
# dictParents: list of dictionaries mapping children to elements that cover 
#              them, one for each coverage function [d1, ..., dm]

def solveLP(l,k, children, elements, dictParents,loweredL, loweredK):
    
    n = len(elements)    
    m = len(children)
    
    # Total number of children over all functions
    numChildren = 0
    for listChildren in children:
        numChildren += len(listChildren)
        
    # Array for objective function (minimized, so take -1 to maximize)
    objective = [-1.0]*numChildren # variables z_jk
    objective += [0.0]*n # variables x_i
    objective += [0.0]*(n*m) # variables x_ij
    
    
    #Total number of constraints
    numConstraints = 0
    numConstraints += numChildren # z <= 1
    numConstraints += numChildren # z <= sum x_ij
    numConstraints += 1 # budget l
    numConstraints += m # budgets k
    numConstraints += n*m # x_ij <= x_i
    numConstraints += n # x_i <= 1
    numConstraints += n*m # x_ij >= 0
    
    #Total number of variables
    numVariables = numChildren + n + n*m    
    
    
    # Matrix of constraints A <= b
    #
    # A: variables are columns and each constraint is a row, A then needs to
    #    be transposed for cvx
    #
    #       z_1 ... z_numChildren  x_1 ... x_n  x_11 ... x_nm     
    # A = [[                                                 ],   
    #                        ...                                  z <= 1
    #      [                                                 ], 
    #      [                                                 ],   
    #                        ...                                  z <= sum x_ij
    #      [                                                 ],
    #      [                                                 ],   budget l      
    #      [                                                 ],   
    #                        ...                                  budgets k
    #      [                                                 ],
    #      [                                                 ],   
    #                        ...                                  x_ij <= x_i
    #      [                                                 ],
    #      [                                                 ],   
    #                        ...                                  x_i <= 1
    #      [                                                 ],
    #      [                                                 ],   
    #                        ...                                  x_ij >= 0
    #      [                                                 ]]
    
    # Initialize A and b
    A = [[0.0]*numVariables for i in range(numConstraints)]
    b = [0.0]*numConstraints
    cstIndex = 0 # index of the current constraint
    
    # z <= 1
    for childNum in range(numChildren):
        A[cstIndex][childNum] = 1.0
        b[cstIndex] = 1.0
        cstIndex += 1
        
    # z <= sum x_ij
    childNum = 0 # child number
    for j in range(m):
        # cover function j
        listChildren = children[j]
        for child in listChildren:
            #z
            A[cstIndex][childNum] = 1.0
            parents = []
            if child in dictParents[j].keys():
                parents = dictParents[j][child]
            #sum x_ij
            for parent in parents:
                indexParent = elements.index(parent)
                A[cstIndex][numChildren + n + m*indexParent + j] = -1.0
            childNum += 1
            cstIndex += 1
    
    # budget l
    for i in range(n):
        A[cstIndex][numChildren + i] = 1.0
    b[cstIndex] = loweredL*1.0
    cstIndex += 1
    
    # budgets k
    for j in range(m):
        for i in range(n):
            A[cstIndex][numChildren + n + m*i + j] = 1.0
        b[cstIndex] = loweredK*1.0
        cstIndex += 1
        
    # x_ij <= x_i 
    for i in range(n):
        for j in range(m):
            A[cstIndex][numChildren + n + m*i + j] = 1.0
            A[cstIndex][numChildren + i] = -1.0
            cstIndex += 1
    
    # x_i <= 1
    for i in range(n):
        A[cstIndex][numChildren + i] = 1.0
        b[cstIndex] = 1.0
        cstIndex += 1
    
    # x_ij >= 0
    for i in range(n):
        for j in range(m):
            A[cstIndex][numChildren + n + m*i + j] = -1.0
            cstIndex += 1
            
    # take the transpose of A
    A = map(list, zip(*A))
    
    A = matrix(A)
    b = matrix(b)
    c = matrix(objective)
    
    fullSolution = solvers.lp(c,A,b)
    sol = fullSolution['x']

    # parse solution
    firstRoundSol = []
    for i in range(n):
        firstRoundSol.append(sol[numChildren + i])
    secondRoundSol = []
    for j in range(m):
        solCoverFunctionJ = []
        for i in range(n):
            solCoverFunctionJ.append(sol[numChildren + n + m*i + j])
        secondRoundSol.append(solCoverFunctionJ)
    relaxedValue = relaxedSolutionValue(secondRoundSol, children, elements, dictParents)
    value = roundedSolutionValue(firstRoundSol, secondRoundSol, l, k, children, elements, dictParents, numSamples)
    print "concave Objective Value: " + str(- fullSolution['primal objective']) 
    print "relaxedValue: " + str(relaxedValue)
    print "value: " + str(value)

    return -fullSolution['primal objective'], relaxedValue, value
    #return fullSolution


############################
########### LP for one Coverage #############
############################

# Simple example to solve lp using cvx: 
# http://cvxopt.org/examples/tutorial/lp.html



# k: number of elements that can be picked in the second round for each function
# children: 1D list [children for cf 1]
# dictParents:  dictionaries mapping children to elements that cover 
#              them d1

def solveOneLP(k, children, elements, dictParent):
    
    n = len(elements)  
    numChildren = len(children)
        
    # Array for objective function (minimized, so take -1 to maximize)
    objective = [-1.0]*numChildren # variables z_jk
    objective += [0.0]*n # variables x_i
    
    
    #Total number of constraints
    numConstraints = 0
    numConstraints += numChildren # z <= 1
    numConstraints += numChildren # z <= sum x_i
    numConstraints += 1 # budgets k
    numConstraints += n # x_i <= 1
    numConstraints += n # x_i >= 0
    
    #Total number of variables
    numVariables = numChildren + n   
    
    
    # Matrix of constraints A <= b
    #
    # A: variables are columns and each constraint is a row, A then needs to
    #    be transposed for cvx
    #
    #       z_1 ... z_numChildren  x_1 ... x_n      
    # A = [[                                                 ],   
    #                        ...                                  z <= 1
    #      [                                                 ], 
    #      [                                                 ],   
    #                        ...                                  z <= sum x_i
    #      [                                                 ],
    #      [                                                 ],   budget k
    #      [                                                 ],   
    #                        ...                                  x_i <= 1
    #      [                                                 ],
    #      [                                                 ],   
    #                        ...                                  x_i >= 0
    #      [                                                 ]]
    
    # Initialize A and b
    A = [[0.0]*numVariables for i in range(numConstraints)]
    b = [0.0]*numConstraints
    cstIndex = 0 # index of the current constraint
    
    # z <= 1
    for childNum in range(numChildren):
        A[cstIndex][childNum] = 1.0
        b[cstIndex] = 1.0
        cstIndex += 1
        
    # z <= sum x_i
    childNum = 0 # child number
    for child in children:
        #z
        A[cstIndex][childNum] = 1.0
        parents = []
        if child in dictParent.keys():
            parents = dictParent[child]
        #sum x_ij
        for parent in parents:
            if parent in elements:
                indexParent = elements.index(parent)
                A[cstIndex][numChildren + indexParent] = -1.0
        childNum += 1
        cstIndex += 1
    
    # budget k
    for i in range(n):
        A[cstIndex][numChildren + i] = 1.0
    b[cstIndex] = k
    cstIndex += 1
    
    
    # x_i <= 1
    for i in range(n):
        A[cstIndex][numChildren + i] = 1.0
        b[cstIndex] = 1.0
        cstIndex += 1
    
    # x_i >= 0
    for i in range(n):
        A[cstIndex][numChildren + i] = -1.0
        cstIndex += 1
            
    # take the transpose of A
    A = map(list, zip(*A))
    
    A = matrix(A)
    b = matrix(b)
    c = matrix(objective)

    solvers.options['show_progress'] = False
    
    fullSolution = solvers.lp(c,A,b)
    sol = fullSolution['x']

    # print "concave Objective Value: " + str(- fullSolution['primal objective']) 
    return - fullSolution['primal objective']


###########################################
######### COMPUTING VALUES ################
###########################################
    
# computes the value of a relaxed solution where the budget holds in expectation,
#    i.e., the sum over all children of the probability that they are covered
#
#     secondRoundSol: 2D list of probabilities of elements being selected 
#       in 2nd round, so one list for each cover function
def relaxedSolutionValue(secondRoundSol, children, elements, dictParents):
    value = 0
    m = len(children)
    for coverFunction in range(m):
        for child in children[coverFunction]:
            probNotCovered = 1
            # the probability that a child is not covered is the product
            # of the probability that each of its parent is not selected
            if child in dictParents[coverFunction].keys():
                for parent in dictParents[coverFunction][child]:
                    indexParent = elements.index(parent)
                    probNotCovered *= 1 - secondRoundSol[coverFunction][indexParent]
            value += 1 - probNotCovered
    return value

# number of children cover by a solution to a coverage problem
#
# solution: 1D list of elements in solution
# children: 1D list of children
# d: dictionary that maps children to elements
def coverageValue(solution, children, d):
    value = 0
    for child in children:
        parents = d[child]
        # intersection
        for parent in parents:
            if parent in solution:
                value += 1
                break
    return value
    
# computes the value of a solution
#
#     secondRoundSol: 2D list of elements being selected 
#       in 2nd round, so one list for each cover function
def solutionValue(secondRoundSol, children, elements, dictParents):   
    value = 0
    m = len(children)
    for cf in range(m):
        value += coverageValue(secondRoundSol[cf], children[cf], dictParents[cf])
    return value
    
# computes the value post-rounding by sampling, all samples that are not 
# feasible are ignored
def roundedSolutionValue(firstRoundSol, secondRoundSol, l, k, children, elements, 
                         dictParents, numSamples):
    n = len(elements)
    m = len(children)
    totalValue = 0
    for sample in range(numSamples):
        firstRoundSample = []
        for ielement in range(n):
            if random.random() <= firstRoundSol[ielement]:
                firstRoundSample.append(elements[ielement])
        # check first round sample is feasible
        if len(firstRoundSample) > l:
            continue            
        secondRoundSample = []
        for cf in range(m):
            sampleCf = []
            for element in firstRoundSample:
                ielement = elements.index(element)
                if random.random() <= secondRoundSol[cf][ielement]/firstRoundSol[ielement]:
                    sampleCf.append(element)
            # check sample is feasible
            if len(sampleCf) > k:
                secondRoundSample.append([])
            else:
                secondRoundSample.append(sampleCf)
        totalValue += solutionValue(secondRoundSample, children, elements, dictParents)
    return totalValue * 1.0 / numSamples
        

################################    
########### GREEDY #############
################################
    

 
# performs greedy on each coverage function for the secondRound
def greedySecondRound(firstRoundSol, k, children, dictParents):
    sol = []
    m = len(children)
    if len(firstRoundSol) < k:
        return [firstRoundSol]*m
    for cf in range(m):
        solCF = []
        elementsLeft = copy.deepcopy(firstRoundSol)
        for i in range(k):
            bestElement = elementsLeft[0]
            bestValue = 0
            for element in elementsLeft:
                solCF.append(element)
                newScore = coverageValue(solCF, children[cf], dictParents[cf])
                if newScore > bestValue:
                    bestElement = element
                    bestValue = newScore
                solCF.remove(element)
            solCF.append(bestElement)
            elementsLeft.remove(bestElement)
        sol.append(solCF)
    return sol

# greedy solution
def greedy(l,k, children, elements, dictParents):   
    firstRoundSol = []
    elementsLeft = copy.deepcopy(elements)
    for i in range(l):
        bestElement = elementsLeft[0]
        bestValue = 0
        for element in elementsLeft:
            firstRoundSol.append(element)
            newSecondRound = greedySecondRound(firstRoundSol, k, children, dictParents)
            newValue = solutionValue(newSecondRound, children, elements, dictParents)
            if newValue > bestValue:
                bestElement = element
                bestValue = newValue
            firstRoundSol.remove(element)
        print bestElement
        firstRoundSol.append(bestElement)
        elementsLeft.remove(bestElement)
    secondRoundSol = greedySecondRound(firstRoundSol, k, children, dictParents)
    value = solutionValue(secondRoundSol, children, elements, dictParents)
    return (firstRoundSol, value)
        


####################################
#########     LS   #################
####################################

def lpSecondRoundVal(firstRoundSol, k, children, dictParents):
    m = len(children)
    value = 0
    for j in range(m):
        value += solveOneLP(k, children[j], firstRoundSol, dictParents[j])
    return value

def localSearchSeeded(k,children,elements,dictParents,seedSolution,count,epsilon):
    currentValue = lpSecondRoundVal(seedSolution, k, children, dictParents)
    minContribSolVal = 100000000000000000
    minContribSol = seedSolution[0]
    for elementSol in seedSolution:
        solWithoutEl = copy.deepcopy(seedSolution)
        solWithoutEl.remove(elementSol)
        contribElSol = currentValue - lpSecondRoundVal(solWithoutEl, k, children, dictParents)
        if contribElSol < minContribSolVal:
            minContribSolVal = contribElSol
            minContribSol = elementSol
    maxContribVal = 0
    maxContrib = elements[0]
    for element in elements:
        solWithEl = copy.deepcopy(seedSolution)
        solWithEl.append(element)
        contribNewEl = lpSecondRoundVal(solWithEl, k, children, dictParents) - currentValue
        if contribNewEl > maxContribVal:
            maxContribVal = contribNewEl
            maxContrib = element
            
    if maxContribVal > minContribSolVal + epsilon:
        print "\n\n\n\n"
        print "BEtter Solution"
        print "\n\n\n\n"
        newSol = copy.deepcopy(seedSolution)
        newSol.remove(minContribSol)
        newSol.append(maxContrib)
        return localSearchSeeded(k,children,elements,dictParents,newSol,count+1)
    return (seedSolution, count)

def localSearch(l,k,children,elements,dictParents,epsilon):
    print "Running greedy for seed solution..."
    (seedSolution,value) = greedy(l,k,children,elements,dictParents)
    print "Running local search..."
    (firstRoundSol, count) = localSearchSeeded(k,children,elements,dictParents,seedSolution,0,epsilon)
    print "First round sol:"
    print firstRoundSol
    print count
    secondRoundSol = greedySecondRound(firstRoundSol, k, children, dictParents)   
    print "Second round sol:"
    print secondRoundSol
    valueSol = solutionValue(secondRoundSol, children, elements, dictParents)
    print "got value " + str(valueSol)
    return valueSol
    
####################################
########### BASELINE 1 #############
####################################

def baseline1(l,k, children, elements, dictParents):
    return

##################################    
########### GENERATE #############
##################################
# generates synthetic data
def generateRandom(l,k,n,m, numChildren, numParents):
    elements = [i for i in range(n)]
    dictParents = []
    children = []
    for j in range(m):
        childrenCf = [i for i in range(numChildren)]
        d = dict()
        for child in childrenCf:
            parents = []
            for i in range(numParents):
                parents.append(random.randint(0,n-1))
            d[child] = parents
        dictParents.append(d)
        children.append(childrenCf)
    return (l,k, children, elements, dictParents)
    
        
        
def generateIndices(maxIndex, k):
    l = []
    remaining = range(maxIndex + 1)
    for i in range(k):
        current = random.randint(0,maxIndex- i)
        value = remaining[current]
        l.append(value)
        remaining.remove(value)
    return l
            
    
        
            
        
        
    
    
    
