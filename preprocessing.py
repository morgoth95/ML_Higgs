import numpy as np

def nan_converter(x,nm=-999,direction=True):
    """
    Convert the non-measured elements of the matrix in nan.
    If direction=False the opposite conversion is made.
    """
    if direction:
        inds=np.where(x[:,:]==nm)
        x[inds]=np.nan
    else:
        inds=np.where(np.isnan(x))
        x[inds]=nm
    return x


def find_cluster(x_bool):
    """
    Determines cluster with missing values in the same position.
    Returns their number and the index of their column.
    """
    v_bool=x_bool.sum(0)
    nb_cluster=0
    index_clusters=[]
    while np.max(v_bool)>0:
        index_clusters.append(np.argmax(v_bool))
        nb_cluster+=1
        v_bool=v_bool*(v_bool[:]!=np.max(v_bool))
    return nb_cluster, index_clusters

def cleaning_function(x,nm=-999,add_feat=True):
    """
    Replaces missing value with the mean of the column.
    Creates a dummy variable indicating rows where observations were missing for each cluster of variables with -999 in the same position.
    Creates an interaction term of the dummies of each cluster.
    """
    # nm= not_measured
    x_bool=x[:,:]==nm
    nb_cluster,index_clusters=find_cluster(x_bool)
    if add_feat:
        v=x[:,index_clusters]!=nm
        x=np.concatenate((x,v,(np.prod(v,axis=1)).reshape(-1,1)),axis=1)
    inds=np.where(x_bool)
    x[inds]=np.nan
    col_mean=np.nanmean(x,axis=0)
    x[inds]=np.take(col_mean,inds[1])
    return x,nb_cluster

def build_polinomial(x,degree,not_poly_features=0,nm=-999,already_cleaned=True):
    """
    Create polynomial features until specified degree. 
    It doesn't compute the power of the last columns of the matrix, which correspond to non-polynomial features 
    not_poly_features, i.e. the interaction terms.
    """
    if not already_cleaned:
        x=nan_converter(x,nm=nm,direction=True)
    phi_list=[np.ones(x.shape[0]).reshape(-1,1)]
    # is it possible to avoid the loop?
    for i in range(1,degree+1):
        phi_list.append(np.power(x[:,0:x.shape[1]-not_poly_features],i))
    if not_poly_features>0:
        phi_list.append(x[:,x.shape[1]-not_poly_features:])
    phi=np.concatenate(phi_list,axis=1)
    if not already_cleaned:
        phi=nan_converter(phi,nm=nm,direction=False)
    return phi

def norm_data(x,not_norm_features=0,skip_first_col=False):
    """
    Performs normalization of the data, subtracting the mean and dividing by the standard deviation of each column.
    """
    if skip_first_col:
        beg=1
    else:
        beg=0
    x_to_norm=x[:,beg:x.shape[1]-not_norm_features]
    means=np.mean(x_to_norm,axis=0)
    sds=np.std(x_to_norm,axis=0)
    x_to_norm=(x_to_norm-means.reshape(1,-1))/sds.reshape(1,-1)
    x[:,beg:x.shape[1]-not_norm_features]=x_to_norm
    return x

def features_augmentation(relevant_columns,not_augm_features=0):
    """
    Performs feature augmentation, creating interaction terms between the features.
    Returns the number of interactions created and the interaction columns.
    The dummies denoting missing variables are excluded.
    """
    num_col=relevant_columns.shape[1]-not_augm_features
    new_col=[]
    for i in range(num_col):
        for j in range(i+1,num_col):
            new_col.append(relevant_columns[:,i]*relevant_columns[:,j])
    new_col=np.array(new_col).transpose()
    if not_augm_features==0:
        new_col=np.concatenate((relevant_columns,new_col),axis=1)
    else:
        #print(new_col.shape,relevant_columns.shape)
        new_col=np.concatenate((relevant_columns[:,0:num_col],new_col,
                                relevant_columns[:,num_col:]),axis=1)
    num_col=new_col.shape[1]-relevant_columns.shape[1]
    return new_col,num_col

def norm_max(x):
    """
    Performs normalisation of variables by dividing by the maximum absolute value of a column.
    """
    max_column = (np.abs(x)).max(axis=0)
    x = x / (max_column + np.spacing(0))
    return x