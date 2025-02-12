import random
import math, random, copy
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from scipy.spatial import distance


class Robot:
    #class variables
    description = "This is the Robot for Pairwise in Genetic Algorithm"
    author = "Daniel Cinalli"


    #methods
    def __init__(self):
        #robot decision strategy

        #not used
        self.pro_cost = .5
        self.anti_cost = .5

    #return pro_cost rate
    def PrintStyle(self):
        return self.pro_cost

    #take decision on what objective to look at: 0=first=cost=f1; 1=second=production=f2
    def TakeDecision(self, value, ind1, ind2):

        coin = round(random.uniform(0, 1.0), 2)
        if coin <= value:
            return self.GetBetterCost(ind1,ind2)
        else:
            return self.GetBetterProduction(ind1, ind2)

    #take decision on what point to compare the distance: choose the closest
    def TakeDecisionDist(self, ref, ind1, ind2):

        #ref[0], ref[1] = reference point
        #ind1[0], ind1[1] = individual 1 fitness
        point1 = [ind1[0], ind1[1]]
        #ind2[0], ind2[1] = individual 2 fitness
        point2 = [ind2[0], ind2[1]]

        dst1 = distance.euclidean(ref,point1)
        dst2 = distance.euclidean(ref,point2)


        if dst1 <=dst2:
            return 0
        else:
            return 1

    def TakeDecisionDist3D(self, ref, ind1, ind2):

        #ref[0], ref[1] = reference point
        #ind1[0], ind1[1] = individual 1 fitness
        point1 = [ind1[0], ind1[1], ind1[2]]
        #ind2[0], ind2[1] = individual 2 fitness
        point2 = [ind2[0], ind2[1], ind2[2]]

        dst1 = distance.euclidean(ref,point1)
        dst2 = distance.euclidean(ref,point2)


        if dst1 <=dst2:
            return 0
        else:
            return 1

    #get the better individual on cost
    def GetBetterCost(self, ind1, ind2):
        if ind1[0]<=ind2[0]:
            return 0
        else:
            return 1

    #get the better individual on production
    def GetBetterProduction(self, ind1, ind2):
        if ind1[1]<=ind2[1]:
            return 0
        else:
            return 1

    def expectation_maximization(self, t, nbclusters=2, nbiter=1, normalize=False,\
            epsilon=0.1, monotony=False, datasetinit=True):
        """
        Each row of t is an observation, each column is a feature
        'nbclusters' is the number of seeds and so of clusters
        'nbiter' is the number of iterations
        'epsilon' is the convergence bound/criterium

        """
        def pnorm(x, m, s):
            """
            Compute the multivariate normal distribution with values vector x,
            mean vector m, sigma (variances/covariances) matrix s
            """
            xmt = np.matrix(x-m).transpose()
            for i in xrange(len(s)):
                if s[i,i] <= sys.float_info[3]: # min float
                    s[i,i] = sys.float_info[3]
            sinv = np.linalg.inv(s)
            xm = np.matrix(x-m)
            return (2.0*math.pi)**(-len(x)/2.0)*(1.0/math.sqrt(np.linalg.det(s)))\
                    *math.exp(-0.5*(xm*sinv*xmt))

        def draw_params():
                if datasetinit:
                    tmpmu = np.array([1.0*t[random.uniform(0,nbobs),:]],np.float64)
                else:
                    tmpmu = np.array([random.uniform(min_max[f][0], min_max[f][1])\
                            for f in xrange(nbfeatures)], np.float64)
                return {'mu': tmpmu,\
                        'sigma': np.matrix(np.diag(\
                        [(min_max[f][1]-min_max[f][0])/2.0\
                        for f in xrange(nbfeatures)])),\
                        'proba': 1.0/nbclusters}

        nbobs = t.shape[0]
        nbfeatures = t.shape[1]
        min_max = []
        # find xranges for each features
        for f in xrange(nbfeatures):
            min_max.append((t[:,f].min(), t[:,f].max()))

        ### Normalization
        if normalize:
            for f in xrange(nbfeatures):
                t[:,f] -= min_max[f][0]
                t[:,f] /= (min_max[f][1]-min_max[f][0])
        min_max = []
        for f in xrange(nbfeatures):
            min_max.append((t[:,f].min(), t[:,f].max()))
        ### /Normalization

        result = {}
        quality = 0.0 # sum of the means of the distances to centroids
        random.seed()
        Pclust = np.ndarray([nbobs,nbclusters], np.float64) # P(clust|obs)
        Px = np.ndarray([nbobs,nbclusters], np.float64) # P(obs|clust)
        # iterate nbiter times searching for the best "quality" clustering
        for iteration in xrange(nbiter):
            ##############################################
            # Step 1: draw nbclusters sets of parameters #
            ##############################################
            params = [draw_params() for c in xrange(nbclusters)]
            old_log_estimate = sys.maxsize         # init, not true/real
            log_estimate = sys.maxint/2 + epsilon # init, not true/real
            estimation_round = 0
            # Iterate until convergence (EM is monotone) <=> < epsilon variation
            while (abs(log_estimate - old_log_estimate) > epsilon\
                    and (not monotony or log_estimate < old_log_estimate)):
                restart = False
                old_log_estimate = log_estimate
                ########################################################
                # Step 2: compute P(Cluster|obs) for each observations #
                ########################################################
                for o in xrange(nbobs):
                    for c in xrange(nbclusters):
                        # Px[o,c] = P(x|c)
                        Px[o,c] = pnorm(t[o,:],\
                                params[c]['mu'], params[c]['sigma'])
                #for o in xrange(nbobs):
                #    Px[o,:] /= math.fsum(Px[o,:])
                for o in xrange(nbobs):
                    for c in xrange(nbclusters):
                        # Pclust[o,c] = P(c|x)
                        Pclust[o,c] = Px[o,c]*params[c]['proba']
                #    assert math.fsum(Px[o,:]) >= 0.99 and\
                #            math.fsum(Px[o,:]) <= 1.01
                for o in xrange(nbobs):
                    tmpSum = 0.0
                    for c in xrange(nbclusters):
                        tmpSum += params[c]['proba']*Px[o,c]
                    Pclust[o,:] /= tmpSum
                    #assert math.fsum(Pclust[:,c]) >= 0.99 and\
                    #        math.fsum(Pclust[:,c]) <= 1.01
                ###########################################################
                # Step 3: update the parameters (sets {mu, sigma, proba}) #
                ###########################################################
                print "iter:", iteration, " estimation#:", estimation_round,\
                        " params:", params
                for c in xrange(nbclusters):
                    tmpSum = math.fsum(Pclust[:,c])
                    params[c]['proba'] = tmpSum/nbobs
                    if params[c]['proba'] <= 1.0/nbobs:           # restart if all
                        restart = True                             # converges to
                        print "Restarting, p:",params[c]['proba'] # one cluster
                        break
                    m = np.zeros(nbfeatures, np.float64)
                    for o in xrange(nbobs):
                        m += t[o,:]*Pclust[o,c]
                    params[c]['mu'] = m/tmpSum
                    s = np.matrix(np.diag(np.zeros(nbfeatures, np.float64)))
                    for o in xrange(nbobs):
                        s += Pclust[o,c]*(np.matrix(t[o,:]-params[c]['mu']).transpose()*\
                                np.matrix(t[o,:]-params[c]['mu']))
                        #print ">>>> ", t[o,:]-params[c]['mu']
                        #diag = Pclust[o,c]*((t[o,:]-params[c]['mu'])*\
                        #        (t[o,:]-params[c]['mu']).transpose())
                        #print ">>> ", diag
                        #for i in xrange(len(s)) :
                        #    s[i,i] += diag[i]
                    params[c]['sigma'] = s/tmpSum
                    print "------------------"
                    print params[c]['sigma']

                ### Test bound conditions and restart consequently if needed
                if not restart:
                    restart = True
                    for c in xrange(1,nbclusters):
                        if not np.allclose(params[c]['mu'], params[c-1]['mu'])\
                        or not np.allclose(params[c]['sigma'], params[c-1]['sigma']):
                            restart = False
                            break
                if restart:                # restart if all converges to only
                    old_log_estimate = sys.maxint          # init, not true/real
                    log_estimate = sys.maxint/2 + epsilon # init, not true/real
                    params = [draw_params() for c in xrange(nbclusters)]
                    continue
                ### /Test bound conditions and restart

                ####################################
                # Step 4: compute the log estimate #
                ####################################
                log_estimate = math.fsum([math.log(math.fsum(\
                        [Px[o,c]*params[c]['proba'] for c in xrange(nbclusters)]))\
                        for o in xrange(nbobs)])
                print "(EM) old and new log estimate: ",\
                        old_log_estimate, log_estimate
                estimation_round += 1

            # Pick/save the best clustering as the final result
            quality = -log_estimate
            if not quality in result or quality > result['quality']:
                result['quality'] = quality
                result['params'] = copy.deepcopy(params)
                result['clusters'] = [[o for o in xrange(nbobs)\
                        if Px[o,c] == max(Px[o,:])]\
                        for c in xrange(nbclusters)]
        return result
    #




