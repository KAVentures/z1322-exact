.PHONY: verify paper clean

verify:
	cd proof && python3 verify_all.py
	cd proof/frontier_closure && python3 verify_all.py && python3 mutation_tests.py && python3 frontier_propagation.py

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

clean:
	cd paper && latexmk -C
	rm -f proof/local_screen_general
