import numpy as np
import matplotlib.pyplot as plt
import scipy
import random
from sklearn.metrics import confusion_matrix
from h1_util import numerical_grad_check

def logistic(z):
    """ 
    Computes the logistic function 1/(1+e^{-x}) to each entry in input vector z.
    
    np.exp may come in handy
    Args:
        z: numpy array shape (d,) 
    Returns:
       logi: numpy array shape (d,) each entry transformed by the logistic function 
    """
    logi = np.zeros(z.shape)
    ### YOUR CODE HERE
    logi = np.array([1/(1+np.exp(-x)) for x in z])  # .reshape(z.shape) <-- no need to reshape
    ### END CODE
    assert logi.shape == z.shape
    return logi

def log_cost(X, y, w, reg=0):
    """
    Compute the (regularized) cross entropy and the gradient under the logistic regression model
    using data X, targets y, weight vector w (and regularization reg)
    
    The L2 regularization is 1/2 reg*|w_{1,d}|^2 i.e. w[0], the bias, is not regularized
    
    np.log, np.sum, np.choose, np.dot may be useful here
    Args:
        X: np.array shape (n,d) float - Features
        y: np.array shape (n,)  int - Labels 
        w: np.array shape (d,)  float - Initial parameter vector
        reg: scalar - regularization parameter

    Returns:
      cost: scalar the cross entropy cost of logistic regression with data X,y using regularization parameter reg
      grad: np.arrray shape(n,d) gradient of cost at w with regularization value reg
    """
    cost = 0
    grad = np.zeros(w.shape)
    ### YOUR CODE HERE
    n = X.shape[0]
    d = X.shape[1]

    cost = -(y.dot(np.log(logistic(w.dot(X.T)))) + (1 - y).dot(np.log((1-logistic(w.dot(X.T))))))/n
    cost += 1/2*reg*sum([np.linalg.norm(w[i])**2 for i in range(1,d)])
    
    grad = -X.T.dot((y-logistic(X.dot(w))))/n
    grad[1:d]+=reg*w[1:d]
    ### END CODE
    assert grad.shape == w.shape
    return cost, grad

def batch_grad_descent(X, y, w=None, reg=0, lr=1.0, rounds=10):
    """
    Run Gradient Descent for logistic regression using all the data to compute gradient in each step
            
    Args:
        X: np.array shape (n,d) dtype float32 - Features 
        y: np.array shape (n,) dtype int32 - Labels 
        w: np.array shape (d,) dtype float32 - Initial parameter vector
        lr: scalar - learning rate for gradient descent
        reg: scalar regularization parameter (optional)    
        rounds: rounds to run (optional)

    Returns:
        w: numpy array shape (d,) learned weight vector w
    """

    if w is None: w = np.zeros(X.shape[1])
    #lr = 1.0
    ### YOUR CODE HERE
    for t in range(rounds):
        cost,grad = log_cost(X,y,w,reg)
        print(cost)
        w = w - lr*grad
    ### END CODE
    return w
    
def mini_batch_grad_descent(X, y, w=None, reg=0, lr=0.1, batch_size=16, epochs=10):
    """
      Run mini-batch stochastic Gradient Descent for logistic regression 
      use batch_size data points to compute gradient in each step.
    
    The function np.random.permutation may prove useful for shuffling the data before each epoch
    It is wise to print the performance of your algorithm at least after every epoch to see if progress is being made.
    Remeber the stochastic nature of the algorithm may give fluctuations in the cost as iterations increase.

    Args:
        X: np.array shape (n,d) dtype float32 - Features
        y: np.array shape (n,) dtype int32 - Labels
        w: np.array shape (d,) dtype float32 - Initial parameter vector
        lr: scalar - learning rate for gradient descent
        reg: scalar regularization parameter (optional)
        rounds: rounds to run (optional)
        batch_size: number of elements to use in minibatch
        epochs: Number of scans through the data

    Returns: 
        w: numpy array shape (d,) learned weight vector w
    """

    n = X.shape[0]
    d = X.shape[1]
    if w is None: w = np.zeros(X.shape[1])
    ### YOUR CODE
    # Pick a 'mini batch' by choosing random indicies
    batch_size=n
    m = int(n/batch_size)
    for i in range(epochs):
        minibatch_indicies = np.array(random.sample(range(n),m*batch_size)).reshape(m,batch_size)
        for j in range(m):
            X_mini_batch = X[minibatch_indicies[j]]
            y_mini_batch = y[minibatch_indicies[j]]
            # Get gradient and update weights
            cost,grad_mini_batch = log_cost(X_mini_batch,y_mini_batch,w,reg)
            print(cost)
            w = w - lr*grad_mini_batch

    ### END CODE
    return w

