async function updateAlarm()
{
    try
    {
        let res =
            await fetch(
                "/api/alarm"
            );

        let data =
            await res.json();

        let alarm =
            document.getElementById(
                "alarmStatus"
            );

        if (!alarm)
            return;

        if (data.alarm)
        {
            alarm.innerHTML =
                "🚨 XE ĐANG BỊ DI CHUYỂN";
        }
        else
        {
            alarm.innerHTML =
                "✅ AN TOÀN";
        }
    }
    catch (e)
    {
        console.log(e);
    }
}

setInterval(
    updateAlarm,
    1000
);