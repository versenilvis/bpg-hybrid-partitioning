# chay pipeline mo phong chinh
run:
    @python -B src/main.py

# chay toan bo suite 109 unit tests
test:
    -@python -B test/full_test.py

# chay rieng tung bo test
test-bpg:
    -@python -B test/test_bpg.py

test-first:
    -@python -B test/test_first_partitioning.py

test-unbalanced:
    -@python -B test/test_unbalanced_graph.py

test-mincut:
    -@python -B test/test_min_cut_graph.py

test-partitioning:
    -@python -B test/test_partitioning.py

# dong goi wheel va source distribution
build: clean
    @python -m build

# day package len pypi
publish: build
    @python -m twine upload dist/*

# don dep cache python va file build
clean:
    @rm -rf build dist *.egg-info src/*.egg-info
    @find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    @find . -type f -name "*.pyc" -delete 2>/dev/null || true
