#!/usr/bin/env bash

function  top_activity() {
    adb shell dumpsys activity activities | grep ResumedActivity | tail -1 | awk '{print $4}'
}

function  top_app() {
    adb shell dumpsys activity activities | grep ResumedActivity | tail -1 | awk '{print $4}' | awk -F '/' '{print $1}'
}

_last_page=''
while [[ 1 ]]; do
    app=`top_app`
    page=`top_activity`
    if [[ "${page}" != "${_last_page}" ]]; then
        echo 'new activities: ' ${page}
        _last_page=$page
    fi

    python3 fps.py reset $app
    sleep 2
    python3 fps.py collect $app > gfx.txt
    python3 fps.py fps gfx.txt
done