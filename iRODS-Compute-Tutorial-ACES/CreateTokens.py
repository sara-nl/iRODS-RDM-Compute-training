# @Author 
# Christine Staiger
# staiger@cwi.nl; staigerchristine@gmail.com
# July 2013

#python imports
import pprint

def generate_tokens(DataAndFeatureExtractors, nrRepeats, nrFolds, experiment):
    """
    Generate all the tokens.
    DataAndFeatureExtractors:   list of tuples, (dataset, ((method, specialParams), network), shuffleNr)
                                dataset, method, network: string
                                specialParams: float or None
                                shuffleNr: int
    nrRepeats, nrFolds:     int
    
    """
    tokens = []
    for (dataset, ((method, specific), network), shuffleNr) in DataAndFeatureExtractors:
            if specific == True or specific == False:
                pass
            elif specific != None:
                specific = "%.2f" % (specific)
            for repeat in range(nrRepeats):
                for fold in range(nrFolds):
                    token = {}
                    if shuffleNr == None:
                        identifier = "%s_%s_%s_%s_%s_%d_%d_%s" % (
                            experiment, dataset, network, method, specific, repeat, fold, shuffleNr)
                    else:
                        identifier = "%s_%s_%s_%s_%s_%d_%d_%d" % (
                            experiment, dataset, network, method, specific, repeat, fold, shuffleNr)
                    token['_id'] = identifier
                    token['input'] = {
                        'dataset': dataset,
                        'network': network,
                        'method': method,
                        'specific': specific,
                        'repeat': repeat,
                        'fold': fold,
                        'shuffleNr': shuffleNr
                    }
                            
                    tokens.append(token)
    return tokens
