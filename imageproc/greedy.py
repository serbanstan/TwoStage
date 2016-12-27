import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def greedy(l, k, featvec, catimg):

	categories = catimg.keys()
	imgList = featvec.keys()

	# generate l clusters
	# then, for each function, pick the best k clusters out of the l clsuters that maximize its value
	def worker():
		S = getClusters()

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

		ax.axis([0, k+1, 0, 300])

		plt.plot([(i+1) for i in range(k)], history, 'ro')

		newhist = [0]
		newhist.extend(history)
		plt.plot([i for i in range(k+1)], newhist, 'b')

		plt.savefig('greedy_plot.png')
		Image.open('greedy_plot.png').save('greedy_plot.jpg','JPEG')

		return S

	def getClusters():
		clusterCenters = [featvec[i] for i in np.random.choice(imgList, l)]

		cnt = 0

		improve = True
		while improve:
			cnt = cnt + 1

			improve = False

			newCenters = [c * 0 for c in clusterCenters]
			numImgs = [0 for c in clusterCenters]

			for img in imgList:
				closest = 0

				for i in range(l):
					if np.linalg.norm(featvec[img] - clusterCenters[i]) < \
						np.linalg.norm(featvec[img] - clusterCenters[closest]):
						closest = i

				newCenters[closest] = [sum(x) for x in zip(newCenters[closest], featvec[img])]
				numImgs[closest] = numImgs[closest] + 1

			for i in range(l):
				if numImgs[i] > 0:
					newCenters[i] = [1.0 * x / numImgs[i] for x in newCenters[i]]
					# print i, numImgs[i], newCenters[i]
				else:
					# print i
					newCenters[i] = [0 for c in categories]

			for i in range(l):
				if np.linalg.norm(newCenters[i] - clusterCenters[i]) > 1e-5:
					improve = True
					break

			clusterCenters = np.copy(newCenters)

		print 'Converged after ', cnt, ' iterations'

		# now, return the images that are closest to these clusters
		S = []
		for i in range(l):
			closest = imgList[0]

			for img in imgList:
				if np.linalg.norm(featvec[img] - clusterCenters[i]) < \
					np.linalg.norm(featvec[closest] - clusterCenters[i]):
					closest = img

			S.append(closest)

		return list(set(S))


	# write a function that computes the value of f for each category
	def computeCost(cat, S):
		tot = 0

		for img in catimg[cat]:
			best = 0

			for s in S:
				best = max(best, computeSim(featvec[img], featvec[s]))
				# best = max(best, 1 / (np.linalg.norm(featvec[img] - featvec[s]) + 1))

			tot = tot + best

		return tot

	def computeSim(a, b):
		return 1.0 / (np.linalg.norm(a - b) + 1)

	return worker()