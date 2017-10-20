"""
	An adaptation of the implementation to work with the code for the wikipedia dataset.

	elements - number of wiki pages
	children - number of elements on the second stage
	dictParents - a coverage dictionary from children to parents
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def novel(l, k, children, elements, dictParents):

	n = len(elements)
	m = len(children)

	# return the set of l elements that maximizes the greedy approach
	def worker():
		global numEvals
		numEvals = 0

		S, picked, history = preK()

		# print 'Solution set after the first k rounds ', S
		# print computeCost(0, S), computeCost(1, S), computeCost(2, S), computeCost(3, S), computeCost(4, S)

		# return S

		# the best S sets for each category
		bestS = [S[:] for i in range(m)]

		oldCost = 0
		for i in range(m):
			oldCost = oldCost + computeCost(i, bestS[i])

		for times in range(l - k):
			bestCost = -1
			bestInd = -1
			bestSwp = [-1 for i in range(m)]

			for ind in range(len(elements)):
				if picked[ind] == False:

					newCost = 0
					swp = [-1 for i in range(m)]

					# now, for each category, swap out the element that gives the least marginal gain
					for i in range(m):

						catOld = computeCost(i, bestS[i])
						catNew = catOld

						# iterate through all k positions and rememeber the best swap
						for j in range(k):
							aux = bestS[i][j]
							bestS[i][j] = elements[ind]

							val = computeCost(i, bestS[i])
							if val > catNew:
								catNew = val
								swp[i] = j

							bestS[i][j] = aux

						newCost = newCost + catNew

					if newCost > bestCost:
						bestCost = newCost
						bestInd = ind
						bestSwp = swp[:]

			# time to add in the best element we found
			if bestCost >= 0:	# make sure we have enough elements in the partition
				S.append(elements[bestInd])
				picked[bestInd] = True
				for i in range(m):
					if bestSwp[i] != -1:
						bestS[i][bestSwp[i]] = elements[bestInd]
				oldCost = bestCost

			# again for plotting purposes
			curSum = 0
			for i in range(m):
				curSum = curSum + computeCost(i, bestS[i])
			history.append(curSum)

		# a plot with the value for all l elements
		# fig = plt.figure()
		# fig.suptitle('Objective function for l steps', fontsize=14, fontweight='bold')

		# ax = fig.add_subplot(111)
		# ax.set_xlabel('element index')
		# ax.set_ylabel('objective value')

		# ax.axis([0, l, 0, 500])

		# plt.plot([i+1 for i in range(l)], history, 'ro')
		# plt.plot([i+1 for i in range(k)], history[:k], 'yo')

		# newhist = [0]
		# newhist.extend(history)
		# plt.plot([i for i in range(l + 1)], newhist, 'b')

		# plt.savefig('plotl.png')
		# Image.open('plotl.png').save('plotl.jpg','JPEG')

		# print 'Our solution set ', S
		# print computeCost(0, bestS[0]), computeCost(1, bestS[1]), computeCost(2, bestS[2]), computeCost(3, bestS[3]), computeCost(4, bestS[4])

		curSum = 0
		for i in range(m):
			curSum = curSum + computeCost(i, bestS[i])
		# print 'We obtained value ', curSum

		# print S, curSum
		# print 'sanity check:'
		# for i in range(m):
		#  	print bestS[i], len(bestS[i]), set(bestS[i]).issubset(set(S)), computeCost(i, bestS[i])

		return S, bestS, curSum, numEvals

	# before hitting k elements, each element will just have to maximize the marginal gain
	def preK():
		S = []

		picked = [False for i in range(len(elements))]

		history = []

		for times in range(k):
			bestCost = -1
			bestInd = -1

			# iterate through the elements
			for ind in range(len(elements)):
				if picked[ind] == False:

					S.append(elements[ind])

					curCost = 0
					for i in range(m):
						curCost = curCost + computeCost(i, S)

					if curCost > bestCost:
						bestCost = curCost
						bestInd = ind

					S.pop()

			# make sure we have enough elements in the partition
			if bestCost >= 0:
				S.append(elements[bestInd])
				picked[bestInd] = True

			curSum = 0
			for i in range(m):
				curSum = curSum + computeCost(i, S)
			history.append(curSum)

		# plotting the value of the function 
		# fig = plt.figure()
		# fig.suptitle('Objective function for first k steps', fontsize=14, fontweight='bold')

		# ax = fig.add_subplot(111)
		# ax.set_xlabel('element index')
		# ax.set_ylabel('objective value')

		# ax.axis([0, k+1, 0, 500])

		# plt.plot([(i+1) for i in range(k)], history, 'ro')

		# newhist = [0]
		# newhist.extend(history)
		# plt.plot([i for i in range(k+1)], newhist, 'b')

		# plt.savefig('plotk.png')
		# Image.open('plotk.png').save('plotk.jpg','JPEG')

		return S, picked, history


	# write a function that computes the value of f for each category
	def computeCost(catIndex, S):
		tot = 0

		global numEvals
		numEvals = numEvals + 1

		for child in children[catIndex]:
			parents = dictParents[catIndex][child]
			# intersection
			for parent in parents:
				if parent in S:
					tot += 1
					break

		# # check how many children are activated by S
		# for cover in dictParents[catIndex].values():
		# 	for c in cover:
		# 		if c in S:
		# 			tot = tot + 1
		# 			break

		return tot

	return worker()

