"""This file contains modules to compute the similarity threshold with a model."""

import matplotlib.pyplot as plt
import numpy as np


def plot_distribution_measures(measures,KGE_model_name):
    """
    Plots the distribution of the measures.
    
        
    Parameters:
        measures : list of 2-elements lists [distance,similarity]
        model_name : str
        
    Returns:
        Plots the distribution.
    """
    list_distance = [measure[0] for measure in measures]
    list_similarity = [measure[1] for measure in measures]

    plt.figure(figsize=(7, 5), dpi=80)

    x = list_distance
    y = list_similarity
    plt.ylim(0, 1)
    plt.scatter(x, y, c = 'red')
    title_ = 'Embedding Distance (X) - Similarity Measure (Y) For Model : ' + KGE_model_name + ' n : ' + str(len(list_distance))
    plt.title(title_)


def fit_model_on_measures(measures,model_degree):
    """
    Returns a fitted model on the measures and its r-squared score.
    """
    x = [measure[0] for measure in measures]
    y = [measure[1] for measure in measures]
    model = np.poly1d(np.polyfit(x, y, model_degree))

    coeffs = np.polyfit(x, y, model_degree)
    p = np.poly1d(coeffs)
    yhat = p(x)
    ybar = np.sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)
    sstot = np.sum((y - ybar)**2)
    r_squared = ssreg / sstot

    return model, r_squared


def plot_distribution_and_model(measures,fitted_model):
    """
    Plots the distribution of the measures.
    
        
    Parameters:
        measures : list of 2-elements lists [distance,similarity]
        fitted_model : numpy.poly1d
        
    Returns:
        Plots the distribution and the model.
    """
    list_distance = [measure[0] for measure in measures]
    list_similarity = [measure[1] for measure in measures]
    
    plots_X = np.linspace(min(list_distance),max(list_distance),200)
    plots_Y = [fitted_model(i) for i in plots_X]

    plt.figure(figsize=(7, 5), dpi=80)

    x = list_distance
    y = list_similarity
    plt.ylim(0, 1)
    plt.scatter(x, y, c = 'red')
    plt.scatter(plots_X, plots_Y, c = 'black',marker = '+')

    title_ = 'Distances Distribution and Associated Fitted Model'
    plt.title(title_)


def get_distance_threshold(fitted_model,SIMILARITY_THRESHOLD):
    """
    Returns the distance threshold for matching similar instances given a similarity threshold.
    Assumption : the fitted_model is descreasing with the distance ()
    
    Parameters:
        fitted_model : numpy.poly1d
        SIMILARITY_THRESHOLD : float
        
    Returns:
        Distance threshold (float)
    """
    x0 = (fitted_model - SIMILARITY_THRESHOLD).roots
    return x0.min().astype(float)
