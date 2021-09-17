import pandas as pd
from sklearn.preprocessing import StandardScaler as ss
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt 
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def IVtable():
    df = pd.read_csv('csv/data.csv', sep=',', usecols=[1,2,3,4,5,6,7])
    ivtable=pd.DataFrame(df.columns,columns=['variable'])
    ivtable['IV']=None
    return ivtable,df

def CalculateIV(df, feature, target):
    lst = []
    df[feature] = df[feature].fillna("NULL")
    for i in range(df[feature].nunique()):
        val = list(df[feature].unique())[i]
        lst.append([feature,# Variable                                                       
                    val,# Value                                                        
                    df[df[feature] == val].count()[feature],# All                      
                    df[(df[feature] == val) & (df[target] > 0.92)].count()[feature],  # Good (think: score>0.92)
                    df[(df[feature] == val) & (df[target] <=0.92)].count()[feature]]) # Bad (think: score<=0.92)
    data = pd.DataFrame(lst, columns=['variable', 'value', 'A', 'G', 'B'])
    # data['share All'] = data['A'] / data['A'].sum()
    # data['Bad Rate'] = data['B'] / data['A']
    data['Distrib Good'] = (data['A'] - data['B']) / (data['A'].sum() - data['B'].sum())
    data['Distrib Bad'] = data['B'] / data['B'].sum()
    data['WoE'] = np.log(data['Distrib Good'] / data['Distrib Bad'])
    
    data = data.replace({'WoE': {np.inf: 0, -np.inf: 0}})
    data['IV'] = data['WoE'] * (data['Distrib Good'] - data['Distrib Bad'])
    data = data.sort_values(by=['variable', 'value'], ascending=[True, True])
    data.index = range(len(data.index))
    iv = data['IV'].sum()
    return iv, data

def FeatureData(data,ivtable,target):  
    list1=data.columns
    for l in list1: 
        iv, dt=CalculateIV(data,l,target)
        ivtable.loc[ivtable['variable']==l,'IV']=iv
    return ivtable


def analysis():
    #降维
    df = pd.read_csv('csv/data.csv', sep=',', usecols=[1,2,3,4,5,6,7])
    X = df.iloc[:, :-1]
    Y = df.iloc[:, -1]
    X2=df.iloc[:, lambda df: [0,1,2,3,4,6]]
    Y2=df.iloc[:,5]

    #data standarlization
    X_z = ss().fit_transform(X)
    X_z2= ss().fit_transform(X2)


    pca = PCA()
    pca2 = PCA()
    X_pca = pca.fit_transform(X_z)# get result of PCA
    X_pca2 = pca2.fit_transform(X_z2)
    

    # covariance
    X_cov = pca.get_covariance()
    X_cov2 = pca2.get_covariance()
    print('For audience_score, X_cov:\n',X_cov)
    print('For professional_score, X_cov:\n',X_cov2)
    # eigenvalues is got from`pca.explained_variance_`
    exp_var_ratio = pca.explained_variance_ratio_ 
    exp_var_ratio2 = pca2.explained_variance_ratio_
    print('For audience_score, exp_var_ratio:\n',exp_var_ratio) 
    print( 'For professional_score, exp_var_ratio2:\n',exp_var_ratio2) 
    return exp_var_ratio,exp_var_ratio2

def visualization():
    ivtable,data=IVtable()
    exp_var_ratio,exp_var_ratio2=analysis()
    
    with plt.style.context('seaborn-white'):
        plt.figure(figsize=(6, 6))
        #figure1:two graphs
        ax1 = plt.subplot(2,1,1)
        ax2 = plt.subplot(2,1,2)
        #figure2:two graphs
        plt.figure(figsize=(8, 4))
        ax3 = plt.subplot(2,1,1)
        ax4 = plt.subplot(2,1,2)

        plt.sca(ax1)#graph1: PCA for audiences' score
        plt.bar(range(6), exp_var_ratio, alpha=0.7, label='individual ratio')
        plt.ylabel('Explained variance ratio')
        plt.xlabel('for audience_score Principal components')
        plt.legend(loc='best')
        plt.tight_layout()

        plt.sca(ax2)#graph2: PCA for professional score
        plt.bar(range(6), exp_var_ratio2, alpha=0.7, label='individual ratio')
        plt.ylabel('Explained variance ratio')
        plt.xlabel('for professional_score Principal components')
        plt.legend(loc='best')
        plt.tight_layout()
        
        plt.sca(ax3)#graph3: info value for audience_lable
        iv1=FeatureData(data,ivtable,'audience_lable')
        plt.bar(list(iv1['variable'])[:-1], np.array(iv1['IV'])[:-1], alpha=0.7, label='for audience_lable')
        plt.legend(loc='best')
        plt.tight_layout()
        
        plt.sca(ax4)#graph4: info value for professional_lable
        iv2=FeatureData(data,ivtable,'professional_lable')
        plt.bar(np.array(iv2['variable'])[[0,1,2,3,4,6]], np.array(iv2['IV'])[[0,1,2,3,4,6]], alpha=0.7, label='for professional_lable')
        plt.legend(loc='best')
        plt.tight_layout()

        plt.show()

if __name__ == "__main__":
    visualization()
    