import uuid
import random
import copy


def get_description_for_generation(X,instance_writer):
    """
    Return whole description of an instance of the writer class and associated books, university and country
    
    Parameters:
        X : KG (numpy array)
        instance_writer : URI of a writer instance
    """
    # description of the writer
    dic_writer = get_description(X,instance_writer)
    
    # description of the books
    dic_of_books = {}
    for book in dic_writer['http://dbpedia.org/ontology/author']:
        dic_of_books[book] = get_description(X,book)
        
    # description of the uni
    uni = get_university_from_writer(X,instance_writer)
    dic_uni = get_description(X,uni)
    
    # description of the country
    country = get_country_from_university(X,uni)
    dic_country = get_description(X,country)
    
    return dic_writer, dic_of_books, uni, dic_uni, country, dic_country


def get_description(X,instance):
    """Return description in dictionnary where a given instance is the subject"""
    dic_description = {}
    for triple in get_triples_where_instance_subject(X,instance):
        if triple[1] in list(dic_description.keys()):
            dic_description[triple[1]] = dic_description[triple[1]] + [triple[2]]
        else:
            dic_description[triple[1]] = [triple[2]]
    return dic_description


def get_triples_where_instance_subject(X,instance):
    """Return triples where instance is the subject"""
    return [x for x in X if x[0]==instance]


def get_university_from_writer(X,instance_writer):
    """Return university URI where a writer studied"""
    return [x[0] for x in X if x[1]=='http://dbpedia.org/ontology/hasForStudent' and x[2]==instance_writer][0]


def get_country_from_university(X,uni_instance):
    """Return country URI where a university is located"""
    return [x[0] for x in X if x[1]=='http://dbpedia.org/ontology/isCountryOf' and x[2]==uni_instance][0]


def get_paths_to_change(X,instance_writer,dic_writer,dic_of_books,uni,dic_uni,country,dic_country,number_differences,blocked_p=[]):
    """
    Given a number of differences, return dictionnary where keys are the URI to be modified and values the properties where they are to be modified.
    Parameters:
        number_differences : int
        blocked_p : list of properties that can not be modified
    """
    p_writer = [[instance_writer,i] for i in list(dic_writer.keys())]
    p_book = []
    for book,dic_book in dic_of_books.items():
        p_book += [[book,i] for i in list(dic_book.keys())]
    p_uni = [[uni,p_] for p_,value in dic_uni.items() for i in range(len(value))]
    p_country = [[country,'http://dbpedia.org/ontology/isCountryOf']]
    
    properties_to_draw_from = p_writer + p_book + p_uni + p_country
    properties_to_draw_from = [p_ for p_ in properties_to_draw_from if p_[1] not in blocked_p]
    properties_to_draw_from.remove([uni,'http://dbpedia.org/ontology/hasForStudent'])
    draw_properties = random.sample(properties_to_draw_from,number_differences)
    
    dic_paths_to_change = {p_[0]:[] for p_ in draw_properties}
    for p_ in draw_properties:
        dic_paths_to_change[p_[0]].append(p_[1])
    
    return dic_paths_to_change


def get_dic_with_type_and_nodes_modified(X,dic_paths_to_change):
    """Return type of the nodes modified"""
    dic_types_modified = {}
    for node, paths_to_change in dic_paths_to_change.items():
        type_node = get_type(X,node)
        if type_node in list(dic_types_modified.keys()):
            dic_types_modified[type_node] = dic_types_modified[type_node] + [node]
        else:
            dic_types_modified[type_node] = [node]
    return dic_types_modified


def draw_objects_from_p(X,instance_modified,p_,objects_to_avoid,number_draw):
    """Given a property, return list of objects in its range that are randomly selected and not already expressed"""
    type_instance_modified = get_type(X,instance_modified)
    instances_with_type = get_instances_for_type(X,type_instance_modified)
    objects_ = [x[2] for x in X if x[1]==p_ and x[2] not in objects_to_avoid and x[0] in instances_with_type]
    return random.sample(objects_,number_draw)


