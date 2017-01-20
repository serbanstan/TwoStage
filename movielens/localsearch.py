"""
	A wrapper for Local Search in the movielens setting.

	n - number of movies
	m - number of categories
	l - size of S
	k - size of S_i
	sim - the similarity matrix for all 100k+ movies
	movies - a dict() of type 'category' -> 'list of movies in said category'
"""

import numpy as np

def lsWrapper(n, m, l, k, epsilon, sim, movies):

	# return the set of l elements that maximizes the greedy approach
	def ls(partition):
		global numEvals
		numEvals = 0

		np.random.seed(3)

		# work forthe first k entries
		S, picked = initS(partition)

		initialCost = 0
		for i in range(m):
			initialCost = initialCost + greedy(i, S)
		print 'Picking l random elements gives cost = ', initialCost

		steps = 0

		done = False
		while not done:
			done = True

			for i in range(n):
				if picked[i] is True:

					# need to compute the set without partition[i]
					noI = S[:]
					noI.remove(partition[i])

					margGainnoI = margGain(noI, partition[i])

					for j in range(n):
						if picked[j] is False:
							# see if swapping out i for j gives a better solution

							if (1 - epsilon) * margGain(S, partition[j]) > margGainnoI:
								picked[i] = False
								picked[j] = True

								S.remove(partition[i])
								S.append(partition[j])

								# print "Replaced index ", i, " with index ", j, " => ", S

								done = False
								break

				if done == False:
					break

			intermCost = 0
			for i in range(m):
				intermCost = intermCost + greedy(i, S)
			print 'Intermediate cost at step ', steps, ' = ', intermCost

			steps = steps + 1
			if steps > 100:
				print "did 100 steps"
				break

		totalCost = 0
		for i in range(m):
			totalCost = totalCost + greedy(i, S)
		print 'Local Search gives cost = ', totalCost

		return S, totalCost, numEvals

	def margGain(S, elem):
		curCost = 0
		for i in range(m):
			curCost = curCost + greedy(i, S)

		newS = S[:]
		newS.append(elem)
		newCost = 0
		for i in range(m):
			newCost = newCost + greedy(i, newS)

		return max(newCost - curCost, 0)

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

	# initialize with singleton that has largest contribution plus (l-1) random elements
	def initS(partition):
		S = []

		picked = [False for i in range(n)]

		bestCost = -1
		bestInd = -1

		for movInd in range(n):
			mov = partition[movInd]

			S.append(mov)

			curCost = 0
			for i in range(m):
				curCost = curCost + computeCost(i, S)

			if curCost > bestCost:
				bestCost = curCost
				bestInd = movInd

			S.pop()

		S.append(partition[bestInd])
		picked[bestInd] = True

		# now, fill up the rest of S with (l-1) random elements
		while True:
			randChoice = np.random.choice(n, l-1)

			if bestInd in randChoice:
				continue
			else:
				for c in randChoice:
					S.append(partition[c])
					picked[c] = True
				break

		return S, picked


	# write a function that computes the value of f for each category
	# this is Facilitypartitiontion from - Learning mixtures of submodular functions for image collection summarization.
	def computeCost(catIndex, S):
		tot = 0

		global numEvals
		numEvals = numEvals + 1

		for mov in movies[catIndex]:
			mostSim = 0

			for s in S:
				mostSim = max(mostSim, np.dot(sim[mov], sim[s]))

			tot = tot + mostSim

		return tot

	return ls

