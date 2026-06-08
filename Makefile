.PHONY: locomo locomo-rerun locomo-dedup locomo-retrieval check-vars

check-vars:
	@test -n "$(ITERATION)" || (echo "Missing ITERATION" && exit 1)
	@test -n "$(VERSION)" || (echo "Missing VERSION" && exit 1)

PREVIOUS ?= results/locomo/simple_decomposition_result_2.json
PREVIOUS_LOGS ?= results/locomo/debug/deduplication_logs_4.json

locomo: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION)

locomo-rerun: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION) \
		--rerun \
		--previous-result-path $(PREVIOUS)

locomo-dedup: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION) \
		--rerun-deduplication \
		--previous-logs-path $(PREVIOUS_LOGS)

locomo-retrieval: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION) \
		--rerun-retrieval