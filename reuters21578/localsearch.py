"""
Local Search
"""

import numpy as np

def localsearch(n, m, l, k, csim, articles, epsilon = 0.2):

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		np.random.seed(3)

		# work forthe first k entries
		S, picked = initS()

		initialCost = 0
		for c in range(m):
			initialCost = initialCost + greedy(c, S)
		print 'Local search value after initialization = ', initialCost

		steps = 0

		done = False
		while not done:
			done = True

			for i in range(n):
				if picked[i] is True:

					# need to compute the set without i
					noI = S[:]
					noI.remove(i)

					margGainnoI = margGain(noI, i)

					for j in range(n):
						if picked[j] is False:
							# see if swapping out i for j gives a better solution

							if (1 - epsilon) * margGain(S, j) > margGainnoI:
								picked[i] = False
								picked[j] = True

								S.remove(i)
								S.append(j)

								# print "Replaced index ", i, " with index ", j, " => ", S

								done = False
								break

				if done == False:
					break

			intermCost = 0
			for c in range(m):
				intermCost = intermCost + greedy(c, S)
			print 'Intermediate cost at step ', steps, ' = ', intermCost

			steps = steps + 1
			if steps > 100:
				print "did 100 steps"
				break

		totalCost = 0
		for c in range(m):
			totalCost = totalCost + greedy(c, S)
		print 'Local Search gives cost = ', totalCost

		return S, totalCost, numEvals

	def margGain(S, elem):
		curCost = 0
		for c in range(m):
			curCost = curCost + greedy(c, S)

		newS = S[:]
		newS.append(elem)
		newCost = 0
		for c in range(m):
			newCost = newCost + greedy(c, newS)

		return max(newCost - curCost, 0)

	# compute the greedy maximization solution for S for the second stage submodular maximization
	def greedy(cat, S):
		greedyS = []

		use = [False for s in S]

		for times in range(min(k, len(S))):
			# at each step, add the element that gives the greatest marginal gain 

			bestInd = -1
			bestCost = -1

			for ind in range(len(S)):
				if use[ind] == False:
					greedyS.append(S[ind])

					curCost = computeCost(cat, greedyS)
					if curCost > bestCost:
						bestCost = curCost
						bestInd = ind

					greedyS.pop()

			greedyS.append(S[bestInd])
			use[bestInd] = True

		return computeCost(cat, greedyS)

	# initialize by picking l elements, such that each new element maximizes the marginal gain
	def initS():
		S = []

		picked = [False for i in range(n)]

		for times in range(l):

			bestCost = -1
			bestInd = -1

			for ind in range(n):
				cost = 0

				S.append(ind)

				for cat in range(m):
					cost = cost + greedy(cat, S)

				S.pop()

				if cost > bestCost:
					bestCost = cost
					bestInd = ind

			S.append(bestInd)
			picked[bestInd] = True

		return S, picked


	# write a function that computes the value of f for each category
	def computeCost(catIndex, S):
		global numEvals
		numEvals = numEvals + 1

		tot = 0

		for articleInd in articles[catIndex]:
			mostSim = 0

			for s in S:
				mostSim = max(mostSim, csim[articleInd][s])

			tot = tot + mostSim

		return tot

	return worker()

