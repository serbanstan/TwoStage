"""
	A wrapper for Amin's algorithm in order to be able to use mapPartitions

	n - number of images
	m - number of categories
	l - size of S
	k - size of S_i
	featvec - a dict of type image_name -> feature_vector
	catimg - a dict of type category -> images_in_said_category
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def novel(l, k, featvec, nrm, nrmdist, catimg):

	categories = catimg.keys()
	imgList = featvec.keys()

	n = len(imgList)
	m = len(categories)

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		# work for the first k entries
		S, picked, history = preK(imgList)

		# the best S sets for each category
		bestS = dict(zip([c for c in categories], [S[:] for c in categories]))

		oldCost = 0
		for c in categories:
			oldCost = oldCost + computeCost(c, bestS[c])

		for times in range(l - k):
			bestCost = -1
			bestInd = -1
			bestSwp = dict(zip([c for c in categories], [-1 for c in categories]))

			for imgInd in range(n):
				if picked[imgInd] == False:

					newCost = 0
					swp = dict(zip([c for c in categories], [-1 for c in categories]))

					# now, for each category, swap out the element that gives the least marginal gain
					for c in categories:

						catOld = computeCost(c, bestS[c])
						catNew = catOld

						# iterate through all k positions and rememeber the best swap
						for j in range(k):
							aux = bestS[c][j]

							bestS[c][j] = imgList[imgInd]

							val = computeCost(c, bestS[c])
							if val > catNew:
								catNew = val
								swp[c] = j

							bestS[c][j] = aux

						newCost = newCost + catNew

					if newCost > bestCost:
						bestCost = newCost
						bestInd = imgInd
						bestSwp = swp.copy()

			# time to add in the best element we found

			if bestCost >= 0:	# make sure we have enough elements in the partition
				S.append(imgList[bestInd])
				picked[bestInd] = True
				for c in categories:
					if bestSwp[c] != -1:
						bestS[c][bestSwp[c]] = imgList[bestInd]
				oldCost = bestCost

			# again for plotting purposes
			curSum = 0
			for c in categories:
				curSum = curSum + computeCost(c, bestS[c])
			history.append(curSum)

		print "We obtained objective value ", history[-1], " for set ", S

		# a plot with the value for all l elements
		# fig = plt.figure()
		# fig.suptitle('Objective function for l steps', fontsize=14, fontweight='bold')

		# ax = fig.add_subplot(111)
		# ax.set_xlabel('element index')
		# ax.set_ylabel('objective value')

		# ax.axis([0, l, 0, 30])

		# plt.plot([i+1 for i in range(l)], history, 'ro')
		# plt.plot([i+1 for i in range(k)], history[:k], 'yo')

		# newhist = [0]
		# newhist.extend(history)
		# plt.plot([i for i in range(l + 1)], newhist, 'b')

		# plt.savefig('plotl.png')
		# Image.open('plotl.png').save('plotl.jpg','JPEG')

		return S, bestS, history[-1]

	# before hitting k elements, each element will just have to maximize the marginal gain
	def preK(imgList):
		S = []

		picked = [False for i in range(n)]

		history = []

		for times in range(k):
			bestCost = -1
			bestInd = -1

			for imgInd in range(n):
				if picked[imgInd] == False:

					img = imgList[imgInd]
					S.append(img)

					curCost = 0
					for c in categories:
						curCost = curCost + computeCost(c, S)

					if curCost > bestCost:
						bestCost = curCost
						bestInd = imgInd

					S.pop()

			# make sure we have enough elements in the partition
			if bestCost >= 0:
				S.append(imgList[bestInd])
				picked[bestInd] = True

			# again for plotting purposes
			curSum = 0
			for c in categories:
				curSum = curSum + computeCost(c, S)
			history.append(curSum)

		# plotting the value of the function 
		# fig = plt.figure()
		# fig.suptitle('Objective function for first k steps', fontsize=14, fontweight='bold')

		# ax = fig.add_subplot(111)
		# ax.set_xlabel('element index')
		# ax.set_ylabel('objective value')

		# ax.axis([0, k+1, 0, 30])

		# plt.plot([(i+1) for i in range(k)], history, 'ro')

		# newhist = [0]
		# newhist.extend(history)
		# plt.plot([i for i in range(k+1)], newhist, 'b')

		# plt.savefig('plotk.png')
		# Image.open('plotk.png').save('plotk.jpg','JPEG')

		return S, picked, history


	# write a function that computes the value of f for each category
	# def computeCost(cat, S):
	# 	tot = 0

	# 	for img in catimg[cat]:
	# 		best = 0

	# 		for s in S:
	# 			best = max(best, 1.0 / (np.linalg.norm(featvec[img] - featvec[s]) + 1))

	# 		tot = tot + best

	# 	return tot

	# def computeCost(cat, S):
	# 	global numEvals
	# 	numEvals = numEvals + 1
		
	# 	# we initialize with e0 = 0
	# 	t1 = 0
	# 	for img in catimg[cat]:
	# 		t1 = t1 + np.linalg.norm(featvec[img])

	# 	t2 = 0
	# 	for img in catimg[cat]:
	# 		# the value for e0
	# 		best = np.linalg.norm(featvec[img])

	# 		for s in S:
	# 			best = min(best, np.linalg.norm(featvec[img] - featvec[s]))

	# 		t2 = t2 + best

	# 	return (t1 - t2) / len(catimg[cat])

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


