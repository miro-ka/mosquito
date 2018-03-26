#!/bin/sh

# Simple scripts which fetched ticker data, runs blueprint and uploads data to gcp

DAYS=2
BUCKET=mosquito
BUCKER_DIR=data/
PAIRS=BTC_ETH
BLEUPRINT=blp5m1117


echo fetching ticker data
cd ..
python3 backfill.py --days $DAYS --pairs $PAIRS

echo generating blueprint
python3 blueprint.py --pairs $PAIRS --days $DAYS --features $BLEUPRINT


echo uploading to gcp
cd utils
python3 blueprints2gcp.py --bucket $BUCKET --bucket_dir $BUCKER_DIR

echo done



