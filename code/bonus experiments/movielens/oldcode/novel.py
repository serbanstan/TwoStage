"""
	A wrapper for Amin's algorithm in order to be able to use mapPartitions

    n - number of movies
	m - number of categories
	l - size of S
	k - size of S_i
	simDist - a dictionary of distances between pairs of movies
	movies - a dict() of type 'category' -> 'list of movies in said category'
"""

import numpy as np

def wrapper(n, m, l, k, simDist, movies):

	# return the set of l elements that maximizes the greedy approach
	def novel(partition):
		global numEvals
		numEvals = 0

		# work forthe first k entries
		S, picked = preK(partition)

		# the best S sets for each category
		bestS = [S[:] for i in range(m)]

		oldCost = 0
		for i in range(m):
			oldCost = oldCost + computeCost(i, bestS[i])

		for times in range(l - k):
			bestCost = -1
			bestInd = -1
			bestSwp = [-1 for i in range(m)]

			for movInd in range(n):
				if picked[movInd] == False:

					newCost = 0
					swp = [-1 for i in range(m)]

					# now, for each category, swap out the element that gives the least marginal gain
					for i in range(m):

						catOld = computeCost(i, bestS[i])
						catNew = catOld

						# iterate through all k positions and rememeber the best swap
						for j in range(k):
							aux = bestS[i][j]

							bestS[i][j] = partition[movInd]

							val = computeCost(i, bestS[i])
							if val > catNew:
								catNew = val
								swp[i] = j

							bestS[i][j] = aux

						newCost = newCost + catNew

					if newCost > bestCost:
						bestCost = newCost
						bestInd = movInd
						bestSwp = swp[:]

			# time to add in the best element we found

			if bestCost >= 0:	# make sure we have enough elements in the partition
				S.append(partition[bestInd])
				picked[bestInd] = True
				for i in range(m):
					if bestSwp[i] != -1:
						bestS[i][bestSwp[i]] = partition[bestInd]
				oldCost = bestCost


		totalCost = 0
		for i in range(m):
			# print 'Cost for category ', i, ":", computeCost(i, bestS[i]), bestS[i]
			totalCost = totalCost + computeCost(i, bestS[i])
		print 'Our solution gives totalCost = ', totalCost


		# for catIndex in range(m):
		# 	newS = []

		# 	print 'Category ', catIndex

		# 	for i in range(k):
		# 		oldS = newS[:]
		# 		newS.append(bestS[catIndex][i])

		# 		print bestS[catIndex][i], " ", computeCost(catIndex, newS) - computeCost(catIndex, oldS)

		# 	print 'Total cost ', computeCost(catIndex, bestS[catIndex]), "\n"

		# sanity check
		# print len(S)
		# for i in range(m):
		#     print set(bestS[i]).issubset(set(S)), len(bestS[i]) == k

		return S, totalCost, numEvals
#		return S, totalCost, numEvals, bestS

	# before hitting k elements, each element will just have to maximize the marginal gain
	def preK(partition):
		S = []

		picked = [False for i in range(len(partition))]

		for times in range(k):
			bestCost = -1
			bestInd = -1

			for movInd in range(len(partition)):
				if picked[movInd] == False:

					mov = partition[movInd]
					S.append(mov)

					curCost = 0
					for i in range(m):
						curCost = curCost + computeCost(i, S)

					if curCost > bestCost:
						bestCost = curCost
						bestInd = movInd

					S.pop()

			# print bestInd

			# make sure we have enough elements in the partition
			if bestCost >= 0:
				S.append(partition[bestInd])
				picked[bestInd] = True

			# print bestCost

		return S, picked


	# write a function that computes the value of f for each category
	# this is Facility Location from - Learning mixtures of submodular functions for image collection summarization.
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

	return novel

