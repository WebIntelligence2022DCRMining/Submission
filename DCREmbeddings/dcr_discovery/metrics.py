"""This file contains modules to compute the metrics for a rule."""

import math


####### FUNCTIONS FOR VITAMIN - FUNCTIONAL PROPERTIES

def get_categorical_values_vitamin(pairs_similar_instances,X,PATH_TREATMENT,PATH_DIET,PATH_IDEAL_DIET,t0,t1):
    """
    For a categorical rule and associated treatment, returns distribution of its associated pairs.
    """
    T_O,T_not_O,same_0 = 0,0,0

    for pair_ in pairs_similar_instances:
        try: # we already know that one instance has t0 and the other has t1
            ti0,oi0 = get_treatment_and_outcome_vitamin(X,pair_[0],PATH_TREATMENT,PATH_DIET,PATH_IDEAL_DIET)
            ti1,oi1 = get_treatment_and_outcome_vitamin(X,pair_[1],PATH_TREATMENT,PATH_DIET,PATH_IDEAL_DIET)

            if ti0 == t0 and ti1 == t1:
                if oi0 > oi1:
                    T_O += 1
                elif oi0 < oi1:
                    T_not_O += 1    
                else:
                    same_0 += 1
            elif ti0 == t1 and ti1 == t0:
                if oi0 < oi1:
                    T_O += 1
                elif oi0 > oi1:
                    T_not_O += 1
                else:
                    same_0 += 1
                
            else:    
                print('There is an error in the treatments values of the instances.')
        except:
            pass
    return T_O,T_not_O,same_0



def compute_metric_vitamin(pairs_similar_instances,X,PATH_TREATMENT,PATH_DIET,PATH_IDEAL_DIET,t0,t1,stat_param=1.96):
    """
    Computation of the metric.
    """
    T_O,T_not_O,same_0 = get_categorical_values_vitamin(pairs_similar_instances,X,PATH_TREATMENT,PATH_DIET,PATH_IDEAL_DIET,t0,t1)
    if T_O > 0 and T_not_O > 0:
        causal_metric = T_O/T_not_O
        log_s = math.log(causal_metric)
        interval_amp = stat_param*math.sqrt((1/T_O)+(1/T_not_O))
        return round(causal_metric,3), [round(math.exp(log_s - interval_amp),3),round(math.exp(log_s + interval_amp),3)],T_O,T_not_O,same_0
    else:
        return 0, [0,0],T_O,T_not_O,same_0
    

def get_treatment_and_outcome_vitamin(X,instance,PATH_TREATMENT,PATH_DIET,PATH_IDEAL_DIET):
    """
    Returns the value on the treatment and outcomes paths for an instance.
    
    This function iterates for each path through all properties until obtaining the values.
    """
    subject_treatment = instance
    for property_treatment in PATH_TREATMENT:
        subject_treatment = [x[2] for x in X if x[0]==subject_treatment and x[1]==property_treatment][0]
        
    subject_outcome_diet = instance
    for property_treatment in PATH_DIET:
        subject_outcome_diet = [x[2] for x in X if x[0]==subject_outcome_diet and x[1]==property_treatment][0]
        
    subject_outcome_ideal_diet = instance
    for property_treatment in PATH_IDEAL_DIET:
        subject_outcome_ideal_diet = [x[2] for x in X if x[0]==subject_outcome_ideal_diet and x[1]==property_treatment][0]
        
    return subject_treatment, int(subject_outcome_diet)-int(subject_outcome_ideal_diet)
    

####### FUNCTIONS FOR VITAMIN - NOT FUNCTIONAL PROPERTIES