def get_new_triples_for_given_instance(X,former_instance,former_dic,dic_paths_to_change):
    """
    Return new triples for an instance to be modified given the dictionnary indicating which properties to modify
    The instance in this function should be countries, universities or books
    New triples from the target class writer are created in another function
    """
    triples_to_add = []
    # creating new instance
    properties_to_change = dic_paths_to_change[former_instance]
    p_count = {p:properties_to_change.count(p) for p in properties_to_change}
    new_dic = copy.deepcopy(former_dic)

    # obtaining the new values
    for p_to_change,number_changed in p_count.items():
        former_objects = new_dic[p_to_change]
        new_objects = random.sample(former_objects,len(former_objects)-number_changed)
        new_dic[p_to_change] = new_objects + draw_objects_from_p(X,former_instance,p_to_change,former_objects,number_changed)

    # adding the new triples
    new_URI = uuid.uuid4().urn.split('uuid:')[1]
    for p_,list_value in new_dic.items():
        for v_ in list_value:
            triples_to_add.append([new_URI,p_,v_])
    
    return new_URI,triples_to_add


def get_type(X,instance):
    """Return type of an instance"""
    types_ = [x[2] for x in X if x[0]==instance and x[1]=='http://www.w3.org/1999/02/22-rdf-syntax-ns#type']
    for t_ in types_:
        if 'dbpedia' in t_:
            return t_
        
    
def get_instances_for_type(X,type_):
    """Return list of instances of a given type"""
    return [x[0] for x in X if x[1]=='http://www.w3.org/1999/02/22-rdf-syntax-ns#type' and x[2]==type_]


def get_if_instance_exist(X,node,dic_paths_to_change):
    """
    Given an instance to be modified and its associated dictionnary with the modification to make,
    verifies if another instance verifying the modification already exists in the KG
    Return the instance if it exists    
    """
    type_node = get_type(X,node)
    description_node = get_description(X,node)
    
    valid_instances = [instance for instance in get_instances_for_type(X,type_node) if instance != node]
    p_to_share = [p_ for p_ in list(description_node.keys()) if p_ not in dic_paths_to_change[node]]
    p_differ = dic_paths_to_change[node]
    
    for p_ in p_to_share:
        if type(description_node[p_])==list:
            for value in description_node[p_]:
                instances_with_p = [x[0] for x in X if x[1]==p_ and x[2]==value]
                valid_instances = [i for i in valid_instances if i in instances_with_p]
        else:
            instances_with_p = [x[0] for x in X if x[1]==p_ and x[2]==description_node[p_]]
            valid_instances = [i for i in valid_instances if i in instances_with_p]
        
        if len(valid_instances)==0:
            return 0
        
    for p_ in p_differ:
        if type(description_node[p_])==list:
            for value in description_node[p_]:
                instances_with_p = [x[0] for x in X if x[1]==p_ and x[2]==value]
                valid_instances = [i for i in valid_instances if i not in instances_with_p]
        else:
            instances_with_p = [x[0] for x in X if x[1]==p_ and x[2]==description_node[p_]]
            valid_instances = [i for i in valid_instances if i not in instances_with_p]
        
        if len(valid_instances)==0:
            return 0
    
    return valid_instances


