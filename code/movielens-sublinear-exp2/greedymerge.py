"""
	A wrapper for Greedy Merge in the movielens setting.

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

def gmWrapper(n, m, l, k, userRatings, movieCats, allCats):

	# return the set of l elements that maximizes the greedy approach
	def gm(partition):
		global numEvals
		numEvals = 0

		totalCost = 0
		S = []		

		start = time.time()

		# greedily maximize each function ignoring the constraint on L
		for catIndex in range(m):

			greedyS = []
			use = [False for i in range(n)]

			# print 'Category ', catIndex

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

					oldS = greedyS[:]
					newS = greedyS[:]
					newS.append(partition[bestInd])

				# print partition[bestInd], " ", computeCost(catIndex, newS) - computeCost(catIndex, oldS)


				greedyS.append(partition[bestInd])
				use[bestInd] = True

			# print "Total cost = ", computeCost(catIndex, greedyS), "\n"

			totalCost = totalCost + computeCost(catIndex, greedyS)
			S.extend(greedyS)

		S = list(set(S))

		print 'Greedy Merge gives cost = ', totalCost
		print 'Size of S is ', len(S)

		return S, totalCost, numEvals, time.time() - start

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

	return gm

