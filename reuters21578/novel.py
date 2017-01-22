"""
	Our algorithm

	n - number of articles
	m - number of categories
	l - size of S
	k - size of S_i
	X - the tf-idf score matrix
	articles - a dict() of type 'category' -> 'list of articles with that tag'
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image
import matplotlib.pyplot as plt

def novel(n, m, l, k, csim, articles):

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		# work forthe first k entries
		S, picked, history = preK()

		# the best S sets for each category
		bestS = [S[:] for i in range(m)]

		oldCost = 0
		for i in range(m):
			oldCost = oldCost + computeCost(i, bestS[i])

		for times in range(l - k):
			bestCost = -1
			bestInd = -1
			bestSwp = [-1 for i in range(m)]

			for articleInd in range(n):
				if picked[articleInd] == False:

					newCost = 0
					swp = [-1 for i in range(m)]

					# now, for each category, swap out the element that gives the least marginal gain
					for i in range(m):

						catOld = computeCost(i, bestS[i])
						catNew = catOld

						# iterate through all k positions and rememeber the best swap
						for j in range(k):
							aux = bestS[i][j]

							bestS[i][j] = articleInd

							val = computeCost(i, bestS[i])
							if val > catNew:
								catNew = val
								swp[i] = j

							bestS[i][j] = aux

						newCost = newCost + catNew

					if newCost > bestCost:
						bestCost = newCost
						bestInd = articleInd
						bestSwp = swp[:]

			# time to add in the best element we found

			if bestCost >= 0:	# make sure we have enough elements in the partition
				S.append(bestInd)
				picked[bestInd] = True
				for i in range(m):
					if bestSwp[i] != -1:
						bestS[i][bestSwp[i]] = bestInd
				oldCost = bestCost

			# again for plotting purposes
			curSum = 0
			for i in range(m):
				curSum = curSum + computeCost(i, bestS[i])
			history.append(curSum)

		print "We obtained objective value ", history[-1], " for set ", S

		# # a plot with the value for all l elements
		# fig = plt.figure()
		# fig.suptitle('Objective function for l steps', fontsize=14, fontweight='bold')

		# ax = fig.add_subplot(111)
		# ax.set_xlabel('element index')
		# ax.set_ylabel('objective value')

		# ax.axis([0, l, 0, 80])

		# plt.plot([i+1 for i in range(l)], history, 'ro')
		# plt.plot([i+1 for i in range(k)], history[:k], 'yo')

		# newhist = [0]
		# newhist.extend(history)
		# plt.plot([i for i in range(l + 1)], newhist, 'b')

		# plt.savefig('plotl.png')
		# Image.open('plotl.png').save('plotl.jpg','JPEG')

		return S, history[-1], numEvals

	# before hitting k elements, each element will just have to maximize the marginal gain
	def preK():
		S = []

		picked = [False for i in range(n)]

		history = []

		for times in range(k):
			bestCost = -1
			bestInd = -1

			for articleInd in range(n):
				if picked[articleInd] == False:

					S.append(articleInd)

					curCost = 0
					for i in range(m):
						curCost = curCost + computeCost(i, S)

					if curCost > bestCost:
						bestCost = curCost
						bestInd = articleInd

					S.pop()

			# make sure we have enough elements in the partition
			if bestCost >= 0:
				S.append(bestInd)
				picked[bestInd] = True

			# again for plotting purposes
			curSum = 0
			for i in range(m):
				curSum = curSum + computeCost(i, S)

			history.append(curSum)

		# print history

		# plotting the value of the function 
		# fig = plt.figure()
		# fig.suptitle('Objective function for first k steps', fontsize=14, fontweight='bold')

		# ax = fig.add_subplot(111)
		# ax.set_xlabel('element index')
		# ax.set_ylabel('objective value')

		# ax.axis([0, k+1, 0, 80])

		# plt.plot([(i+1) for i in range(k)], history, 'ro')

		# newhist = [0]
		# newhist.extend(history)
		# plt.plot([i for i in range(k+1)], newhist, 'b')

		# plt.savefig('plotk.png')
		# Image.open('plotk.png').save('plotk.jpg','JPEG')

		return S, picked, history


	# write a function that computes the value of f for each category
	# this is Facilityelemstion from - Learning mixtures of submodular functions for image collection summarization.
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


	# def computeCost(catIndex, S):
	# 	global numEvals
	# 	numEvals = numEvals + 1

	# 	tot = 0

	# 	for articleInd in articles[catIndex]:
	# 		mostSim = 0

	# 		for s in S:
	# 			mostSim = max(mostSim, cosine_similarity(X[articleInd].reshape(1,-1), X[s].reshape(1,-1))[0][0])

	# 		tot = tot + mostSim

	# 	return tot

	return worker()

