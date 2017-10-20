"""
	A wrapper for Greedy Sum
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def greedysum(n, m, l, k, csim, articles):

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		# greedily pick l elements
		picked = [False for i in range(n)]
		S = []

		for times in range(l):
			bestInd = -1
			bestCost = -1

			for ind in range(n):
				S.append(ind)

				curCost = 0
				for c in range(m):
					curCost = curCost + computeCost(c, S)

				if curCost > bestCost:
					bestCost = curCost
					bestInd = ind

				S.pop()

			S.append(bestInd)
			picked[bestInd] = True

		totalCost = 0
		for c in range(m):
			totalCost = totalCost + greedy(c, S)
		print 'Greedy Sum gives cost = ', totalCost

		return S, totalCost, numEvals

	# compute the greedy maximization solution for S for the second stage submodular maximization
	def greedy(c, S):
		greedyS = []

		use = [False for s in S]

		for times in range(k):
			# at each step, add the element that gives the greatest marginal gain 

			bestInd = -1
			bestCost = -1

			for ind in range(len(S)):
				if use[ind] == False:
					greedyS.append(S[ind])

					curCost = computeCost(c, greedyS)
					if curCost > bestCost:
						bestCost = curCost
						bestInd = ind

					greedyS.pop()

			greedyS.append(S[bestInd])
			use[bestInd] = True

		return computeCost(c, greedyS)


	# write a function that computes the value of f for each category
	# this is FacilityLocation from - Learning mixtures of submodular functions for image collection summarization.
	def computeCost(catIndex, S):
		global numEvals
		numEvals = numEvals + 1

		# we are only interested in the elements of S that are part of category catIndex
		catS = list(set(S).intersection(articles[catIndex]))

		tot = 0

		for articleInd in articles[catIndex]:
			mostSim = 0

			for s in catS:
				mostSim = max(mostSim, csim[articleInd][s])

			tot = tot + mostSim

		return tot

	return worker()

