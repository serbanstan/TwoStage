"""
	Greedy Merge. 
"""

import numpy as np

def greedymerge(l, k, featvec, nrm, nrmdist, catimg):

	categories = catimg.keys()
	imgList = featvec.keys()

	n = len(imgList)
	m = len(categories)

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		totalCost = 0
		S = []

		# greedily maximize each function ignoring the constraint on L
		for c in categories:

			greedyS = []
			use = [False for i in range(n)]

			for times in range(k):
				# at each step, add the element that gives the greatest marginal gain 
				bestInd = -1
				bestCost = -1

				for ind in range(n):
					if use[ind] == False:
						greedyS.append(imgList[ind])

						curCost = computeCost(c, greedyS)
						if curCost > bestCost:
							bestCost = curCost
							bestInd = ind

						greedyS.pop()

				greedyS.append(imgList[bestInd])
				use[bestInd] = True

			totalCost = totalCost + computeCost(c, greedyS)
			S.extend(greedyS)

		S = list(set(S))

		print 'Greedy Merge gives cost = ', totalCost
		print 'Size of S is ', len(S)

		return S, totalCost, numEvals


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

