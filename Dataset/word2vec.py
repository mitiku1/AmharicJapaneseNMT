from Utils import load_config
import sentencepiece as spm
import os
import glob
from Exceptions import InvalidStateError
from tensorflow.keras.preprocessing import sequence
import numpy as np
from .base import DataGenerator


class Word2VecDataGenerator(DataGenerator):
    def __init__(self, config, language):
        self.language = language
        super(Word2VecDataGenerator, self).__init__(config)

    def _generate(self, case=None):

        vocabulary_size = self.config["params"]["vocab_size"]
        window_size = self.config["params"]["word2vec"]["window_size"]
        batch_size = self.config["hyper_params"]["word2vec"]["batch_size"]
        sampling_table = sequence.make_sampling_table(vocabulary_size, 0.1)
        while True:
            pairs = []
            labels = []
            indexes = np.arange(len(self.sentences))
            np.random.shuffle(indexes)
            for i in indexes:
                p, l = sequence.skipgrams(
                    self.sentences[i], vocabulary_size, window_size=window_size, sampling_table=sampling_table)
                pairs.extend(p)
                labels.extend(l)
                if len(pairs) >= batch_size:
                    
                    output_pairs = pairs[:batch_size]
                    output_labels = labels[:batch_size]

                    pairs = pairs[batch_size:]
                    labels = labels[batch_size:]
                    output_targets, output_contexts = zip(*output_pairs)

                    output_targets = np.array(output_targets, dtype=np.int32)
                    output_contexts = np.array(output_contexts, dtype=np.int32)

                    output_labels = np.array(output_labels, dtype=np.float32)

                    yield (output_targets, output_contexts), output_labels

    def _load_dataset(self):
        train_file, dev_file, test_file = self._get_data_files()
        train_sentences = self._load_sentences(train_file)
        dev_sentences = self._load_sentences(dev_file)
        test_sentences = self._load_sentences(test_file)

        self.sentences = train_sentences + dev_sentences + test_sentences

    def _load_sentences(self, filename):
        with open(filename) as data_file:
            sentences = data_file.read().splitlines()
            sentences = [[int(i.strip()) for i in sentence if len(
                i.strip()) > 0] for sentence in sentences]
            return sentences


class ReverseWord2VecDataGenerator(Word2VecDataGenerator):
    def __init__(self, config, language):
        super(ReverseWord2VecDataGenerator, self).__init__(config, language)

    def _generate(self, case=None):
        batch_size = self.config["hyper_params"]["rword2vec"]["batch_size"]
        while True:
            indexes = np.arange(len(self.sentences))
            np.random.shuffle(indexes)
            outputs = []
            for i in indexes:
                outputs.extend(self.sentences[i])
                if len(outputs) > batch_size:
                    o = outputs[:batch_size]
                    outputs = outputs[batch_size:]
                    yield np.array(o), np.array(o)
