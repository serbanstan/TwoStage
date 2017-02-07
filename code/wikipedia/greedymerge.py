"""
	A wrapper for Greedy Merge in the movielens setting.
"""

import numpy as np

def greedymerge(l, k, children, elements, dictParents):

	n = len(elements)
	m = len(children)

	# return the set of l elements that maximizes the greedy approach
	def gm():
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
						greedyS.append(elements[ind])

						curCost = computeCost(catIndex, greedyS)
						if curCost > bestCost:
							bestCost = curCost
							bestInd = ind

						greedyS.pop()

				greedyS.append(elements[bestInd])
				use[bestInd] = True

			totalCost = totalCost + computeCost(catIndex, greedyS)
			S.extend(greedyS)

		S = list(set(S))

		print 'Greedy Merge gives cost = ', totalCost
		print 'Size of S is ', len(S)

		return S, totalCost, numEvals

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

	return gm()

