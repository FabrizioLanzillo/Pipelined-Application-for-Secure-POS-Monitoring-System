import os
import joblib
from sklearn.model_selection import ParameterGrid

import utility
from development_system.training_configuration import TrainingConfiguration
from development_system.top_classifier import TopClassifier
from development_system.top_classifiers_report_generator import TopClassifierReportGenerator
from development_system.mlp_training import MLPTraining


class GridSearchController:

    def __init__(self, mlp_classifier: MLPTraining, training_conf: TrainingConfiguration):

        # data from the json training_configuration file
        self.validation_tolerance = training_conf.validation_tolerance
        self.number_of_top_classifiers = training_conf.number_of_top_classifiers

        # necessary field for the gridsearch algorithm
        self.grid_search_mlp_training = mlp_classifier
        self.validation_error_top_classifiers = dict.fromkeys([1, 2, 3, 4, 5])
        self.top_classifiers_object_list = []

    def save_classifier_among_top_classifier(self, id_classifier, possible_hyperparameters_combination):
        top_classifier = TopClassifier(id_classifier, self.grid_search_mlp_training,
                                       possible_hyperparameters_combination)
        if len(self.top_classifiers_object_list) == self.number_of_top_classifiers:
            self.top_classifiers_object_list[id_classifier - 1] = top_classifier
        else:
            self.top_classifiers_object_list.insert(id_classifier - 1, top_classifier)

        filename_classifier = "classifier_number_" + str(id_classifier) + ".sav"
        save_path = os.path.join(utility.data_folder, 'development_system/classifiers/' + filename_classifier)
        joblib.dump(self.grid_search_mlp_training.mlp, save_path)

    def check_validation_error_classifier(self, index, possible_hyperparameters_combination):

        if index <= self.number_of_top_classifiers:
            self.validation_error_top_classifiers.update({index: self.grid_search_mlp_training.validation_error})
            self.save_classifier_among_top_classifier(index, possible_hyperparameters_combination)

        else:
            key_value_with_max_validation_error = max(self.validation_error_top_classifiers,
                                                      key=self.validation_error_top_classifiers.get)
            if self.grid_search_mlp_training.validation_error not in self.validation_error_top_classifiers.values() \
                    and self.grid_search_mlp_training.validation_error < self.validation_error_top_classifiers.get(
                                                                                key_value_with_max_validation_error):
                self.validation_error_top_classifiers.update(
                    {key_value_with_max_validation_error: self.grid_search_mlp_training.validation_error}
                )
                self.save_classifier_among_top_classifier(key_value_with_max_validation_error,
                                                          possible_hyperparameters_combination)

    def generate_grid_search_hyperparameters(self, setted_hyper_parameters):

        grid_search = list(ParameterGrid(setted_hyper_parameters))
        index = 1
        for possible_hyperparameters_combination in grid_search:
            print(f"Combinazione {index}")
            self.grid_search_mlp_training.train_neural_network(possible_hyperparameters_combination)
            self.check_validation_error_classifier(index, possible_hyperparameters_combination)
            index = index + 1

        TopClassifierReportGenerator.generate_report(self.validation_tolerance,
                                                     self.number_of_top_classifiers,
                                                     self.top_classifiers_object_list)
