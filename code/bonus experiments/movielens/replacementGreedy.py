"""
	A wrapper for replacementGreedy in the movielens setting

    n - number of movies
	m - number of categories
	l - size of S
	k - size of S_i
	simDist - a dictionary of distances between pairs of movies
	movies - a dict() of type 'category' -> 'list of movies in said category'
"""

import numpy as np

def replacementGreedy(n, m, l, k, simDist, movies):

	# return the set of l elements that maximizes the greedy approach
	def worker(partition):
		global numEvals
		numEvals = 0

		# the best S sets for each category
		S = []
		T = [[] for i in range(m)]

		for j in range(l):
			xStar = findXStar(partition, T)
			S.append(xStar)

			for i in range(m):
				if repGain(i, xStar, T[i]) > 0:
					y = minElement(i, xStar, T[i])

					if y != [] and len(T[i]) == k:
						T[i].remove(y)

					T[i].append(xStar)

		totalCost = 0
		for i in range(m):
			totalCost = totalCost + computeCost(i, T[i])

		return S, totalCost, numEvals

	def findXStar(partition, T):
		bestX = partition[0]
		bestCost = 0

		for x in partition:
			curCost = 0
			for i in range(m):
				curCost = curCost + repGain(i, x, T[i])

			if curCost > bestCost:
				bestCost = curCost
				bestX = x

		return bestX


	def repGain(i, x, A):
		if len(A) < k:
			newA = A[:]
			newA.append(x)

			return computeCost(i, newA) - computeCost(i, A)
		else:
			y = minElement(i, x, A)

			if y == []:
				return 0

			newA = A[:]
			newA.remove(y)
			newA.append(x)

			assert (computeCost(i, newA) - computeCost(i, A) > 0), "cost(newA) - cost(oldA) should be > 0"

			return computeCost(i, newA) - computeCost(i, A)

	def minElement(i, x, A):
		initialCost = computeCost(i, A)

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
	# this is Facility Location from - Learning mixtures of submodular functions for image collection summarization.
	def computeCost(catIndex, A):
		tot = 0

		# we are only interested in the elements of A that are part of category catIndex
		catA = list(set(A).intersection(movies[catIndex]))

		global numEvals
		numEvals = numEvals + 1

		for mov in movies[catIndex]:
			mostSim = 0

			for a in catA:
				mostSim = max(mostSim, simDist[(mov, a)])

			tot = tot + mostSim

		return tot

	return worker

