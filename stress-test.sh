URL="http://localhost:25192/picker/pick/%s/%s"
users=()
for i in $(seq 1 500)
do
    users+=("$(head /dev/urandom | tr -dc a-z | fold -w 5 | head -n 1)")
done

run() {
    for tmp in $(seq 1 500)
    do
        campaign_id=$((RANDOM % 50 + 1))
        username=$((RANDOM % 500))
        r=$(curl -s -o /dev/null -w "%{http_code}" "$(printf ${URL} ${campaign_id} ${users[${username}]})")
        if [ "${r}" != "200" ]
        then
            echo "${r}"
        fi
    done
}

start_time=$(date +%s)
for i in $(seq 1 10)
do
    run &
done
wait
finish_time=$(date +%s)

echo "Stress test finished in $((finish_time - start_time)) seconds"