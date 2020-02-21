TFIDF_SRC_DIR = $(SRC_DIR)/TfIdf
export PYTHONPATH:=$(PYTHONPATH):$(TFIDF_SRC_DIR)/

$(TFIDF): $(TFIDF_SRC_DIR)/train_tfidf.py \
		$(TEXT_PREPROCESSED_TRAINING_NODES) \
		$(RAW_TRAINING_ARGUMENTS) \
		$(DICTIONARY) 
	$(PYTHON) $^ $@
	@echo

#$(TFIDF_SRC_DIR)/TfIdf.py: 
#	@touch $@

$(TFIDF_SRC_DIR)/train_tfidf.py: $(TFIDF_SRC_DIR)/TfIdf.py
	@touch $@

