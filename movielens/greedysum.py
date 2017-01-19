"""
	A wrapper for Greedy Sum in the movielens setting.

	n - number of movies
	m - number of categories
	l - size of S
	k - size of S_i
	sim - the similarity matrix for all 100k+ movies
	movies - a dict() of type 'category' -> 'list of movies in said category'
"""

import numpy as np

def gsWrapper(n, m, l, k, sim, movies):

	# return the set of l elements that maximizes the greedy approach
	def gs(partition):
		global numEvals
		numEvals = 0

		# greedily pick l elements
		picked = [False for i in range(n)]
		S = []

		for times in range(l):
			bestInd = -1
			bestCost = -1

			for ind in range(n):
				S.append(partition[ind])

				curCost = 0
				for i in range(m):
					curCost = curCost + computeCost(i, S)

				if curCost > bestCost:
					bestCost = curCost
					bestInd = ind

				S.pop()

			S.append(partition[bestInd])
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
	# this is Facilitypartitiontion from - Learning mixtures of submodular functions for image collection summarization.
	def computeCost(catIndex, S):
		tot = 0

		global numEvals
		numEvals = numEvals + 1

		for mov in movies[catIndex]:
			mostSim = 0

			for s in S:
				mostSim = max(mostSim, np.dot(sim[mov], sim[s]))

			tot = tot + mostSim

		return tot

	return gs