def get_triples_to_add(X,instance_writer,dic_paths_to_change,dic_writer,dic_of_books,uni,dic_uni,country,dic_country):
    """
    Return new URI and triples for an instance of a target class
    """
    triples_to_add = []
    new_writer_URI = uuid.uuid4().urn.split('uuid:')[1]
    
    # sorting the nodes to modify in order of interest
    dic_types_modified = get_dic_with_type_and_nodes_modified(X,dic_paths_to_change)
    
    # dealing with the university
    if 'http://dbpedia.org/ontology/University' in list(dic_types_modified.keys()):
        uni = dic_types_modified['http://dbpedia.org/ontology/University'][0]
        valid_instances = get_if_instance_exist(X,uni,dic_paths_to_change)
        if valid_instances: # we try to find if there is an existing node with these differences
            instance_selected = random.sample(valid_instances,1)
            # the instance exists : only need to create new predicate
            triples_to_add.append([instance_selected,'http://dbpedia.org/ontology/hasForStudent',new_writer_URI])
            
        else:
            new_uni_URI,triples_to_add_university = get_new_triples_for_given_instance(X,uni,dic_uni,dic_paths_to_change)
            triples_to_add.append([new_uni_URI,'http://dbpedia.org/ontology/hasForStudent',new_writer_URI])
            triples_to_add = triples_to_add + triples_to_add_university
            uni = new_uni_URI
            
    else:
        triples_to_add.append([uni,'http://dbpedia.org/ontology/hasForStudent',new_writer_URI])
    
    # dealing with the country
    if 'http://dbpedia.org/ontology/Country' in list(dic_types_modified.keys()):
        # we add the university to another country
        countries = get_instances_for_type(X,'http://dbpedia.org/ontology/Country')
        countries_to_draw_from = [c for c in countries if c != country]
        country_selected = random.sample(countries_to_draw_from,1)[0]
        triples_to_add.append([country_selected,'http://dbpedia.org/ontology/isCountryOf',uni])
    else:
        triples_to_add.append([country,'http://dbpedia.org/ontology/isCountryOf',uni])
    
    # dealing with the books
    if 'http://dbpedia.org/ontology/Book' in list(dic_types_modified.keys()):
        for book in dic_types_modified['http://dbpedia.org/ontology/Book']:
            valid_instances = get_if_instance_exist(X,book,dic_paths_to_change)
            if valid_instances:
                instance_selected = random.sample(valid_instances,1)
                # the instance exists : only need to create new predicate
                triples_to_add.append([new_URI,'http://dbpedia.org/ontology/author',instance_selected])
            else:
                dic_book = dic_of_books[book]
                new_book_URI, triples_to_add_book = get_new_triples_for_given_instance(X,book,dic_book,dic_paths_to_change)
                triples_to_add.append([new_writer_URI,'http://dbpedia.org/ontology/author',new_book_URI])
                triples_to_add = triples_to_add + triples_to_add_book
                        
    # dealing with the writer
    if 'http://dbpedia.org/ontology/Writer' in list(dic_types_modified.keys()):
        # creating new instance
        properties_to_change = dic_paths_to_change[instance_writer]
        p_count = {p:properties_to_change.count(p) for p in properties_to_change}
        new_writer_dic = copy.deepcopy(dic_writer)

        # obtaining the new values
        for p_to_change,number_changed in p_count.items():
            former_objects = new_writer_dic[p_to_change]
            new_objects = random.sample(former_objects,len(former_objects)-number_changed)
            new_writer_dic[p_to_change] = new_objects + draw_objects_from_p(X,instance_writer,p_to_change,former_objects,number_changed)

        # adding the new triples
        for p_,list_value in new_writer_dic.items():
            if p_ == 'http://dbpedia.org/ontology/author': # one must be careful about 
                for book in list_value:
                    if 'http://dbpedia.org/ontology/Book' in dic_types_modified.keys():
                        if book not in dic_types_modified['http://dbpedia.org/ontology/Book']:
                            triples_to_add.append([new_writer_URI,p_,book])
            else:
                for v_ in list_value:
                    triples_to_add.append([new_writer_URI,p_,v_])
                    
    else: # if no modification on the target class - add all original properties 
        for p_,list_value in dic_writer.items():
            if p_ == 'http://dbpedia.org/ontology/author': # only add books that are not modified - the modified are already added
                for book in list_value:
                    if 'http://dbpedia.org/ontology/Book' in dic_types_modified.keys():
                        if book not in dic_types_modified['http://dbpedia.org/ontology/Book']:
                            triples_to_add.append([new_writer_URI,p_,book])
            else:
                for v_ in list_value:
                    triples_to_add.append([new_writer_URI,p_,v_])
                    
    return new_writer_URI, triples_to_add
