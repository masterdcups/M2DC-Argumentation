DICTIONARY_SRC_DIR = $(SRC_DIR)/Dictionary
export PYTHONPATH:=$(PYTHONPATH):$(DICTIONARY_SRC_DIR)/

$(DICTIONARY): $(DICTIONARY_SRC_DIR)/train_dictionary.py \
		$(TEXT_PREPROCESSED_TRAINING_NODES) \
		$(RAW_TRAINING_ARGUMENTS) \
		$(DICTIONARY_CFG) 
	$(PYTHON) $^ $@
	@echo

$(DICTIONARY_SRC_DIR)/Dictionary.py: $(MLLIB)/preprocessing/text_preprocessing/text_preprocessing.py
	@touch $@

$(DICTIONARY_SRC_DIR)/train_dictionary.py: $(DICTIONARY_SRC_DIR)/Dictionary.py
	@touch $@

