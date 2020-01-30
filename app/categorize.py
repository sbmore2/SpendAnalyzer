import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt


def load_training_data():
    names = ['Date', 'Desc', 'Amount', 'Balance', 'Category']
    df = pd.read_csv('train.csv', names=names)
    df['Desc'] = df['Desc'].apply(lambda x: x.strip('Card Purchase').strip())
    return df['Desc'], df['Category']


def categorize(df):
    X_train, y_train = load_training_data()
    text_clf = Pipeline([('vect', CountVectorizer()),
                         ('tfidf', TfidfTransformer()),
                         ('clf', LinearSVC()), ]) # MultinomialNB()

    text_clf.fit(X_train, y_train)
    df['Category'] = text_clf.predict(df['Desc'])
    accuracy = (text_clf.predict(X_train) == y_train).sum()*100/y_train.size
    print('Training Accuracy is %f%%' % accuracy)


def create_pie_chart(df):
    pie = df[(df['Amount'] <= 0) & (df['Category'] != 'Others')].groupby('Category')['Amount'].sum()
    pie = abs(pie)
    fig1, ax1 = plt.subplots()
    ax1.pie(pie.values, labels=pie.keys(), autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()

