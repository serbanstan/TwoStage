# Pick best k for each category. From the union, take the elements that occur most often. Break ties randomly. 

import numpy as np
import random
from PIL import Image
import matplotlib.pyplot as plt

from collections import Counter

def dumb2(l, k, featvec, catimg):

	categories = catimg.keys()
	imgList = featvec.keys()

	def worker():
		S = []

		# add to S the best k for each category
		for c in categories:
			picked = dict(zip([img for img in imgList], [False for img in imgList]))

			curS = []

			for times in range(k):
				best = curS[:]

				for img in imgList:
					if picked[img] == False:
						aux = curS[:]
						aux.append(img)

						if computeCost(c, aux) > computeCost(c, best):
							best = aux[:]

				curS = best[:]

			S.extend(curS)

		# pick the l elements that appear most. randomly deal with ties. 
		mc = Counter(S).most_common(l)
		S = []
		for times in range(l):
			S.append(mc[times][0])

		# now, to compute the cost of S, we'll greedily maximize our submodular functions based on our cluster set S
		bestS = dict(zip([c for c in categories], [[] for c in categories]))

		for c in categories:
			picked = dict(zip([s for s in S], [False for s in S]))

			for steps in range(k):
				# initialize best with a valid entry
				bestCost = -1
				bestImg = -1

				for s in S:
					# try to see which elements maximizes the marginal gain
					if picked[s] == False:
						newS = bestS[c][:]
						newS.append(s)

						if computeCost(c, newS) > bestCost:
							bestCost = computeCost(c, newS)
							bestImg = s

				if bestCost > -1:
					bestS[c].append(bestImg)
				else:
					print "error"

		# compute the objective value and output it
		totalCost = 0
		for c in categories:
			totalCost = totalCost + computeCost(c, bestS[c])
		print 'Obtained cost ', totalCost, ' for set ', S

		return S

	def computeCost(cat, S):
		# we initialize with e0 = 0
		t1 = 0
		for img in catimg[cat]:
			t1 = t1 + np.linalg.norm(featvec[img])

		t2 = 0
		for img in catimg[cat]:
			# the value for e0
			best = np.linalg.norm(featvec[img])

			for s in S:
				best = min(best, np.linalg.norm(featvec[img] - featvec[s]))

			t2 = t2 + best

		return (t1 - t2) / len(catimg[cat])

	return worker()