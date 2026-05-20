cd ~/models/models/damicore_tree_builder

PYTHONPATH=src python -m damicore_tree_builder.cli \
    --input ../fixtures/distance-matrix-output.csv \
    --output ../fixtures/dataset-seade-pop-age/output-phylo-tree-distance-ncd-gzip-cod_distr-ano-idade.newick
