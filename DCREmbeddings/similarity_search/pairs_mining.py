"""This file contains modules to draw pairs of similar instances."""

from ampligraph.discovery import find_nearest_neighbours
import pandas as pd
import numpy as np
import copy
from scipy.spatial import distance


def get_matrix_similarity_pairs(model,instances_tc,mode='mixed',instances_t0='instances_t0',instances_t1='instances_t1'):
    """
    Getting the euclidean distance between pairs of studied instances of a target class.
    The instances of a pair can differ on the treatment (mode=treatment_sort), or created independently of their treatment values. (mode=mixed)
    
    Parameters :
    model : ampligraph EmbeddingModel 
    all_people : list of instances studied
    mode : str
    instances_t0 : list of instances
    instances_t1 : list of instances

    Returns :
    df : pandas dataframe
        With euclidean distance between all pairs of instances
    df_to_numpy : numpy array
        array version of the df
    """
    if mode == 'mixed':
        df = pd.DataFrame(columns=instances_tc,index=instances_tc)
        for t_ in instances_tc:
            neighbors, dist = find_nearest_neighbours(model,
                                                entities=[t_],
                                                n_neighbors=len(instances_tc)-1,
                                                entities_subset=instances_tc)
            for i in range(len(neighbors[0])):
                df.loc[neighbors[0][i],t_] = round(dist[0][i],3)

        df = df.fillna(100)
        df_to_numpy = df.to_numpy()
        np.fill_diagonal(df_to_numpy, 100)
        return df,df_to_numpy
    
    elif mode == 'treatment_sort':
        df_ = pd.DataFrame(columns=instances_t0,index=instances_t1)
        for t_ in instances_t0:
            neighbors, dist = find_nearest_neighbours(model,
                                                entities=[t_],
                                                n_neighbors=len(instances_t1)-1,
                                                entities_subset=instances_t1)
            for i in range(len(neighbors[0])):
                df_.loc[neighbors[0][i],t_] = round(dist[0][i],3)

        df_ = df_.fillna(200)
        df_to_numpy = df_.to_numpy()
        return df_,df_to_numpy


def get_pairs_from_matrix_and_threshold(df,distance_threshold,strategy='greedy',mode='mixed'):
    """
    Returns the similar pairs of a target class given a threshold.
    
    Parameters :
    df : pandas dataframe
        With euclidean distance between all pairs of instances 
    distance_threshold : float
        Threshold on the distance for selecting similar instances
    strategy : string (by default = 'greedy')
        Strategy to obtain the pairs. Can be greedy or optimal

    Returns :
    pairs_similar_instances : list
        All pairs of similar instances 
    """
    df__ = copy.deepcopy(df)
    df_to_numpy = df__.to_numpy()
    min_value = df_to_numpy.min()
    pairs_similar_instances = []
    
    if strategy == 'greedy':
        if min_value >= distance_threshold:
            return pairs_similar_instances
        else:
            while min_value < distance_threshold:
                # get position
                position = np.where(df_to_numpy==min_value)

                # add to set of pairs
                first_instance = list(df.columns)[position[1][0]]
                second_instance = list(df.index)[position[0][0]]
                pairs_similar_instances.append([first_instance,second_instance])

                # replace value
                if mode=='mixed': # squared matrix - we update 2 values
                    df_to_numpy[position[0][0]] = [100]
                    df_to_numpy[:,position[1][0]] = [100]
                elif mode == 'treatment_sort': # only one value to update
                    df_to_numpy[position[0][0]] = [100]

                #update min
                min_value = df_to_numpy.min()

            return pairs_similar_instances            

    elif strategy == 'optimal':
        return pairs_similar_instances

    else:
        print("This stratedy does not exist, please switch to greedy or optimal.")
        return None


def get_pairs_from_matrix_and_proportion(df,number_total_instances,proportion=0.05,mode='mixed'):
    """
    Returns the closer pairs of a target class given a proportion of pairs to create.
    
    Parameters :
    df : pandas dataframe
        With euclidean distance between all pairs of instances 
    proportion : float
        Proportion of pairs to create

    Returns :
    pairs_closer_instances : list
        The closer pairs of instances given the proportion
    """
    df__ = copy.deepcopy(df)
    df_to_numpy = df__.to_numpy()
    pairs_closer_instances = []
    
    number_possible_pairs = min(df.shape[0],df.shape[1])
    number_pairs_total = number_total_instances*(number_total_instances-1)/2
    number_to_reach = number_pairs_total*proportion
    
    if number_possible_pairs < number_to_reach:
        number_to_reach = number_possible_pairs
        
    print('Number of pairs to build : ',number_to_reach)

    while len(pairs_closer_instances) < number_to_reach:
        # get position
        min_value = df_to_numpy.min()
        max_value = df_to_numpy.max()
        position = np.where(df_to_numpy==min_value)

        # add to set of pairs
        first_instance = list(df.columns)[position[1][0]]
        second_instance = list(df.index)[position[0][0]]
        pairs_closer_instances.append([first_instance,second_instance])

        # replace value
        if mode=='mixed': # squared matrix - we update 2 values
            df_to_numpy[position[0][0]] = [max_value]
            df_to_numpy[:,position[1][0]] = [max_value]
        elif mode == 'treatment_sort': # only one value to update
            df_to_numpy[position[0][0]] = [max_value]
            
    return pairs_closer_instances


def get_distance_for_degree(dic_distance_per_d,degree):
    if degree in list(dic_distance_per_d.keys()):
        all_values_degree = dic_distance_per_d[degree]
        return np.mean(all_values_degree)
    else:
        print('Degree can not be found')
        return None


def get_distance_for_pair(pair_,model,type_distance='euclidian'):
    """
    Returns the distance between the embedding vectors of a pair.

    The type of the distance can be specified in : euclidian, TO_COMPLETE
    """
    array_pair = np.array(pair_)
    embedding_pair = model.get_embeddings(entities=np.array(array_pair))
    if type_distance=='euclidian':
        return distance.euclidean(embedding_pair[0],embedding_pair[1])
    else:
        return None