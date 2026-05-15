.PHONY: locomo locomo-rerun check-vars

check-vars:
	@test -n "$(ITERATION)" || (echo "Missing ITERATION" && exit 1)
	@test -n "$(VERSION)" || (echo "Missing VERSION" && exit 1)

PREVIOUS ?= results/locomo/simple_decomposition_result_2.json

locomo: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION)

locomo-rerun: check-vars
	python3 -m benchmarks.run_locomo_pipeline $(ITERATION) $(VERSION) \
		--rerun \
		--previous-result-path $(PREVIOUS)
