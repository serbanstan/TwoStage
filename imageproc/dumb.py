# Pick L points randomly, then greedily select the best k for each category 

import numpy as np
import random
from PIL import Image
import matplotlib.pyplot as plt

def dumb(l, k, featvec, catimg):

	categories = catimg.keys()
	imgList = featvec.keys()

	def worker():
		# randomly remain with only l elements
		S = random.sample(imgList, l)

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

		# plotting
		history = []
		for step in range(k):
			curTot = 0

			for c in categories:
				curTot = curTot + computeCost(c, bestS[c][:(step + 1)])

			history.append(curTot)

		fig = plt.figure()
		fig.suptitle('Objective function for first k steps', fontsize=14, fontweight='bold')

		ax = fig.add_subplot(111)
		ax.set_xlabel('element index')
		ax.set_ylabel('objective value')

		ax.axis([0, k+1, 0, 30])

		plt.plot([(i+1) for i in range(k)], history, 'ro')

		newhist = [0]
		newhist.extend(history)
		plt.plot([i for i in range(k+1)], newhist, 'b')

		plt.savefig('dumb_plot.png')
		Image.open('dumb_plot.png').save('dumb_plot.jpg','JPEG')

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