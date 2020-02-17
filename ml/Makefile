# Setup
PYTHON=python3

DIR = ${CURDIR}

SRC_DIR = src
CFG_DIR = cfg

MLLIB_DIR = $(DIR)
export PYTHONPATH=$(MLLIB_DIR)


DATA_DIR = data
# Input files
DATASETS_DIR = $(DATA_DIR)/raw

NODE_DIR = $(DATASETS_DIR)
NODE_FILENAME =$(NODE_DIR)/sentences.pkl

ARGUMENT_DIR = $(DATASETS_DIR)
ARGUMENT_TRAIN_FILENAME = $(ARGUMENT_DIR)/train.pkl
ARGUMENT_VALIDATION_FILENAME = $(ARGUMENT_DIR)/dev.pkl
ARGUMENT_TEST_FILENAME = $(ARGUMENT_DIR)/test.pkl

# Output directories
OUTPUT_DIR = $(DATA_DIR)/basic

PREPROCESSED_DIR = $(OUTPUT_DIR)/preprocessed
MODEL_DIR = $(OUTPUT_DIR)/models
EVALUATION_DIR = $(OUTPUT_DIR)/evaluation

OUTPUT_DIRS = $(PREPROCESSED_DIR) $(MODEL_DIR) $(EVALUATION_DIR)

# Preprocessing targets
PREPROCESSED_NODE_FILENAME = $(PREPROCESSED_DIR)/preprocessed_nodes.pkl

DICTIONARY_FILENAME = $(PREPROCESSED_DIR)/dictionary.pkl
DICTIONARY_CFG_FILENAME = $(CFG_DIR)/dictionary.yaml

TFIDF_FILENAME = $(PREPROCESSED_DIR)/tfidf_model.pkl

PREPROCESSED_TRAINING_FILENAME = $(PREPROCESSED_DIR)/training_preprocessed_arguments.pkl
PREPROCESSED_VALIDATION_FILENAME = $(PREPROCESSED_DIR)/validation_preprocessed_arguments.pkl
PREPROCESSED_TEST_FILENAME = $(PREPROCESSED_DIR)/test_preprocessed_arguments.pkl

# Training targets
MODEL_FILENAME = $(MODEL_DIR)/model.pkl

# Evaluation targets
EVALUATION_FILENAME = $(EVALUATION_DIR)/evaluation.txt

OUTPUTS = $(PREPROCESSED_NODE_FILENAME) \
	  $(DICTIONARY_FILENAME) $(TFIDF_FILENAME) \
	  $(PREPROCESSED_TRAINING_FILENAME) $(PREPROCESSED_VALIDATION_FILENAME) \
	  $(PREPROCESSED_TEST_FILENAME) \
	  $(MODEL_FILENAME) $(EVALUATION_FILENAME)

### You can stop reading here if you just wanted to define paths.

# Main rule
.PHONY: all
all: pre-build $(EVALUATION_FILENAME)

.PHONY: pre-build
pre-build: $(OUTPUT_DIRS)


# Preprocessing rules

$(PREPROCESSED_NODE_FILENAME): \
		$(NODE_FILENAME)
	$(PYTHON) $(SRC_DIR)/preprocess_nodes.py $^ $@
	@echo

$(DICTIONARY_FILENAME): \
		$(PREPROCESSED_NODE_FILENAME) \
		$(ARGUMENT_TRAIN_FILENAME) \
		$(DICTIONARY_CFG_FILENAME)
	$(PYTHON) $(SRC_DIR)/train_dictionary.py $^ $@
	@echo

$(TFIDF_FILENAME): \
		$(PREPROCESSED_NODE_FILENAME) \
		$(ARGUMENT_TRAIN_FILENAME) \
		$(DICTIONARY_FILENAME)
	$(PYTHON) $(SRC_DIR)/train_tfidf.py $^ $@
	@echo

$(PREPROCESSED_TRAINING_FILENAME): \
		$(ARGUMENT_TRAIN_FILENAME) \
		$(PREPROCESSED_NODE_FILENAME) \
		$(DICTIONARY_FILENAME) \
		$(TFIDF_FILENAME) 
	$(PYTHON) $(SRC_DIR)/preprocess_arguments.py $^ $@
	@echo

$(PREPROCESSED_VALIDATION_FILENAME): \
		$(ARGUMENT_VALIDATION_FILENAME) \
		$(PREPROCESSED_NODE_FILENAME) \
		$(DICTIONARY_FILENAME) \
		$(TFIDF_FILENAME) 
	$(PYTHON) $(SRC_DIR)/preprocess_arguments.py $^ $@
	@echo

# Training rules

$(MODEL_FILENAME): \
		$(PREPROCESSED_TRAINING_FILENAME) \
		$(PREPROCESSED_VALIDATION_FILENAME) \
		$(DICTIONARY_CFG_FILENAME)
	$(PYTHON) $(SRC_DIR)/train_model.py $^ $@
	@echo

# Evaluation rules

$(EVALUATION_FILENAME): \
		$(MODEL_FILENAME) \
		$(PREPROCESSED_TRAINING_FILENAME) \
		$(PREPROCESSED_VALIDATION_FILENAME) \
		$(DICTIONARY_CFG_FILENAME)
	$(PYTHON) $(SRC_DIR)/evaluate_model.py $^ # $@
	@echo


### Misc target rules

$(OUTPUT_DIRS): %: 
	@mkdir -p $@

.PHONY: clean
clean:
	@read -p "rm -rf $(OUTPUT_DIR) ? [y]/n " confirmation; \
	if [ -z "$$confirmation" ] || [ "$$confirmation" = "y" ]; \
	then \
		rm -rf $(OUTPUT_DIR); \
	fi
