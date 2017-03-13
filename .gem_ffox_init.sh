export GEM_FIREFOX_ON_HOLD=
if [ "$GEM_FIREFOX_ON_HOLD" ]; then
    sudo apt-mark hold firefox firefox-locale-en
else
    sudo apt-get update
    ffox_pol="$(apt-cache policy firefox)"
    ffox_cur="$(echo "$ffox_pol" | grep '^  Installed:' | sed 's/.*: //g')"
    ffox_can="$(echo "$ffox_pol" | grep '^  Candidate:' | sed 's/.*: //g')"
    if [ "$ffox_cur" != "$ffox_can" ]; then
        echo "WARNING: firefox has been upgraded, run it to accomplish update operations"
        sudo apt-get -y upgrade
        sudo apt-get -y install wmctrl
        export DISPLAY=:1
        firefox &
        ffox_pid=$!
        st="none"
        for i in $(seq 1 1000) ; do
            ffox_wins="$(wmctrl -l | grep -i "firefox" || true)"
            if [ "$st" = "none" ]; then
                if echo "$ffox_wins" | grep -qi 'update'; then
                    st="update"
                elif echo "$ffox_wins" | grep -qi 'mozilla'; then
                    break
                fi
            elif [ "$st" = "update" ]; then
                if echo "$ffox_wins" | grep -qvi 'update'; then
                    break
                fi
            fi
            sleep 0.02
        done
        kill $ffox_pid || true
        sleep 2
    fi
fi
