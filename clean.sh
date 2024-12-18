for i in {1..4}; do	
  HOMEDIR=node$i	
  rm -rf $HOMEDIR/data/*.db $HOMEDIR/data/snapshots $HOMEDIR/data/cs.wal
  jq -n '{"height": "0", "round": 0, "step": 0}' > $HOMEDIR/data/priv_validator_state.json
done  
