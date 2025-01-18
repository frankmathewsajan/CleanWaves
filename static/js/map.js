let map;
let markers = [];
let polygon = null;

window.initMap = function () {
    map = new google.maps.Map(document.getElementById("map"), {
        center: {lat: 10.8505, lng: 76.2711},
        zoom: 7,
        mapTypeId: "satellite",
    });

    map.addListener("click", (event) => {
        toggleMarker(event.latLng);
    });

    document.getElementById("shade-region-btn").addEventListener("click", () => {
        redrawPolygon();
    });

    document.getElementById("clear-markers-btn").addEventListener("click", () => {
        clearMarkers();
    });
}

function toggleMarker(location) {
    // Check if a marker already exists at the clicked location
    const existingIndex = markers.findIndex((marker) => {
        const pos = marker.getPosition();
        return pos.lat() === location.lat() && pos.lng() === location.lng();
    });

    if (existingIndex !== -1) {
        // Remove marker
        markers[existingIndex].setMap(null);
        markers.splice(existingIndex, 1);
        return;
    }

    // Add new marker
    const marker = new google.maps.Marker({
        position: location,
        map: map,
    });
    markers.push(marker);
}

function clearMarkers() {
    markers.forEach((marker) => marker.setMap(null));
    markers = [];
    if (polygon) {
        polygon.setMap(null);
        polygon = null;
    }
}

function redrawPolygon() {
    if (markers.length < 3) return;

    if (polygon) polygon.setMap(null);

    const points = markers.map((marker) => marker.getPosition());
    const hull = getConvexHull(points);

    polygon = new google.maps.Polygon({
        paths: hull,
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.35,
        map: map,
    });
}

function getConvexHull(points) {
    points.sort((a, b) => a.lng() - b.lng() || a.lat() - b.lat());

    const cross = (o, a, b) =>
        (a.lng() - o.lng()) * (b.lat() - o.lat()) - (a.lat() - o.lat()) * (b.lng() - o.lng());

    const lower = [];
    for (const p of points) {
        while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) {
            lower.pop();
        }
        lower.push(p);
    }

    const upper = [];
    for (const p of points.slice().reverse()) {
        while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) {
            upper.pop();
        }
        upper.push(p);
    }

    lower.pop();
    upper.pop();
    return lower.concat(upper);
}
