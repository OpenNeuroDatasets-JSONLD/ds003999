#!/bin/bash

setup_colors() {
  if [[ -t 2 ]] && [[ -z "${NO_COLOR-}" ]] && [[ "${TERM-}" != "dumb" ]]; then
    NOFORMAT='\033[0m' RED='\033[0;31m' GREEN='\033[0;32m' ORANGE='\033[0;33m' BLUE='\033[0;34m' PURPLE='\033[0;35m' CYAN='\033[0;36m' YELLOW='\033[1;33m'
  else
    NOFORMAT='' RED='' GREEN='' ORANGE='' BLUE='' PURPLE='' CYAN='' YELLOW=''
  fi
}

msg() {
  echo >&2 -e "$@"
}



max_children=10

function parallel {
    local time1=$(date +"%H:%M:%S")
    local time2=""

    # for the sake of the example, I'm using $2 as a description, you may be interested in other description
    msg "$GREEN Starting $NOFORMAT $@ ($time1)..."
    "$@" && time2=$(date +"%H:%M:%S") && msg "$ORANGE Finishing $NOFORMAT $@ ($time1 -- $time2)..." &

    local my_pid=$$
    local children=$(ps -eo ppid | grep -w $my_pid | wc -w)
    children=$((children-1))
    if [[ $children -ge $max_children ]]; then wait -n; fi
}

setup_colors

subs=$(awk '$5=="data2" {print $2}' sourcedata/name2id.tsv)
for sub in $subs
do
    for ses in $sub/*
    do
        file=$ses/anat/*nii.gz
        if [[ -d "$ses/anat" ]]; 
        then
            msg "$CYAN Now defacing file $NOFORMAT $file"
            defaced_file=$ses/anat/defaced_$(basename $file)
            parallel pydeface --outfile $defaced_file --force $file && echo "$CYAN Defacing $NOFORMAT $file $ORANGE finished! $NOFORMAT" 
        fi
    done
done
