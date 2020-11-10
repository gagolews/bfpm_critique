# ############################################################################ #
#                                                                              #
#   Copyleft (C) 2020, Marek Gagolewski <https://www.gagolewski.com>           #
#                                                                              #
#                                                                              #
#   This program is free software: you can redistribute it and/or modify       #
#   it under the terms of the GNU Affero General Public License                #
#   Version 3, 19 November 2007, published by the Free Software Foundation.    #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the               #
#   GNU Affero General Public License Version 3 for more details.              #
#   You should have received a copy of the License along with this program.    #
#   If this is not the case, refer to <https://www.gnu.org/licenses/>.         #
#                                                                              #
# ############################################################################ #



import numpy as np
import scipy.spatial.distance, scipy.linalg
import pandas as pd




def partition(X, c, m=2.0, V_init=None, eps=1e-8, eps2=1e-12,
        maxiter=1000, use_FCM=False, V_prev_history_size=10, verbose=False):
    """
    Implements both the Bounded Fuzzy Possibilistic Method
    (use_FCM=False, the default)
    as well as the Fuzzy c-means method (use_FCM=True).


    References
    ----------

    H. Yazdani, Bounded fuzzy possibilistic method,
    Fuzzy Sets and Systems 389 (2020) 51-65. doi:10.1016/j.fss.2019.07.011

    J. Bezdek, R. Ehrlich, W. Full, FCM: The fuzzy c-means clustering algorithm,
    Computers & Geosciences 10 (1984) 191-203. doi:10.1016/0098-3004(84)90020-7


    Details
    -------

    By default, the method starts from a pseudo-random initial guess.
    However, a user may provide a set of initial cluster centres (V_init).

    The algorithms' convergence criteria are controlled with
    the eps and maxiter parameters.

    The division by zero error mentioned in this letter is avoided
    by assuming 0/1=1. Moreover, we are checking here whether a current
    intermediate V is amongst the V_prev_history_size previous ones.


    Parameters
    ----------

    X: numpy.ndarray
        a real matrix of size n*d, where n is the number of inputs

    c: int
        number of clusters to find

    m: defaults to 2.0
        exponent in the objective function

    V_init: defaults to None
        initial cluster centroids; matrix of size c*d;
        None for a random initialisation

    eps: defaults to 1e-8
        convergence criterion

    eps2: defaults to 1e-12
        convergence criterion

    maxiter: defaults to 1000
        convergence criterion

    use_FCM: defaults to False
        True for FCM, False for BFPM

    V_prev_history_size: defaults to 10
        how many previous sets of centroids to store?
        allows for stopping the BFPM method in case it starts running in circles

    verbose: defaults to False
        whether to print diagnostic messages


    Returns
    -------

    V: numpy.ndarray
        cluster centroids; matrix of size c*d
    """
    n, d = X.shape

    def get_V(X, U, m):
        """A subroutine that computes the cluster centres
           based on Eq. (11a) in Bezdek's paper"""
        c = U.shape[0]
        d = X.shape[1]
        V = np.empty((c, d))
        for i in range(c):
            # weighted componentwise arithmetic means:
            V[i,:]  = np.sum(((U[i,:]**m).reshape(-1,1))*X, axis=0)
            V[i,:] /= np.sum(U[i,:]**m)
        return V

    if V_init is None: # the default -- random guess
        # start with a random "fuzzy" partition:
        U = np.random.rand(c, n)
        U = U/np.sum(U, axis=0).reshape(1,-1)
        V = get_V(X, U, m)
    else:
        # U will be determined in the first iteration below:
        U = np.empty((c, n))
        V = V_init


    V_prev_history = []
    for h in range(V_prev_history_size):
        # recently generated Vs - initialise randomly:
        V_prev_history.append(np.random.rand(c, d))

    it = 1
    while True:
        # D[i,j] gives the Euclidean distance between V[i,:] and X[j,:]:
        D = scipy.spatial.distance.cdist(V, X)

        for j in range(n):
            which_zero = (D[:,j] < eps2)
            if np.any(which_zero):
                # EXTRA: avoid division by 0
                U[:,j] = which_zero*np.sum(which_zero)
            else:
                for i in range(c):
                    U[i,j] = np.sum((D[i,j]/D[:,j])**(2.0/(m-1.0)))

        if use_FCM:
            U = U**(-1.0)  # Fuzzy c-means
        else:
            U = U**(1.0/m) # Yazdani's BFPM

        # The following is not true for BFPM:
        if use_FCM:
            assert np.all(U>-eps2) and np.all(U<1+eps2)
            assert np.all(np.abs(np.sum(U, axis=0)-1.0)<eps2)

        V = get_V(X, U, m)

        for h in range(V_prev_history_size):
            if np.max(np.sum((V_prev_history[h]-V)**2.0, axis=1)) <= eps:
                if h == 0:
                    return V # the end (normal convergence)
                else:
                    if verbose:
                        print("--- cycle in V updates!")
                        for g in range(h, -1, -1):
                            print("--- V in iteration %d:"% (it-g-1))
                            print(np.round(V_prev_history[g], 4))
                        print("--- V in iteration %d (current):"%it)
                        print(np.round(V, 4))
                    return V # the end

        it += 1
        if it == maxiter:
            if verbose:
                print("--- failed to converge in %d iterations"%maxiter)
            return V # the end

        # add current V to history, forget the oldest V:
        V_prev_history = [V]+V_prev_history[:-1]
