"""
	A wrapper for replacementGreedy

	n - number of images
	m - number of categories
	l - size of S
	k - size of S_i
	exempDist - a dictionary with distances from elements to the phantom exemplar
	dist - a dictionary with the l2 norm distance between the images
	featvec - a dict of type image_name -> feature_vector
	catimg - a dict of type category -> images_in_said_category
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def replacementGreedy(l, k, featvec, exempDist, dist, catimg):

	# a list of categories
	categories = catimg.keys()

	# a list of images
	imgList = featvec.keys()

	n = len(imgList)
	m = len(categories)

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		S = []
		T = [[] for i in range(m)]
 
		for j in range(l):
			xStar = findXStar(T)
			S.append(xStar)

			for i in range(m):
				if repGain(i, xStar, T[i]) > 0:
					y = minElement(i, xStar, T[i])

					# check if we are in the case where len(T[i]) < k
					if y != [] and len(T[i]) == k:
						T[i].remove(y)

					T[i].append(xStar)

		totalCost = 0
		for i in range(m):
			totalCost += computeCost(i, T[i])

		return S, totalCost, numEvals

	def findXStar(T):
		bestX = imgList[0]
		bestValue = 0

		for x in imgList:
			curValue = 0
			for i in range(m):
				curValue = curValue + repGain(i, x, T[i])

			if curValue > bestValue:
				bestValue = curValue
				bestX = x

		return bestX

	def repGain(i, x, A):
		if len(A) < k:
			newA = A[:]
			newA.append(x)

			return computeCost(i, newA) - computeCost(i, A)
		else:
			y = minElement(i, x, A)

			# if minElement returns the empty set, repGain is just 0
			if y == []:
				return 0

			newA = A[:]
			newA.remove(y)
			newA.append(x)

			assert (computeCost(i, newA) - computeCost(i, A) > 0), "cost(newA) - cost(oldA) should be > 0"

			return computeCost(i, newA) - computeCost(i, A)

	def minElement(i, x, A):
		if len(A) < k:
			return []

		initialCost = computeCost(i, A);

		bestY = []
		bestValue = 0

		for y in A:
			newA = A[:]

			newA.remove(y)
			newA.append(x)

			newCost = computeCost(i, newA)

			if newCost > initialCost:
				if newCost - initialCost > bestValue:
					bestValue = newCost - initialCost
					bestY = y

		return bestY


	# this is exemplar based clustering from - https://las.inf.ethz.ch/files/mirzasoleiman13distributed.pdf
	def computeCost(i, S):
		cat = categories[i]

		global numEvals
		numEvals = numEvals + 1

		# we are interested in elements from S that are in category i
		catS = list(set(S).intersection(catimg[cat]))
		
		# we initialize with e0 = 0
		t1 = 0
		for img in catimg[cat]:
			t1 = t1 + exempDist[img]

		t2 = 0
		for img in catimg[cat]:
			# the value for e0
			best = exempDist[img]

			for s in catS:
				best = min(best, dist[(img, s)])

			t2 = t2 + best

		return (t1 - t2) / len(catimg[cat])

	return worker()


