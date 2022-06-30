"""This file contains modules to estimate the distance threshold to mine similar pairs."""

from ampligraph.discovery import find_nearest_neighbours
import pandas as pd
import numpy as np
import random
import itertools

from scipy.spatial import distance


def draw_set_of_pairs(list_target_class_instances,n_sample=200):
    """
    Getting a set of randomly draw pairs of the target class. 
    
    Parameters :
    list_target_class_instances : list 
    n_sample : int

    Returns :
    list_pairs : list
        List of randomly selected pairs
    """
    all_pairs = [pair for pair in itertools.combinations(list_target_class_instances,2)]
    return random.sample(all_pairs,n_sample)


def get_measures_for_pairs(sample_pairs,model,X,dic_functionality,type_end,PATH_TYPE,type_distance='euclidian'):
    """
    Returns the the list of measures (distance and similarity) for all pairs.
    """
    measures = []
    for pair_ in sample_pairs:
        dist_ = get_distance_for_pair(pair_,model)
        sim_ = get_similarity_for_pair(pair_,model,X,dic_functionality,type_end,PATH_TYPE)
        measures.append([dist_,sim_])
    return measures


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


def get_similarity_for_pair(pair_,model,X,dic_functionality,type_end,PATH_TYPE,previous_node_weight=1):
    """
    Returns the similarity between two instances of a pair using the predictions of the learned embedding model.
    This function is called recursively on all properties that need to be assessed.
    
    Parameters:
        pair_ : list
        model : ampligraph.model
        X : numpy array
        dic_functionalty : dictionnary
        
    Returns:
        similarity_global : float
    """
    similarity_entities = 0
    entity_0 = pair_[0]
    entity_1 = pair_[1]
    
    # we first need to now what properties to go through
    properties_to_assess = get_properties_to_assess(pair_,X)
    properties_to_assess = list(dic_functionality.keys())
    
    relative_weight = previous_node_weight/len(properties_to_assess)
    
    # we go through each property
    for p_ in properties_to_assess:
        # (1) we obtain the possible objects
        objects_for_p = get_objects_of_property(p_,X)
        
        # (2) we obtain the top n triples for each instance on the property p_
        top_triples_i0 = get_n_objects_for_property_entity(entity_0,p_,objects_for_p,model,dic_functionality[p_])
        top_triples_i1 = get_n_objects_for_property_entity(entity_1,p_,objects_for_p,model,dic_functionality[p_])
        
        # (3) we compare the top triples : 2 different cases depending on the triples type
        if end_node(top_triples_i0[0],X,PATH_TYPE,type_end):
            # studying literals or URIs without properties : we study the intersection set
            intersection = list(set(top_triples_i0).intersection(top_triples_i1))
            objects_common = len(intersection)/dic_functionality[p_] # score entre 0 et 1
            similarity_property = objects_common*relative_weight # score entre 0 et poids du chemin
            similarity_entities += similarity_property
            
        else:
            # studying URIs : exploration stops if same URIs, or recursive call if different
            intersection = list(set(top_triples_i0).intersection(top_triples_i1))
            objects_common = len(intersection)/dic_functionality[p_]
            similarity_property = objects_common/relative_weight
            
            # exploring the URIs not similar : we must go through all possible combinations (which are compared of pairs)
            objects_i0 = [i for i in top_triples_i0 if i not in intersection]
            objects_i1 = [i for i in top_triples_i1 if i not in intersection]
            
            set_of_combinaisons = [list(zip(each_p, objects_i1)) for each_p in itertools.permutations(objects_i0, len(objects_i1))]
            scores_combinaisons = {}
            
            for combinaison in set_of_combinaisons:
                score_pairs = 0
                for pair_combi in combinaison:
                    similarity_pair_combi = get_similarity_for_pair(pair_combi,model,X,dic_functionality,previous_node_weight=relative_weight)
                    score_pairs += similarity_pair_combi
                scores_combinaisons[combinaison] = score_pairs
            
            scores_combi = list(scores_combinaisons.values())
            similarity_property = max(scores_combi)/relative_weight
            similarity_entities += similarity_property
            
    return similarity_entities


def get_properties_to_assess(pair_,X):
    """
    Returns all properties for an instance of a pair.
    
    TO UPDATE: 
        Current version: might not query all properties for an entity (only query the one it has in its description)
        Future version: define all properties in schema to get exhaustive properties to query 
    """
    return list(np.unique([x[1] for x in X if x[0] == pair_[0]]))


def get_objects_of_property(property_,X):
    """
    Returns possible objects for a property.
    """
    return list(np.unique([x[2] for x in X if x[1] == property_]))


def get_n_objects_for_property_entity(entity_,property_,objects_,model,func_):
    """
    Obtain the list of the top ranked objects for an entity on the property p_ given the model.
    """
    triples_ent_ = generate_array_triples(entity_,property_,objects_)
    scores_ = model.predict(triples_ent_)
    df_ = create_df_values_scores(entity_,property_,objects_,scores_)
    return list(df_['object'])[:func_]


def generate_array_triples(entity_,property_,objects_):
    """
    Generates all possible triples in the appropriate format to assess their score afterwards.
    """
    return np.array([[entity_,property_,o] for o in objects_])


def create_df_values_scores(entity_,property_,objects_,scores_):
    """
    Given the triples and the scores, returns the triples in a pandas.dataframe ranked on the score.
    """
    df_ = pd.DataFrame()
    for i in range(len(objects_)):
        dic_add = {
            'subject':entity_,
            'predicate':property_,
            'object':objects_[i],
            'score':scores_[i]
        }
        df_ = df_.append(dic_add,ignore_index=True)
    df_ = df_.sort_values(by=['score'],ascending=False)
    return df_


def end_node(entity_,X,PATH_TYPE,type_end):
    """
    Returns True if the entity is an end node (literal or URI without further properties).
    """
    if [x[2] for x in X if x[1] == PATH_TYPE][0] in type_end:
        return True
    elif len([x for x in X if x[0] == entity_]) > 0:
        return False
    else:
        return True


def get_subset_points_for_threshold(measures,number_points=20,number_step=20):
    """
    Returns a subset of points which is distributed on the distance measure.

    This is realized as no assumptions can be made on the distance distribution of the points.
    Therefore, some intervals could be overestimated.
    This ensures a reduction of the bias on the threshold estimation in next steps.

    Parameters:
        measures : list of 2-elements list
        number_points, number_step : int

    Returns:
        subset_points : list of 2-elements list

    """
    # sorting the points on the intervals
    updated_set_of_points = []
    distances = [i[0] for i in measures]
    step = (max(distances)-min(distances))/number_step
    intervals = [[min(distances)+step*(i),min(distances)+step*(i+1)] for i in range(0,number_step)]
    dic_intervals = {tuple(i):[]for i in intervals}
    for point_ in measures:
        p_distance = point_[0]
        for interval_, list_points_interval in dic_intervals.items():
            if p_distance >= interval_[0] and p_distance <= interval_[1]:
                list_points_interval.append(point_)
    
    # sampling the points per interval
    subset_points = []
    for interval, set_points in dic_intervals.items():
        if len(set_points) <= number_points:
            subset_points += set_points
        else:
            subset_points += random.sample(set_points,number_points)
            
    return subset_points