#!/bin/sh

echo "Loading cached fixtures"
echo "If this doesn't work, run rebuild_all.py instead"
./clear_db.py
../manage.py loaddata ../fixtures/all.json