def compute_metric_vitamin_not_functional(pairs_similar_instances,list_instances_t,X,PATH_DIET,PATH_IDEAL_DIET,stat_param=1.96):
    """
    Computation of the metric for not functional properties.
    """
    T_O,T_not_O,same_0 = get_categorical_values_vitamin_not_functional(pairs_similar_instances,list_instances_t,X,PATH_DIET,PATH_IDEAL_DIET)
    if T_O > 0 and T_not_O > 0:
        causal_metric = T_O/T_not_O
        log_s = math.log(causal_metric)
        interval_amp = stat_param*math.sqrt((1/T_O)+(1/T_not_O))
        return round(causal_metric,3), [round(math.exp(log_s - interval_amp),3),round(math.exp(log_s + interval_amp),3)],T_O,T_not_O,same_0
    else:
        return 0, [0,0],T_O,T_not_O,same_0


def get_categorical_values_vitamin_not_functional(pairs_similar_instances,list_instances_t,X,PATH_DIET,PATH_IDEAL_DIET):
    """
    For a categorical rule and associated treatment, returns distribution of its associated pairs.
    """
    T_O,T_not_O,same_0 = 0,0,0

    for pair_ in pairs_similar_instances:
        try: # we already know that one instance has t0 and the other has t1
            oi0 = get_outcome_vitamin_not_functional(X,pair_[0],PATH_DIET,PATH_IDEAL_DIET)
            oi1 = get_outcome_vitamin_not_functional(X,pair_[1],PATH_DIET,PATH_IDEAL_DIET)

            if pair_[0] in list_instances_t and pair_[1] not in list_instances_t:
                if oi0 > oi1:
                    T_O += 1
                elif oi0 < oi1:
                    T_not_O += 1    
                else:
                    same_0 += 1
                    
            elif pair_[1] in list_instances_t and pair_[0] not in list_instances_t:
                if oi0 < oi1:
                    T_O += 1
                elif oi0 > oi1:
                    T_not_O += 1
                else:
                    same_0 += 1
                
            else:    
                print('There is an error in the treatments values of the instances.')
        except:
            pass
    return T_O,T_not_O,same_0
    
    
def get_outcome_vitamin_not_functional(X,instance,PATH_DIET,PATH_IDEAL_DIET):
    """
    Returns the value on the treatment and outcomes paths for an instance.
    
    This function iterates for each path through all properties until obtaining the values.
    """
        
    subject_outcome_diet = instance
    for property_treatment in PATH_DIET:
        subject_outcome_diet = [x[2] for x in X if x[0]==subject_outcome_diet and x[1]==property_treatment][0]
        
    subject_outcome_ideal_diet = instance
    for property_treatment in PATH_IDEAL_DIET:
        subject_outcome_ideal_diet = [x[2] for x in X if x[0]==subject_outcome_ideal_diet and x[1]==property_treatment][0]
        
    return int(subject_outcome_diet)-int(subject_outcome_ideal_diet)


####### FUNCTIONS FOR DBPEDIA 

def get_outcome_dbpedia(X,instance,PATH_OUTCOME):
    birthDate = int([x[2] for x in X if x[0]==instance and x[1]==PATH_OUTCOME[0][0]][0])
    all_books = [x[2] for x in X if x[0]==instance and x[1]==PATH_OUTCOME[1][0]]
    year_published = []
    for book in all_books:
        year_published.append(int([x[2] for x in X if x[0]==book and x[1]==PATH_OUTCOME[1][1]][0]))
    
    return min(year_published)-birthDate


def compute_metric_dbpedia_categorial(pairs_similar_instances,list_instances_t,X,PATH_OUTCOME,stat_param=1.96):
    """
    Computation of the metric.
    """
    T_O,T_not_O,same_0 = get_categorical_values_dbpedia(pairs_similar_instances,list_instances_t,X,PATH_OUTCOME)
    if T_O > 0 and T_not_O > 0:
        causal_metric = T_O/T_not_O
        log_s = math.log(causal_metric)
        interval_amp = stat_param*math.sqrt((1/T_O)+(1/T_not_O))
        return round(causal_metric,3), [round(math.exp(log_s - interval_amp),3),round(math.exp(log_s + interval_amp),3)],T_O,T_not_O,same_0
    else:
        return 0, [0,0],T_O,T_not_O,same_0
    
    
