async function updateWifi()
{
    try
    {
        let res =
            await fetch(
                "/api/wifi_status"
            );

        let data =
            await res.json();

        document.getElementById(
            "wifiName"
        ).innerHTML =
            data.wifi;

        if (
            data.wifi ===
            "Disconnected"
        )
        {
            document.getElementById(
                "wifiType"
            ).innerHTML =
                "Không có kết nối";

            return;
        }

        document.getElementById(
            "wifiType"
        ).innerHTML =
            data.backup
            ?
            "WiFi tạm thời"
            :
            "Mạng gốc X200";
    }
    catch (e)
    {
        console.log(e);
    }
}

updateWifi();

setInterval(
    updateWifi,
    3000
);