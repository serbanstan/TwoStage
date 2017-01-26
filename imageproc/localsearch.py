"""
Local Search
"""

import numpy as np

def localsearch(l, k, featvec, nrm, nrmdist, catimg, epsilon):

	categories = catimg.keys()
	imgList = featvec.keys()

	n = len(imgList)
	m = len(categories)

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		np.random.seed(3)

		# work forthe first k entries
		S, picked = initS()

		initialCost = 0
		for c in categories:
			initialCost = initialCost + greedy(c, S)
		print 'Local search value after initialization = ', initialCost

		steps = 0

		done = False
		while not done:
			done = True

			for i in range(n):
				if picked[i] is True:

					# need to compute the set without imgList[i]
					noI = S[:]
					noI.remove(imgList[i])

					margGainnoI = margGain(noI, imgList[i])

					for j in range(n):
						if picked[j] is False:
							# see if swapping out i for j gives a better solution

							if (1 - epsilon) * margGain(S, imgList[j]) > margGainnoI:
								picked[i] = False
								picked[j] = True

								S.remove(imgList[i])
								S.append(imgList[j])

								# print "Replaced index ", i, " with index ", j, " => ", S

								done = False
								break

				if done == False:
					break

			intermCost = 0
			for c in categories:
				intermCost = intermCost + greedy(c, S)
			print 'Intermediate cost at step ', steps, ' = ', intermCost

			steps = steps + 1
			if steps > 100:
				print "did 100 steps"
				break

		totalCost = 0
		for c in categories:
			totalCost = totalCost + greedy(c, S)
		print 'Local Search gives cost = ', totalCost

		return S, totalCost, numEvals

	def margGain(S, elem):
		curCost = 0
		for c in categories:
			curCost = curCost + greedy(c, S)

		newS = S[:]
		newS.append(elem)
		newCost = 0
		for c in categories:
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
	# def initS():
	# 	S = []

	# 	picked = [False for i in range(n)]

	# 	for times in range(l):

	# 		bestCost = -1
	# 		bestInd = -1

	# 		for ind in range(n):
	# 			cost = 0

	# 			S.append(imgList[ind])

	# 			for cat in categories:
	# 				cost = cost + greedy(cat, S)

	# 			S.pop()

	# 			if cost > bestCost:
	# 				bestCost = cost
	# 				bestInd = ind

	# 		S.append(imgList[bestInd])
	# 		picked[bestInd] = True

	# 	return S, picked

	def initS():
		S = []

		picked = [False for i in range(n)]

		bestCost = -1
		bestInd = -1

		for imgInd in range(n):
			S.append(imgList[imgInd])

			curCost = 0
			for cat in categories:
				curCost = curCost + computeCost(cat, S)

			if curCost > bestCost:
				bestCost = curCost
				bestInd = imgInd

			S.pop()

		S.append(imgList[bestInd])
		picked[bestInd] = True

		# now, fill up the rest of S with (l-1) random elements
		while True:
			randChoice = np.random.choice(n, l-1)

			if bestInd in randChoice:
				continue
			else:
				for c in randChoice:
					S.append(imgList[c])
					picked[c] = True
				break

		return S, picked



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