def get_categorical_values_dbpedia(pairs_similar_instances,list_instances_t,X,PATH_OUTCOME):
    """
    For a categorical rule and associated treatment, returns distribution of its associated pairs.
    """
    T_O,T_not_O,same_0 = 0,0,0

    for pair_ in pairs_similar_instances:
        try: # we already know that one instance has t0 and the other has t1
            oi0 = get_outcome_dbpedia(X,pair_[0],PATH_OUTCOME)
            oi1 = get_outcome_dbpedia(X,pair_[1],PATH_OUTCOME)

            if pair_[0] in list_instances_t and pair_[1] not in list_instances_t:
                if oi0 < oi1:
                    T_O += 1
                elif oi0 > oi1:
                    T_not_O += 1    
                else:
                    same_0 += 1
                    
            elif pair_[1] in list_instances_t and pair_[0] not in list_instances_t:
                if oi0 > oi1:
                    T_O += 1
                elif oi0 < oi1:
                    T_not_O += 1
                else:
                    same_0 += 1
                
            else:    
                print('There is an error in the treatments values of the instances.')
        except:
            pass
    return T_O,T_not_O,same_0


def get_numerical_treatment_dbpedia(X,instance,path_treatment):
    if path_treatment == ['http://dbpedia.org/ontology/birthDate']:
        return int([x[2] for x in X if x[0]==instance and x[1]==path_treatment[0]][0])
    elif path_treatment == ['http://dbpedia.org/ontology/arwuW']:
        uni = [x for x in X if x[1]=='http://dbpedia.org/ontology/hasForStudent' and x[2]==instance][0]
        return int([x[2] for x in X if x[0]==uni and x[1]=='http://dbpedia.org/ontology/arwuW'][0])


def compute_metric_dbpedia_numerical(pairs_similar_instances,list_instances_t,X,path_treatment,PATH_OUTCOME,stat_param=1.96):
    """
    Computation of the metric.
    """
    T_O,T_not_O,same_0 = get_numerical_values_dbpedia(pairs_similar_instances,list_instances_t,X,path_treatment,PATH_OUTCOME)
    if T_O > 0 and T_not_O > 0:
        causal_metric = T_O/T_not_O
        log_s = math.log(causal_metric)
        interval_amp = stat_param*math.sqrt((1/T_O)+(1/T_not_O))
        return round(causal_metric,3), [round(math.exp(log_s - interval_amp),3),round(math.exp(log_s + interval_amp),3)],T_O,T_not_O,same_0
    else:
        return 0, [0,0],T_O,T_not_O,same_0
    
    
def get_numerical_values_dbpedia(pairs_similar_instances,X,path_treatment,PATH_OUTCOME):
    """
    For a numerical treatment, returns distribution of the mined similar pairs.
    """
    T_O,T_not_O,same_0 = 0,0,0

    for pair_ in pairs_similar_instances:
        try: # we already know that one instance has t0 and the other has t1
            oi0 = get_outcome_dbpedia(X,pair_[0],PATH_OUTCOME)
            oi1 = get_outcome_dbpedia(X,pair_[1],PATH_OUTCOME)
            
            ti0 = get_numerical_treatment_dbpedia(X,pair_[0],path_treatment)
            ti1 = get_numerical_treatment_dbpedia(X,pair_[1],path_treatment)
            
            if ti0 > ti1:
                if oi0 < oi1:
                    T_O += 1
                elif oi0 > oi1:
                    T_not_O += 1
                else:
                    same_0 += 1
                    
            elif ti0 < ti1:
                if oi0 > oi1:
                    T_O += 1
                elif oi0 < oi1:
                    T_not_O += 1
                else:
                    same_0 += 1
                    
        except:
            pass
    return T_O,T_not_O,same_0