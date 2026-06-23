<script>

async function updateAlarm()
{
    let res =
        await fetch(
            "/api/alarm"
        );

    let data =
        await res.json();

    document.getElementById(
        "alarmStatus"
    ).innerHTML =
        data.alarm
        ?
        "🚨 CÓ TRỘM"
        :
        "An toàn";
}

updateAlarm();

setInterval(
    updateAlarm,
    1000
);

</script>