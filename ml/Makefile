# Setup
PYTHON=python3

DIR = ${CURDIR}

SRC_DIR = src
CFG_DIR = cfg

MLLIB_PATH = $(PWD)
MLLIB = $(MLLIB_PATH)/mllib
export PYTHONPATH:=$(PYTHONPATH):$(MLLIB_PATH)


DATA_DIR = data
# Input files
DATASETS_DIR = $(DATA_DIR)/raw

NODE_DIR = $(DATASETS_DIR)
RAW_NODES = $(NODE_DIR)/sentences.pkl

EMBEDDINGS_DIR = $(DATA_DIR)/word_embeddings
EMBEDDING = $(EMBEDDINGS_DIR)/fasttext_wiki.multi.en.npz

ARGUMENT_DIR = $(DATASETS_DIR)
RAW_TRAINING_ARGUMENTS = $(ARGUMENT_DIR)/train.pkl
RAW_VALIDATION_ARGUMENTS = $(ARGUMENT_DIR)/dev.pkl
RAW_TEST_ARGUMENTS = $(ARGUMENT_DIR)/test.pkl

# Output directories
OUTPUT_DIR = $(DATA_DIR)/basic

PREPROCESSED_DIR = $(OUTPUT_DIR)/preprocessed
MODEL_OUTPUT_DIR = $(OUTPUT_DIR)/models
EVALUATION_OUTPUT_DIR = $(OUTPUT_DIR)/evaluation

OUTPUT_DIRS = $(PREPROCESSED_DIR) $(MODEL_OUTPUT_DIR) $(EVALUATION_OUTPUT_DIR)

# Preprocessing targets
TEXT_PREPROCESSED_TRAINING_NODES = $(PREPROCESSED_DIR)/preprocessed_training_nodes.pkl
TEXT_PREPROCESSED_VALIDATION_NODES = $(PREPROCESSED_DIR)/preprocessed_validation_nodes.pkl

DICTIONARY = $(PREPROCESSED_DIR)/dictionary.pkl
DICTIONARY_CFG = $(CFG_DIR)/dictionary.yaml

TFIDF = $(PREPROCESSED_DIR)/tfidf_model.pkl

PREPROCESSED_TRAINING_ARGUMENTS = $(PREPROCESSED_DIR)/training_preprocessed_arguments.pkl
PREPROCESSED_VALIDATION_ARGUMENTS = $(PREPROCESSED_DIR)/validation_preprocessed_arguments.pkl
PREPROCESSED_TEST_ARGUMENTS = $(PREPROCESSED_DIR)/test_preprocessed_arguments.pkl

# Training targets
MODEL_SRC_DIR = $(SRC_DIR)/model
MODEL = $(MODEL_OUTPUT_DIR)/model.pkl

# Evaluation targets
EVALUATION_FILENAME = $(EVALUATION_OUTPUT_DIR)/evaluation.txt

#export

OUTPUTS = $(TEXT_PREPROCESSED_TRAINING_NODES) \
	  $(DICTIONARY) $(TFIDF) \
	  $(PREPROCESSED_TRAINING_FILENAME) $(PREPROCESSED_VALIDATION_ARGUMENTS) \
	  $(PREPROCESSED_TEST_ARGUMENTS) \
	  $(MODEL) $(EVALUATION_FILENAME)

### You can stop reading here if you just wanted to define paths.

# Main rule: post-build uses $(EVALUATION) included from model_src_dir
.PHONY: all
all: pre-build post-build

.PHONY: pre-build
pre-build: $(OUTPUT_DIRS)

# Preprocessing rules

$(SRC_DIR)/preprocess_nodes.py: $(SRC_DIR)/TextPreprocessor.py
	@touch $@

$(TEXT_PREPROCESSED_TRAINING_NODES): $(SRC_DIR)/preprocess_nodes.py \
		$(RAW_NODES) \
		$(RAW_TRAINING_ARGUMENTS)
	$(PYTHON) $^ $@
	@echo

$(TEXT_PREPROCESSED_VALIDATION_NODES): $(SRC_DIR)/preprocess_nodes.py \
		$(RAW_NODES) \
		$(RAW_VALIDATION_ARGUMENTS)
	$(PYTHON) $^ $@
	@echo

include $(SRC_DIR)/Dictionary/Makefile
#$(DICTIONARY): \
#		$(TEXT_PREPROCESSED_TRAINING_NODES) \
#		$(RAW_TRAINING_ARGUMENTS) \
#		$(DICTIONARY_CFG)
#	$(PYTHON) $(SRC_DIR)/train_dictionary.py $^ $@
#	@echo

include $(SRC_DIR)/TfIdf/Makefile
#$(TFIDF): \
#		$(TEXT_PREPROCESSED_TRAINING_NODES) \
#		$(RAW_TRAINING_ARGUMENTS) \
#		$(DICTIONARY)
#	$(PYTHON) $(SRC_DIR)/train_tfidf.py $^ $@
#	@echo

# Download a fastext embedding ("wiki.multi.en.vec" is one)
$(EMBEDDINGS_DIR)/fasttext_%.vec:
	wget https://dl.fbaipublicfiles.com/arrival/vectors/$*.vec -O $@

# Preprocess a .vec embedding file (to .npz)
$(EMBEDDINGS_DIR)/%.npz: $(SRC_DIR)/preprocess_vec_embedding.py \
		$(EMBEDDINGS_DIR)/%.vec
	$(PYTHON) $^ $@

$(PREPROCESSED_TRAINING_ARGUMENTS): \
		$(RAW_TRAINING_ARGUMENTS) \
		$(TEXT_PREPROCESSED_TRAINING_NODES) \
		$(DICTIONARY) \
		$(TFIDF) 
	echo $(PYTHONPATH)
	$(PYTHON) $(SRC_DIR)/preprocess_arguments.py $^ $@
	@echo

$(PREPROCESSED_VALIDATION_ARGUMENTS): \
		$(RAW_VALIDATION_ARGUMENTS) \
		$(TEXT_PREPROCESSED_VALIDATION_NODES) \
		$(DICTIONARY) \
		$(TFIDF) 
	$(PYTHON) $(SRC_DIR)/preprocess_arguments.py $^ $@
	@echo

# Training rules
include $(MODEL_SRC_DIR)/Makefile
#$(MODEL): \
#		$(PREPROCESSED_TRAINING_ARGUMENTS) \
#		$(PREPROCESSED_VALIDATION_ARGUMENTS) \
#		$(DICTIONARY_CFG)
#	$(PYTHON) $(SRC_DIR)/train_model.py $^ $@
#	@echo

# Evaluation rules

#$(EVALUATION_FILENAME): \
#		$(MODEL) \
#		$(PREPROCESSED_TRAINING_ARGUMENTS) \
#		$(PREPROCESSED_VALIDATION_ARGUMENTS) \
#		$(DICTIONARY_CFG)
#	$(PYTHON) $(SRC_DIR)/evaluate_model.py $^ # $@
#	@echo

post-build: $(EVALUATION) 

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
