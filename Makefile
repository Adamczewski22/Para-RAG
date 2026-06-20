.PHONY: locomo locomo-rerun locomo-dedup locomo-retrieval locomo-profiles check-vars

check-version:
	@test -n "$(VERSION)" || (echo "Missing VERSION" && exit 1)

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

locomo-profiles: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION) \
		--rerun-profiles \
		--previous-logs-path $(PREVIOUS_LOGS)

locomo-final: check-version
	python3 -m benchmarks.run_locomo_pipeline $(VERSION) \
		--final

locomo-profile-ablation: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION) \
		--rerun \
		--profile-ablation \
		--previous-result-path $(PREVIOUS)	

locomo-deduplication-ablation: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION) \
		--deduplication-ablation

locomo-decomposition-ablation: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION) \
		--decomposition-ablation
