async function updateStatus()
{
    try
    {
        let res =
            await fetch(
                "/api/lock_status"
            );

        let data =
            await res.json();

        document.getElementById(
            "lockStatus"
        ).innerHTML =
            data.status;
    }
    catch (e)
    {
        console.log(e);
    }
}

updateStatus();

setInterval(
    updateStatus,
    1000
);