"""
	A wrapper for Amin's algorithm in order to be able to use mapPartitions

	n - number of movies
	m - number of categories
	l - size of S
	k - size of S_i
	allSim - the similarity matrix for all 100k+ movies
	allMovies - a dict() of type 'category' -> 'list of movies in said category'
"""

import numpy as np

def wrapper(n, m, l, k, allSim, allMovies):

	# return the set of l elements that maximizes the greedy approach
	def novel(partition):

		# retrieve the elements from this partition - speed improvement
		local = [i for i in partition]

		# update sim and movies to cater for this partition only
		sim = dict()
		movies = dict()

		for i in local:
			sim[i] = allSim[i]
		for category in allMovies:
			movies[category] = list(set(allMovies[category]).intersection(set(local)))

		# work forthe first k entries
		S, picked = preK(local, sim, movies)

		# the best S sets for each category
		bestS = [S for i in range(m)]

		oldCost = 0
		for i in range(m):
			oldCost = oldCost + computeCost(i, bestS[i], sim, movies)

		for times in range(l - k):
			bestCost = -1
			bestInd = -1
			bestSwp = [-1 for i in range(m)]

			for movInd in range(len(local)):
				if picked[movInd] == False:

					newCost = 0
					swp = [-1 for i in range(m)]

					# now, for each category, swap out the element that gives the least marginal gain
					for i in range(m):

						catOld = computeCost(i, bestS[i], sim, movies)
						catNew = catOld

						# iterate through all k positions and rememeber the best swap
						for j in range(k):
							aux = bestS[i][j]

							bestS[i][j] = local[movInd]

							val = computeCost(i, bestS[i], sim, movies)
							if val > catNew:
								catNew = val
								swp[i] = j

							bestS[i][j] = aux

						newCost = newCost + catNew

					if newCost > bestCost:
						bestCost = newCost
						bestInd = movInd
						bestSWP = [el for el in swp]

			# time to add in the best element we found

			if bestCost >= 0:	# make sure we have enough elements in the partition
				S.append(local[bestInd])
				picked[bestInd] = True
				for i in range(m):
					if bestSwp[i] != -1:
						bestS[i][bestSwp[i]] = ind
				oldCost = bestCost


		# totalCost = 0
		# for i in range(m):
		# 	totalCost = totalCost + computeRealCost(i, bestS[i])
		# print 'Our solution gives totalCost = ', totalCost

		return S

	# before hitting k elements, each element will just have to maximize the marginal gain
	def preK(local, sim, movies):
		S = []

		picked = [False for i in range(len(local))]

		for times in range(k):
			bestCost = -1
			bestInd = -1

			for movInd in range(len(local)):
				if picked[movInd] == False:

					mov = local[movInd]
					S.append(mov)

					curCost = 0
					for i in range(m):
						curCost = curCost + computeCost(i, S, sim, movies)

					if curCost > bestCost:
						bestCost = curCost
						bestInd = movInd

					S.pop()

			# print bestInd

			# make sure we have enough elements in the partition
			if bestCost >= 0:
				S.append(local[bestInd])
				picked[bestInd] = True

			# print bestCost

		return S, picked


	# write a function that computes the value of f for each category
	# this is FacilityLocaltion from - Learning mixtures of submodular functions for image collection summarization.
	def computeCost(catIndex, S, sim, movies):
		tot = 0

		for mov in movies[catIndex]:
			mostSim = 0

			for s in S:
				mostSim = max(mostSim, np.dot(sim[mov], sim[s]))

			tot = tot + mostSim

		return tot

	# the computeCost function only computes the cost w.r.t. the set it's working with. this function computes the cost w.r.t.
	# all the elements
	def computeRealCost(catIndex, S):
		tot = 0

		for mov in allMovies[catIndex]:
			mostSim = 0

			for s in S:
				mostSim = max(mostSim, np.dot(allSim[mov], allSim[s]))

			tot = tot + mostSim

		return tot

	return novel

