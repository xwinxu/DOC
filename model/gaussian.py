'''
Question 1 Skeleton Code

Here you should implement and evaluate the Conditional Gaussian classifier.
'''

import numpy as np
# Import pyplot - plt.imshow is useful!
# import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.stats import multivariate_normal


def compute_mean_mles(train_data, train_labels):
    '''
    Compute the mean estimate for each digit class

    Should return a numpy array of size (10,64)
    The ith row will correspond to the mean estimate for digit class i
    '''

    means = np.zeros((train_labels.shape[1], train_data.shape[1]))
    reformatted = np.argmax(train_labels, axis=1)

    for i in range(train_data.shape[0]):
        means[int(reformatted[i])] += train_data[i]

    for k in range(train_labels.shape[1]):
        means[k] /= np.sum(reformatted == k)

    # Compute means
    return means

def compute_sigma_mles(train_data, train_labels):
    '''
    Compute the covariance estimate for each digit class

    Should return a three dimensional numpy array of shape (10, 64, 64)
    consisting of a covariance matrix for each digit class
    '''
    covariances = np.zeros((train_labels.shape[1], train_data.shape[1], train_data.shape[1]))

    means = compute_mean_mles(train_data, train_labels)
    reformatted = np.argmax(train_labels, axis=1)

    for i in range(train_data.shape[0]):
        mu = means[int(reformatted[i])]
        covariances[int(reformatted[i])] += np.matrix(train_data[i] - mu).transpose() * np.matrix(train_data[i] - mu)

    for k in range(10):
        covariances[k] /= np.sum(reformatted == k)

    epsilon = 0.01 * np.eye(train_data.shape[1])

    for k in range(10):
        covariances[k] += epsilon

    # Compute covariances
    return covariances

def generative_likelihood(digits, means, covariances):
    '''
    Compute the generative log-likelihood:
        log p(x|y,mu,Sigma)

    Should return an n x 10 numpy array
    '''

    likelihoods = np.zeros([digits.shape[0], means.shape[0]])

    print("Computing generative likelihood")

    for n in tqdm(range(digits.shape[0])):
        for k in range(means.shape[0]):
            val = (-digits.shape[-1] / 2) * np.log(2 * np.pi)
            val += np.log((np.linalg.det(covariances[k] + 0.1*np.eye(300))) ** -0.5)
            normalized = np.matrix(digits[n] - means[k])
            likelihoods[n][k] = val + -0.5 * normalized * np.linalg.inv(covariances[k]) * normalized.transpose()

    return likelihoods

def conditional_likelihood(digits, means, covariances):
    '''
    Compute the conditional likelihood:

        log p(y|x, mu, Sigma)

    This should be a numpy array of shape (n, 10)
    Where n is the number of datapoints and 10 corresponds to each digit class
    '''

    generative = generative_likelihood(digits, means, covariances)

    cond_likelihood = np.zeros([digits.shape[0], means.shape[0]])

    print("Generating conditional likelihood")

    for n in tqdm(range(digits.shape[0])):
        for k in range(means.shape[0]):
            cond_likelihood[n][k] = generative[n][k] - np.log(np.sum(np.exp(generative[n])))

    return cond_likelihood

def avg_conditional_likelihood(digits, labels, means, covariances):
    '''
    Compute the average conditional likelihood over the true class labels

        AVG( log p(y_i|x_i, mu, Sigma) )

    i.e. the average log likelihood that the model assigns to the correct class label
    '''
    cond_likelihood = conditional_likelihood(digits, means, covariances)

    print("Computing the average conditional likelihood")

    summation = 0

    for n in range(digits.shape[0]):
        summation += cond_likelihood[n][int(labels[n])]
    # Compute as described above and return

    return summation / digits.shape[0]

def classify_data(digits, means, covariances):
    '''
    Classify new points by taking the most likely posterior class
    '''

    for d in range(digits.shape[0]):
        for k in range(means.shape[0]):
            y = multivariate_normal.pdf(digits, means[k], covariances[k])
            print(y)
            input()

    pred = np.argmax(cond_likelihood, axis=1)
    return pred

def calculate_accuracy(pred, labels):
    return sum(pred == labels) / pred.shape[0]

def plot_eigenvectors(covariances):
    # fig=plt.figure(figsize=(10, 5))
    #
    # for k in range(covariances.shape[0]):
    #     w, v = np.linalg.eig(covariances[k])
    #     index = np.argmax(w)
    #     vector = v[:, index].reshape([8,8])
    #     plot = fig.add_subplot(2, 5, k+1)
    #     plot.set_title("Class {}".format(k))
    #     plt.imshow(vector, cmap='gray', interpolation="nearest")
    # plt.show()
    pass

def main():
    # train_data, train_labels, test_data, test_labels = data.load_all_data('data')
    #
    # # Fit the model
    # means = compute_mean_mles(train_data, train_labels)
    # covariances = compute_sigma_mles(train_data, train_labels)
    #
    # # Evaluation
    # # First compute the average conditional log likelihood
    # train_avg = avg_conditional_likelihood(train_data, train_labels, means, covariances)
    # print("Average conditional log likelihood on train data: {}".format(train_avg))
    #
    # test_avg = avg_conditional_likelihood(test_data, test_labels, means, covariances)
    # print("Average conditional log likelihood on test data: {}".format(test_avg))
    #
    # # Now we calculate the accuracy of our predictions
    # train_accuracy = calculate_accuracy(classify_data(train_data, means, covariances), train_labels)
    # print("Average accuracy on train data: {}".format(train_accuracy))
    #
    # test_accuracy = calculate_accuracy(classify_data(test_data, means, covariances), test_labels)
    # print("Average accuracy on test data: {}".format(test_accuracy))
    #
    # # Finally, plot the most significant eigenvectors of the covariance matrices
    # plot_eigenvectors(covariances)
    pass

if __name__ == '__main__':
    main()
