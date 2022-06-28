import pandas as pd

from tensorflow.keras.datasets import imdb


class GetData():
    def __init__(self):
        pass

    def load_imdb_data(self, percentage_of_sentences=None):
        '''
        Loads data from IMDB
        These data are IMDB review
        Returns a list of strings
        '''

        # Load the data
        (sentences_train, y_train), (sentences_test, y_test) = imdb.load_data()

        # Take only a given percentage of the entire data
        if percentage_of_sentences is not None:
            assert(percentage_of_sentences> 0 and percentage_of_sentences<=100)

            len_train = int(percentage_of_sentences/100*len(sentences_train))
            sentences_train = sentences_train[:len_train]
            y_train = y_train[:len_train]

            len_test = int(percentage_of_sentences/100*len(sentences_test))
            sentences_test = sentences_test[:len_test]
            y_test = y_test[:len_test]

        # Load the {interger: word} representation
        word_to_id = imdb.get_word_index()
        word_to_id = {k:(v+3) for k,v in word_to_id.items()}
        for i, w in enumerate(['<PAD>', '<START>', '<UNK>', '<UNUSED>']):
            word_to_id[w] = i

        id_to_word = {v:k for k, v in word_to_id.items()}

        # Convert the list of integers to list of words (str)
        X_train = [' '.join([id_to_word[_] for _ in sentence[1:]]) \
            for sentence in sentences_train]

        return X_train

    def get(self, min_occurence=200, max_sentence_len=20):
        '''
        Loads a list of sentences
        Returns X (a list of lists of words) and y (a list of words)
        The word in y immediately follows the words in X in a sentence
        '''

        # load sentences
        data = self.load_imdb_data(percentage_of_sentences=10)

        df = pd.DataFrame({
            "word" : (" ".join(data)).split()
        })
        df["count"] = 1

        df_count = df.groupby(by="word", as_index=False).count()\
            .sort_values("count", ascending=False).reset_index(drop=True)

        # let's focus on words with at least 200 occurences
        df_200 = df_count[df_count["count"] > min_occurence]

        # for each of these words, let's find 200 sentences where they appear
        reference_list = df_200["word"].to_list()
        X = []
        y = []
        for sentence in data:
            words = sentence.split()
            for idx, word in enumerate(words):
                if word in reference_list:
                    X.append(words[:idx])
                    y.append(word)
        df_X_y = pd.DataFrame({
            "X" : X,
            "y" : y
        })
        df_X_y["len"] = df_X_y["X"].apply(len)
        df_X_y.sort_values(by="len", ascending=False, inplace=True)
        df_X_y = df_X_y[df_X_y["len"] > 0].reset_index(drop=True)

        df_X_y_200 = df_X_y.groupby("y").head(min_occurence)\
            .reset_index(drop=True)

        # one last thing: let's limit X to 20 words
        df_X_y_200["X_trimed"] = df_X_y_200["X"]\
            .apply(lambda x: x[-max_sentence_len:] \
                if len(x) > max_sentence_len else x)

        # return a list of lists of words and a list of words
        return df_X_y_200["X_trimed"].to_list(), df_X_y_200["y"].to_list()