def fast_descent(X, y, w=None, reg=0, rounds=100):
    """ Uses fancy optimizer to do the gradient descent """
    # unstable if linear separable...
    if w is None: w = np.zeros(X.shape[1])
    w =  scipy.optimize.minimize(lambda t: log_cost(X,y,t,reg), w, jac=True, options={'maxiter':rounds, 'disp':True})
    return w.x

def test_logistic():
    print('*'*5, 'Testing logistic function')
    a = np.array([0,1,2,3])
    lg = logistic(a)
    target = np.array([ 0.5, 0.73105858, 0.88079708, 0.95257413])
    assert np.allclose(lg, target), 'Logistic Mismatch Expected {0} - Got {1}'.format(target, lg)
    print('Test Success!')

def test_cost():
    print('*'*5, 'Testing Cost Function')
    X = np.array([[1.0, 0.0], [1.0, 1.0]])
    y = np.array([0, 0], dtype='int64')
    w = np.array([0.0, 0.0])
    reg = 0
    cost,_ = log_cost(X,y, w)
    target = -np.log(0.5)
    
    assert np.allclose(cost, target), 'Cost Function Error:  Expected {0} - Got {1}'.format(target, cost)
    print('Test Success')

def test_reg_cost():
    print('*'*5, 'Testing Regularized Cost Function')
    X = np.array([[1.0, -1.0], [-1.0, 1.0]])
    y = np.array([0, 0], dtype='int64')
    w = np.array([1.0, 1.0])
    reg = 1.0
    cost,_ = log_cost(X, y, w, reg=reg)
    target = -np.log(0.5) + 0.5
    assert np.allclose(cost, target), 'Cost Function Error:  Expected {0} - Got {1}'.format(target, cost)
    print('Test Success')

def test_grad():
    print('*'*5, 'Testing  Gradient')
    X = np.array([[1.0, 0.0], [1.0, 1.0]])
    w = np.array([0.0, 0.0])
    y = np.array([0, 0]).astype('int64')
    reg = 0
    f = lambda z: log_cost(X, y, w=z, reg=reg)
    numerical_grad_check(f, w)
    print('Test Success')

def test_mini_batch():
    print('*'*5, 'Testing Mini batch')
    X = np.random.rand(100,10)
    w = np.zeros(10,)
    y = np.zeros(100,).astype('int64')
    reg = 0
    # f = lambda z: log_cost(X, y, w=z, reg=reg)
    # numerical_grad_check(f, w)
    print(log_cost(X, y, w)[0])
    w = mini_batch_grad_descent(X, y, w,batch_size=1)
    print(log_cost(X, y, w)[0])    
    print('Test Success')    

def test_reg_grad():
    print('*'*5, 'Testing  Gradient')
    X = np.array([[1.0, 0.0], [1.0, 1.0]])
    w = np.array([0.0, 0.0])
    y = np.array([0, 0]).astype('int64')
    reg = 1.0
    f = lambda z: log_cost(X, y, w=z, reg=reg)
    numerical_grad_check(f, w)
    print('Test Success')
    
if __name__ == '__main__':
    test_logistic()
    test_cost()
    test_grad()
    test_reg_cost()
    test_reg_grad()
    
    
