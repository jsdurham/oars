import numpy as np

class traceEqualityIndicator():
    """
    Class for the trace proximal operator
    projects into the space tr(A*X) = v
    where A is a real symmetric matrix and v is a scalar
    and X is a real symmetric matrix
    """

    def __init__(self, data):
        self.A = data['A'] # The coefficient matrix
        self.v = data['v'] # The value to match
        self.U = self.scale(self.A)
        self.shape = self.A.shape

    def scale(self, A):
        """
        Scale the matrix A by the squared Frobenius norm
        """    
        return A/np.linalg.norm(A, 'fro')**2

    def prox(self, X, t=1):
        """
        Compute the proximal operator of the trace norm
        """
        ax = np.trace(self.A @ X)
        if ax == self.v:
            return X

        return X - (ax - self.v)*self.U


class traceHalfspaceIndicator():
    """
    Class for the trace proximal operator
    """

    def __init__(self, A):
        self.A = A
        self.U = self.scale(A)
        self.shape = A.shape

    def scale(self, A):
        """
        Scale the matrix A by the squared Frobenius norm
        """    
        return A/np.linalg.norm(A, 'fro')**2

    def prox(self, X, t=1):
        """
        Compute the proximal operator of the trace norm
        """
        ax = np.trace(self.A @ X)
        if ax >= 0:
            return X
        
        return X - ax*self.U

class reducedCone():
    """
    Class for the reduced cone proximal operator
    projects into the subspace of the PSD cone with 
    u in the null space of A
    """

    def __init__(self, u):
        self.u = u # The vector u
        self.U = np.outer(u, u)
        self.shape = self.U.shape

    def getEigen(self, X):
        """
        Compute the eigenvalue of A corresponding to the vector u
        """
        return self.u @ X @ self.u

    def prox(self, X, t=1):
        """
        Compute the proximal operator of the reduced cone
        """
        # Project onto the subspace
        #Y = X - self.getEigen(X)*self.U

        # Project onto the PSD cone
        # Catch exceptions for numerical stability
        try:
            eig, vec = np.linalg.eigh(X)
            eig[eig < 0] = 0
        except:
            print('Error in eigh')
            print(X)
        XX = vec @ np.diag(eig) @ vec.T

        return XX - self.getEigen(XX)*self.U

class psdCone():
    """
    Class for the PSD cone proximal operator
    """

    def __init__(self, dim):
        self.shape = dim

    def prox(self, X, t=1):
        """
        Compute the proximal operator of the PSD cone
        """
        try:
            eig, vec = np.linalg.eigh(X)
            eig[eig < 0] = 0
        except:
            print('Error in eigh')
            print(X)
        return vec @ np.diag(eig) @ vec.T

class linearSubdiff():
    """
    Class for the linear subdifferential
    """

    def __init__(self, A):
        self.A = A
        self.shape = A.shape

    def prox(self, X, t=1):
        """
        Compute the proximal operator of the linear subdifferential
        """
        return X - t*self.A

class sumOne():
    """
    Class for the sum one proximal operator
    """

    def __init__(self, dim):
        self.shape = dim
        self.n = dim[0]//2

    def prox(self, X, t=1):
        """
        Compute the proximal operator of the sum one norm
        """
        s = sum(X[i,i] for i in range(self.n))
        if s == 0:
            Y = np.zeros(self.shape)
            for i in range(self.n):
                Y[i,i] = 1/self.n
            return X + Y
        return X/s


class absprox():
    '''L1 Norm Resolvent function'''
    def __init__(self, data):
        self.data = data
        self.shape = data.shape

    # Evaluates L1 norm
    def __call__(self, x):
        u = x - self.data
        return sum(abs(u))

    # Evaluates L1 norm resolvent
    def prox(self, y, tau=1.0):
        u = y - self.data
        r = max(abs(u)-tau, 0)*np.sign(u) + self.data
        # print(f"Data: {self.data}, y: {y}, u: {u}, r: {r}", flush=True)
        return r

    def __repr__(self):
        return "L1 norm resolvent"
        

class quadprox():
    def __init__(self, data):
        self.data = data
        self.shape = data.shape
    
    def prox(self, y, tau=1.0):
        return (y+tau*self.data)/(1+tau)

