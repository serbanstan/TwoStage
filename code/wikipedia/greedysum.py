"""
	A wrapper for Greedy Sum
"""

import numpy as np

def greedysum(l, k, children, elements, dictParents):

	n = len(elements)
	m = len(children)

	# return the set of l elements that maximizes the greedy approach
	def gs():
		global numEvals
		numEvals = 0

		# greedily pick l elements
		picked = [False for i in range(n)]
		S = []

		for times in range(l):
			bestInd = -1
			bestCost = -1

			for ind in range(n):
				S.append(elements[ind])

				curCost = 0
				for i in range(m):
					curCost = curCost + computeCost(i, S)

				if curCost > bestCost:
					bestCost = curCost
					bestInd = ind

				S.pop()

			S.append(elements[bestInd])
			picked[bestInd] = True

		totalCost = 0
		for i in range(m):
			totalCost = totalCost + greedy(i, S)
		print 'Greedy Sum gives cost = ', totalCost

		return S, totalCost, numEvals

	# compute the greedy maximization solution for S for the second stage submodular maximization
	def greedy(catIndex, S):
		greedyS = []

		use = [False for s in S]

		for times in range(k):
			# at each step, add the element that gives the greatest marginal gain 

			bestInd = -1
			bestCost = -1

			for ind in range(len(S)):
				if use[ind] == False:
					greedyS.append(S[ind])

					curCost = computeCost(catIndex, greedyS)
					if curCost > bestCost:
						bestCost = curCost
						bestInd = ind

					greedyS.pop()

			greedyS.append(S[bestInd])
			use[bestInd] = True

		return computeCost(catIndex, greedyS)


	# write a function that computes the value of f for each category
	def computeCost(catIndex, S):
		tot = 0

		global numEvals
		numEvals = numEvals + 1

		# check how many children are activated by S
		for child in children[catIndex]:
			parents = dictParents[catIndex][child]
			# intersection
			for parent in parents:
				if parent in S:
					tot += 1
					break

		return tot

	return gs()

