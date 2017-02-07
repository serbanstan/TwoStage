"""
	A wrapper for Greedy Sum
"""

import numpy as np

def greedysum(l, k, featvec, nrm, nrmdist, catimg):

	categories = catimg.keys()
	imgList = featvec.keys()

	n = len(imgList)
	m = len(categories)

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		# greedily pick l elements
		picked = [False for i in range(n)]
		S = []

		for times in range(l):
			bestInd = -1
			bestCost = -1

			for ind in range(n):
				S.append(imgList[ind])

				curCost = 0
				for c in categories:
					curCost = curCost + computeCost(c, S)

				if curCost > bestCost:
					bestCost = curCost
					bestInd = ind

				S.pop()

			S.append(imgList[bestInd])
			picked[bestInd] = True

		totalCost = 0
		for c in categories:
			totalCost = totalCost + greedy(c, S)
		print 'Greedy Sum gives cost = ', totalCost

		return S, totalCost, numEvals

	# compute the greedy maximization solution for S for the second stage submodular maximization
	def greedy(c, S):
		greedyS = []

		use = [False for s in S]

		for times in range(k):
			# at each step, add the element that gives the greatest marginal gain 

			bestInd = -1
			bestCost = -1

			for ind in range(len(S)):
				if use[ind] == False:
					greedyS.append(S[ind])

					curCost = computeCost(c, greedyS)
					if curCost > bestCost:
						bestCost = curCost
						bestInd = ind

					greedyS.pop()

			greedyS.append(S[bestInd])
			use[bestInd] = True

		return computeCost(c, greedyS)


	# write a function that computes the value of f for each category
	def computeCost(cat, S):
		global numEvals
		numEvals = numEvals + 1
		
		# we initialize with e0 = 0
		t1 = 0
		for img in catimg[cat]:
			t1 = t1 + nrm[img]

		t2 = 0
		for img in catimg[cat]:
			# the value for e0
			best = nrm[img]

			for s in S:
				best = min(best, nrmdist[(img, s)])

			t2 = t2 + best

		return (t1 - t2) / len(catimg[cat])

	return worker()

