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

        if (data.alarm)
        {
            alarm.innerHTML =
                "🚨 CẢNH BÁO";
        }
        else
        {
            alarm.innerHTML =
                "✅ Bình thường";
        }
    }
    catch (e)
    {
        console.log(e);
    }
}

updateAlarm();

setInterval(
    updateAlarm,
    1000
);