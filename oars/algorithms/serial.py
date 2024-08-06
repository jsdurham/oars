import numpy as np
from oars.algorithms.helpers import ConvergenceChecker, getWarmPrimal
from time import time

def serialAlgorithm(n, data, resolvents, W, Z, warmstartprimal=None, warmstartdual=None, itrs=1001, gamma=0.9, alpha=1.0, vartol=None, objtol=None, objective=None, checkperiod=10, verbose=False):
    """
    Run the serial algorithm
    Args:
        n (int): the number of resolvents
        data (list): list containing the problem data for each resolvent
        resolvents (list): list of :math:`n` resolvent classes
        W (ndarray): size (n, n) ndarray for the :math:`W` matrix
        Z (ndarray): size (n, n) ndarray for the :math:`Z` matrix
        warmstartprimal (ndarray, optional): resolvent.shape ndarray for :math:`x` in v^0
        warmstartdual (list, optional): is a list of n ndarrays for :math:`u` which sums to 0 in v^0
        itrs (int, optional): the number of iterations
        gamma (float, optional): parameter in :math:`v^{k+1} = v^k - \\gamma W x^k`
        alpha (float, optional): the resolvent step size in :math:`x^{k+1} = J_{\\alpha F^i}(y^k)`
        vartol (float, optional): is the variable tolerance
        objtol (float, optional): is the objective tolerance
        objective (function, optional): the objective function
        checkperiod (int, optional): the period to check for convergence
        verbose (bool, optional): True for verbose output

    Returns:
        x (ndarray): the solution
        results (list): list of dictionaries with the results for each resolvent
    """
    # Initialize the resolvents and variables
    all_x = []
    for i in range(n):
        resolvents[i] = resolvents[i](data[i])
        if i == 0:
            m = resolvents[0].shape
        x = np.zeros(m)
        all_x.append(x)
    if warmstartprimal is not None:
        all_v = getWarmPrimal(warmstartprimal, L)
        if verbose:print('warmstartprimal', all_v)
    else:
        all_v = [np.zeros(m) for _ in range(n)]
    if warmstartdual is not None:
        all_v = [all_v[i] + warmstartdual[i] for i in range(n)]
        if verbose:print('warmstart final', all_v)

    # Run the algorithm
    if verbose:
        print('Starting Serial Algorithm')
        diffs = [ 0 ]*n
        start_time = time()
    convergence = ConvergenceChecker(vartol, objtol, counter=n, objective=objective, data=data, x=all_x) 
    verbose_itr = 1
    counter = checkperiod
    xresults = []
    vresults = []
    wx = [np.zeros(m) for _ in range(n)]
    for itr in range(itrs):
        if verbose and itr % verbose_itr == 0:
            print(f'Iteration {itr+1}')

        for i in range(n):
            resolvent = resolvents[i]
            y = all_v[i] - sum(Z[i,j]*all_x[j] for j in range(i))
            x = resolvent.prox(y, alpha)
            if verbose: 
                diffs[i] = np.linalg.norm(x - all_x[i])
                print("B/t iteration difference norm for", i, ":", diffs[i])
            all_x[i] = x #resolvent.prox(y, alpha)

        for i in range(n):     
            wx[i] = sum(W[i,j]*all_x[j] for j in range(n))       
            all_v[i] = all_v[i] - gamma*wx[i]
            if verbose:
                print("Change in w", i, ":", np.linalg.norm(gamma*wx[i]))
        if verbose and itr % verbose_itr == 0:
            for i in range(n):    
                print("Difference across x", i, i-1, np.linalg.norm(all_x[i]-all_x[i-1]))
            for i in range(n):
                print('x', i, all_x[i])
                print('v', i, all_v[i])
            xresults.append(all_x.copy())
            vresults.append(all_v.copy())
        if convergence.check(all_x, verbose=verbose):
            print('Converged in objective value, iteration', itr+1)
            break
        
    if verbose:
        print('Serial Algorithm Loop Time:', time()-start_time)
    x = sum(all_x)/n
    
    # Build results list
    results = []
    for i in range(n):
        if hasattr(resolvents[i], 'log'):
            results.append({'x':all_x[i], 'v':all_v[i], 'log':resolvents[i].log})
        else:
            results.append({'x':all_x[i], 'v':all_v[i]})
    if verbose:
        print('results', 'x', all_x, 'v', all_v)
        results.append({'xresults':xresults, 'vresults':vresults})
    return x, results


