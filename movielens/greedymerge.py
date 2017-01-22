"""
	A wrapper for Greedy Merge in the movielens setting.

	n - number of movies
	m - number of categories
	l - size of S
	k - size of S_i
	sim - the similarity matrix for all 100k+ movies
	movies - a dict() of type 'category' -> 'list of movies in said category'
"""

import numpy as np

def gmWrapper(n, m, l, k, simDist, movies):

	# return the set of l elements that maximizes the greedy approach
	def gm(partition):
		global numEvals
		numEvals = 0

		totalCost = 0
		S = []

		# greedily maximize each function ignoring the constraint on L
		for catIndex in range(m):

			greedyS = []
			use = [False for i in range(n)]

			for times in range(k):
				# at each step, add the element that gives the greatest marginal gain 
				bestInd = -1
				bestCost = -1

				for ind in range(n):
					if use[ind] == False:
						greedyS.append(partition[ind])

						curCost = computeCost(catIndex, greedyS)
						if curCost > bestCost:
							bestCost = curCost
							bestInd = ind

						greedyS.pop()

				greedyS.append(partition[bestInd])
				use[bestInd] = True

			totalCost = totalCost + computeCost(catIndex, greedyS)
			S.extend(greedyS)

		S = list(set(S))

		print 'Greedy Merge gives cost = ', totalCost
		print 'Size of S is ', len(S)

		return S, totalCost, numEvals

	# write a function that computes the value of f for each category
	# this is Facilitypartitiontion from - Learning mixtures of submodular functions for image collection summarization.
	def computeCost(catIndex, S):
		tot = 0

		global numEvals
		numEvals = numEvals + 1

		for mov in movies[catIndex]:
			mostSim = 0

			for s in S:
				mostSim = max(mostSim, simDist[(mov, s)])
				# mostSim = max(mostSim, np.dot(sim[mov], sim[s]))

			tot = tot + mostSim

		return tot

	return gm

