#!/usr/bin/env bash

echo "Number range: "
read -r range_number

shuf_number=$(shuf -i 1-"$range_number" -n1)

echo "Input number: "
read -r current_number

start_index=1
end_index=$range_number

while [ "$current_number" != "$shuf_number" ]; do

  if [ "$current_number" -le "$end_index" ] && [ "$current_number" -ge "$start_index" ]; then
    # -lt 小于, -gt 大于, -eq 等于
    # -le 小于等于, -ge 大于等于, -ne 不相等
    if [ "$current_number" -lt "$shuf_number" ]; then
      start_index=$current_number
      echo "small than shuf_number "
      echo "Input number: [$start_index ~ $end_index]"
      read -r current_number
    elif [ "$current_number" -gt "$shuf_number" ]; then
      end_index=$current_number
      echo "Big than shuf_numer "
      echo "Input number: [$start_index ~ $end_index]"
      read -r current_number
    fi
  else
    echo "You must input number between $start_index and $end_index"
    echo "Input number: "
    read -r current_number
  fi
done

echo "Bingo!!!, the shuf number is $shuf_number"
