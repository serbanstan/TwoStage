"""
	The replacementGreedy algo

	n - number of articles
	m - number of categories
	l - size of S
	k - size of S_i
	csim - the cosine similarity between the entries of the tf-idf matrix
	articles - a dict() of type 'category' -> 'list of articles with that tag'

	The articles themselves are represented as numbers from 0 to n-1
"""

import numpy as np

def replacementGreedy(n, m, l, k, csim, articles):

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		S = []
		T = [[] for i in range(m)]

		# the best S sets for each category
		for j in range(l):
			xStar = findXStar(T)
			S.append(xStar)

			for i in range(m):
				if repGain(i, xStar, T[i]) > 0:
					y = minElement(i, xStar, T[i])
					if y != [] and len(T[i]) == k:
						T[i].remove(y)
					
					T[i].append(xStar)

		totalCost = 0
		for i in range(m):
			totalCost += computeCost(i, T[i])

		return S, totalCost, numEvals

	def findXStar(T):
		bestX = 0
		bestValue = 0

		for x in range(n):
			curValue = 0
			for i in range(m):
				curValue = curValue + repGain(i, x, T[i])

			if curValue > bestValue:
				bestValue = curValue
				bestX = x

		return bestX

	def repGain(i, x, A):
		if len(A) < k:
			newA = A[:]
			newA.append(x)

			return computeCost(i, newA) - computeCost(i, A)
		else:
			y = minElement(i, x, A)

			# if minElement returns the empty set, repGain is just 0
			if y == []:
				return 0

			newA = A[:]
			newA.remove(y)
			newA.append(x)

			assert (computeCost(i, newA) - computeCost(i, A) > 0), "cost(newA) - cost(oldA) should be > 0"

			return computeCost(i, newA) - computeCost(i, A)

	def minElement(i, x, A):
		if len(A) < k:
			return []

		initialCost = computeCost(i, A);

		bestY = []
		bestValue = 0

		for y in A:
			newA = A[:]

			newA.remove(y)
			newA.append(x)

			newCost = computeCost(i, newA)

			if newCost > initialCost:
				if newCost - initialCost > bestValue:
					bestValue = newCost - initialCost
					bestY = y

		return bestY

	# write a function that computes the value of f for each category
	# this is Facilityelemstion from - Learning mixtures of submodular functions for image collection summarization.
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

