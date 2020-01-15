#!/usr/bin/env bash

# adb shell input swipe 540 1300 540 500 100   从坐标点（540，1300）用100ms滑动到（540，500）坐标点

start_x=600
start_y=1200

end_x=600
end_y=500

dur_time=100
dur_all_time=360
current_second=0
while [ $current_second -le $dur_all_time ]; do
  sleep 1
  current_second=$(("$current_second" + 1))
  echo "$current_second"
  if [ $(("$current_second" % 2)) -eq 0 ]; then
    adb shell input swipe $start_x $start_y $end_x $end_y $dur_time
  else
    adb shell input swipe $end_x $end_y $start_x $start_y $dur_time
  fi
done
