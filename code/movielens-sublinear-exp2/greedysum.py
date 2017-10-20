"""
	A wrapper for Greedy Sum in the movielens setting.

	n - number of movies
	m - number of categories
	l - size of S
	k - size of S_i
	userRatings - a dict of dicts, such that for each user we know all the ratings he gave
	movieCats - a dict telling us the categories(genres) each movie is part of
	allCats - a list containing all categories
"""

import numpy as np
import time

def gsWrapper(n, m, l, k, userRatings, movieCats, allCats):

	# return the set of l elements that maximizes the greedy approach
	def gs(partition):
		global numEvals
		numEvals = 0

		allS = []
		allCost = []
		allEvals = []
		allTime = []

		start = time.time()

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

			if times >= k-1:
				# now add the values for this current iteration
				totalCost = 0
				for i in range(m):
					totalCost = totalCost + greedy(i, S)

				allS.append(S[:])
				allCost.append(totalCost)
				allEvals.append(numEvals)
				allTime.append(time.time() - start)

				print 'Finished step ', times, ' with cost ', totalCost, '; number of evals', numEvals, '; total runtime', time.time() - start

		return allS, allCost, allEvals, allTime

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


	# write a function that computes the value of f for each user
	# for each category, we look at the intersection between that category and our set, and then pick the maximum rated the user gave
	def computeCost(userIndex, A):
		global numEvals
		numEvals = numEvals + 1

		tot = 0

		curUser = userRatings.keys()[userIndex]

		catA = dict()
		for cat in allCats:
			catA[cat] = []
		for mov in A:
			for cat in movieCats[mov]:
				catA[cat].append(mov)

		for cat in allCats:
			# now, find the highest rated movie in each category
			highestRated = 0
			for mov in catA[cat]:
				highestRated = max(highestRated, userRatings[curUser][mov])

			tot = tot + highestRated

		return tot

	return gs

