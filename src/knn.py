#-*-coding:utf-8 -*-
from sklearn import datasets
from numpy import *
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from sklearn.metrics import label_ranking_loss
from Config import get_config
config = get_config()

np.random.seed(0)  #设置随机种子，不设置的话默认是按系统时间作为参数，因此每次调用随机模块时产生的随机数都不一样设置后每次产生的一样

matrix = np.loadtxt(open(config.data_path + 'Test/' + 'Matrix_' + str(0.003) + 'LP.csv', "rb"), delimiter=",", skiprows=0 , dtype=int)
print matrix.shape

label = []
with open(config.data_path + 'Test/' + 'All electronic products_label.txt', 'r') as f:
    for line in f.readlines():
        label.append(int(line.strip()))
f.close()

pp_x = matrix
pp_y = array(label,  dtype=int)

indices = np.random.permutation(len(pp_x))
pp_x_train = pp_x[indices[:-109]]#随机选取140个样本作为训练数据集
pp_y_train = pp_y[indices[:-109]]#并且选取这140个样本的标签作为训练数据集的标签
pp_x_test  = pp_x[indices[-109:]]#剩下的10个样本作为测试数据集
pp_y_test  = pp_y[indices[-109:]]#并且把剩下10个样本对应标签作为测试数据集的标签

knn = KNeighborsClassifier()
knn.fit(pp_x_train, pp_y_train)

pp_y_predict = knn.predict(pp_x_test)
score = knn.score(pp_x_test, pp_y_test, sample_weight=None) #准确率
# neighborpoint = knn.kneighbors(pp_x_test[-1], 5, False) #计算与最后一个测试样本距离在最近的5个点，返回的是这些样本的序号组成的数组
probility = knn.predict_proba(pp_x_test)  #计算各测试样本基于概率的预测
print probility
print len(probility)

'''
print('pp_y_predict = ')  
print(pp_y_predict)  
#输出测试的结果
print('pp_y_test = ')
print(pp_y_test)    
#输出原始测试数据集的正确标签
print 'Accuracy:', score
#输出准确率计算结果
#print 'neighborpoint of last test sample:',neighborpoint
#print pp_x[neighborpoint]
print 'probility:', probility

'''
i = 0
PP_y_test = []
for i in range(len(pp_y_test)):
    if pp_y_test[i] == 1:
        PP_y_test.append([0, 1])
    else:
        PP_y_test.append([1, 0])
# print PP_y_test

# y_true = np.array([[1, 0, 0], [0, 0, 1]])
# y_score = np.array([[0.75, 0.5, 1], [1, 0.2, 0.1]])
loss = label_ranking_loss(PP_y_test, probility)
print loss, '+++'


# y_score = np.array([[1.0, 0.1, 0.2], [0.1, 0.2, 0.9]])
# print label_ranking_loss(pp_y_test, probility)


# classify_report = metrics.classification_report(y_true, y_pred)
# confusion_matrix = metrics.confusion_matrix(y_true, y_pred)
# overall_accuracy = metrics.accuracy_score(y_true, y_pred)
# acc_for_each_class = metrics.precision_score(y_true, y_pred, average=None)
# average_accuracy = np.mean(acc_for_each_class)
# score = metrics.accuracy_score(y_true, y_pred)
# print('classify_report : \n', classify_report)
# print('confusion_matrix : \n', confusion_matrix)
# print('acc_for_each_class : \n', acc_for_each_class)
# print('average_accuracy: {0:f}'.format(average_accuracy))
# print('overall_accuracy: {0:f}'.format(overall_accuracy))
# print('score: {0:f}'.format(score))