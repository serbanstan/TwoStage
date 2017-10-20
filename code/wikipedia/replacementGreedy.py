"""
	An adaptation of the implementation to work with the code for the wikipedia dataset.

	elements - wiki pages
	children - elements on the second stage
	dictParents - a coverage dictionary from children to parents
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def replacementGreedy(l, k, children, elements, dictParents):

	n = len(elements)
	m = len(children)

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		S = []
		T = [[] for i in range(m)]

		# the best S sets for each category
		for j in range(l):
			xStar = findXStar(T)
			S.append(xStar)

			for i in range(m):
				if repGain(i, xStar, T[i]) > 0:
					y = minElement(i, xStar, T[i])
					if y != [] and len(T[i]) == k:
						T[i].remove(y)
					
					T[i].append(xStar)

		totalCost = 0
		for i in range(m):
			totalCost += computeCost(i, T[i])

		return S, totalCost, numEvals

	def findXStar(T):
		bestX = elements[0]
		bestValue = 0

		for x in elements:
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

	# write a function that computes the value of f for each category
	def computeCost(catIndex, A):
		tot = 0

		global numEvals
		numEvals = numEvals + 1

		for child in children[catIndex]:
			parents = dictParents[catIndex][child]
			# intersection
			for parent in parents:
				if parent in A:
					tot += 1
					break

		return tot

	return worker()

