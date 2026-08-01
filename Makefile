.PHONY: verify paper clean

verify:
	cd proof && python3 verify_all.py

paper:
	cd paper && if command -v tectonic >/dev/null 2>&1; then tectonic -o . main.tex; elif command -v latexmk >/dev/null 2>&1; then latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex; else echo 'Need tectonic or latexmk to build the paper' >&2; exit 1; fi

clean:
	cd paper && latexmk -C
	rm -f proof/local_screen_general
