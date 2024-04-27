LOCALE_DIR ?= .

.PHONY: locale

locale: $(wildcard res/po/*.po)
	for f in $^; do \
	  lang=$$(basename $$f | cut -d '.' -f 1); \
	  target="$(LOCALE_DIR)/locale/$$lang/LC_MESSAGES"; \
	  mkdir -p "$$target"; \
	  msgfmt "$$f" -o "$$target/ginvoice.mo"; \
	  echo $$f to $$target/ginvoice.mo; \
	done
