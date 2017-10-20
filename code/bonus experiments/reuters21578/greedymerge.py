"""
	Greedy Merge. 
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def greedymerge(n, m, l, k, csim, articles):

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		totalCost = 0
		S = []

		# greedily maximize each function ignoring the constraint on L
		for c in range(m):

			greedyS = []
			use = [False for i in range(n)]

			for times in range(k):
				# at each step, add the element that gives the greatest marginal gain 
				bestInd = -1
				bestCost = -1

				for ind in range(n):
					if use[ind] == False:
						greedyS.append(ind)

						curCost = computeCost(c, greedyS)
						if curCost > bestCost:
							bestCost = curCost
							bestInd = ind

						greedyS.pop()

				greedyS.append(bestInd)
				use[bestInd] = True

			totalCost = totalCost + computeCost(c, greedyS)
			S.extend(greedyS)

		S = list(set(S))

		print 'Greedy Merge gives cost = ', totalCost
		print 'Size of S is ', len(S)

		return S, totalCost, numEvals


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

