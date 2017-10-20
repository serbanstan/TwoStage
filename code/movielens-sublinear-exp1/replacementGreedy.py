"""
	A wrapper for replacementGreedy in the movielens setting

    n - number of movies
	m - number of categories
	l - size of S
	k - size of S_i
	userRatings - a dict of dicts, such that for each user we know all the ratings he gave
	weights - a dict or dicts, such that for each user we know the weights associated to each genre
	movieCats - a dict telling us the categories(genres) each movie is part of
	allCats - a list containing all categories
"""

import numpy as np
import time

def replacementGreedy(n, m, lmax, k, userRatings, weights, movieCats, allCats):

	# return the set of l elements that maximizes the greedy approach
	def worker(partition):
		global numEvals
		numEvals = 0

		allS = []
		allCost = []
		allEvals = []
		allTime = []

		start = time.time()

		# the best S sets for each category
		S = []
		T = [[] for i in range(m)]

		for j in range(lmax):
			xStar = findXStar(partition, T)
			S.append(xStar)

			for i in range(m):
				if repGain(i, xStar, T[i]) > 0:
					y = minElement(i, xStar, T[i])

					if y != [] and len(T[i]) == k:
						T[i].remove(y)

					T[i].append(xStar)

			if j >= k-1:
				# now add the values for this current iteration
				totalCost = 0
				for i in range(m):
					totalCost = totalCost + computeCost(i, T[i])

				allS.append(S[:])
				allCost.append(totalCost)
				allEvals.append(numEvals)
				allTime.append(time.time() - start)

				print 'Finished step ', j, ' with cost ', totalCost, '; number of evals', numEvals, '; total runtime', time.time() - start

		return allS, allCost, allEvals, allTime

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

	# write a function that computes the value of f for each user
	# for each category, we look at the intersection between that category and our set, and then pick the maximum rated the user gave
	def computeCost(userIndex, A):
		global numEvals
		numEvals = numEvals + 1

		tot = 0

		curUser = userRatings.keys()[userIndex]

		# make sure we are only considering movies the current user rated
		ratedA = list(set(A).intersection(userRatings[curUser].keys()))

		catA = dict()
		for cat in allCats:
			catA[cat] = []
		for mov in ratedA:
			for cat in movieCats[mov]:
				catA[cat].append(mov)

		for cat in allCats:
			# now, find the highest rated movie in each category
			highestRated = 0
			for mov in catA[cat]:
				highestRated = max(highestRated, userRatings[curUser][mov])

			tot = tot + weights[curUser][cat] * highestRated

		return tot

	return worker

