let currentLat = 10.0;
let currentLng = 106.0;

let oldLat = 0;
let oldLng = 0;

let map =
    L.map("map").setView(
        [
            currentLat,
            currentLng
        ],
        18
    );

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19
    }
).addTo(map);

let marker =
    L.marker(
        [
            currentLat,
            currentLng
        ]
    ).addTo(map);

async function updateGPS()
{
    try
    {
        const res =
            await fetch("/gps");

        const data =
            await res.json();

        currentLat =
            parseFloat(
                data.latitude
            );

        currentLng =
            parseFloat(
                data.longitude
            );

        if (
            currentLat !== oldLat ||
            currentLng !== oldLng
        )
        {
            marker.setLatLng(
                [
                    currentLat,
                    currentLng
                ]
            );

            map.panTo(
                [
                    currentLat,
                    currentLng
                ]
            );

            oldLat =
                currentLat;

            oldLng =
                currentLng;
        }
    }
    catch (e)
    {
        console.log(e);
    }
}

function openMap()
{
    window.open(
        `https://www.google.com/maps?q=${currentLat},${currentLng}`,
        "_blank"
    );
}

updateGPS();

setInterval(
    updateGPS,
    1000
);