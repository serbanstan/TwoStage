"""
	A wrapper for Amin's algorithm in order to be able to use mapPartitions

	The 
"""

import numpy as np

def wrapper(n, m, l, k, sim, movies):

	# return the set of l elements that maximizes the greedy approach
	def novel(partition):
		local = [i for i in partition]

		S, picked = preK(local)

		# print "local: ", local
		# print "S: ", S

		# the best S sets for each category
		bestS = [S for i in range(m)]

		oldCost = 0
		for i in range(m):
			oldCost = oldCost + computeCost(i, bestS[i])

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

						catOld = computeCost(i, bestS[i])
						catNew = catOld

						# iterate through all k positions and rememeber the best swap
						for j in range(k):
							aux = bestS[i][j]

							bestS[i][j] = local[movInd]

							val = computeCost(i, bestS[i])
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

		return S

	# before hitting k elements, each element will just have to maximize the marginal gain
	def preK(local):
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
						curCost = curCost + computeCost(i, S)

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
	def computeCost(catIndex, S):
		tot = 0

		for mov in S:
			mostSim = 0

			for otherMov in movies[catIndex]:
				if otherMov != mov:
					candidate = np.dot(sim[:, mov], sim[:, otherMov])

					mostSim = max(mostSim, candidate)

			tot = tot + mostSim

		return tot

	return novel


