// JavaScript for enhanced region mapper with added functionality and map integration
let map;
let polygon;
let botOverlay = null; // Overlay for the bot image

// Helper function: Calculate distance between two points in kilometers
function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Radius of Earth in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

// Helper function: Compute azimuth angle between two points
function calculateAzimuth(lat1, lng1, lat2, lng2) {
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const y = Math.sin(dLng) * Math.cos(lat2 * Math.PI / 180);
    const x = Math.cos(lat1 * Math.PI / 180) * Math.sin(lat2 * Math.PI / 180) -
        Math.sin(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.cos(dLng);
    return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360; // Normalize to [0, 360]
}

// Helper function: Find the closest edge and projection point
function findClosestEdge(point, edges) {
    let closestEdge = null;
    let minDistance = Infinity;
    let projection = null;

    edges.forEach(([start, end]) => {
        const A = {lat: start.lat, lng: start.lng};
        const B = {lat: end.lat, lng: end.lng};
        const AP = {lat: point.lat - A.lat, lng: point.lng - A.lng};
        const AB = {lat: B.lat - A.lat, lng: B.lng - A.lng};
        const abSquared = AB.lat * AB.lat + AB.lng * AB.lng;
        const apDotAb = AP.lat * AB.lat + AP.lng * AB.lng;
        const t = Math.max(0, Math.min(1, apDotAb / abSquared));
        const projectionPoint = {lat: A.lat + t * AB.lat, lng: A.lng + t * AB.lng};

        const distance = calculateDistance(point.lat, point.lng, projectionPoint.lat, projectionPoint.lng);
        if (distance < minDistance) {
            minDistance = distance;
            closestEdge = [A, B];
            projection = projectionPoint;
        }
    });

    return {closestEdge, projection};
}

// Helper function: Place the bot image on the map
function placeBot(position, angle) {
    if (botOverlay) botOverlay.setMap(null); // Remove existing bot

    class BotOverlay extends google.maps.OverlayView {
        constructor(position, angle) {
            super();
            this.position = position;
            this.angle = angle;
        }

        onAdd() {
            const div = document.createElement("div");
            div.style.position = "absolute";
            div.style.transform = `rotate(${this.angle}deg)`;
            div.style.transformOrigin = "center";

            div.innerHTML = `<img src="/static/imgs/cleaning_bot.png" alt="Bot" id="bot-image" style="width:30px;height:30px;transform: rotate(225deg)">`;
            this.div = div;
            const panes = this.getPanes();
            panes.overlayLayer.appendChild(div);
        }

        draw() {
            const projection = this.getProjection();
            const position = projection.fromLatLngToDivPixel(new google.maps.LatLng(this.position));
            this.div.style.left = `${position.x - 15}px`; // Center the bot
            this.div.style.top = `${position.y - 15}px`;  // Center the bot
        }

        onRemove() {
            this.div.parentNode.removeChild(this.div);
            this.div = null;
        }
    }

    botOverlay = new BotOverlay(position, angle);
    botOverlay.setMap(map);
}

// Compute the Convex Hull using Graham's scan algorithm
function computeConvexHull(points) {
    if (points.length < 3) return points; // Convex hull is undefined for fewer than 3 points

    points.sort((a, b) => a.lng === b.lng ? a.lat - b.lat : a.lng - b.lng);

    const cross = (o, a, b) => (a.lng - o.lng) * (b.lat - o.lat) - (a.lat - o.lat) * (b.lng - o.lng);

    const lower = [];
    for (const point of points) {
        while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], point) <= 0) {
            lower.pop();
        }
        lower.push(point);
    }

    const upper = [];
    for (const point of points.reverse()) {
        while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], point) <= 0) {
            upper.pop();
        }
        upper.push(point);
    }

    upper.pop();
    lower.pop();

    return lower.concat(upper);
}



async function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: {lat: 16.4913, lng: 80.4963}, // Default center
        zoom: 15,
        mapTypeId: 'terrain',
        // Enable compass
        mapTypeControlOptions: {
            mapTypeIds: ['roadmap', 'satellite', 'hybrid', 'terrain']
        },
        controls: {
            compass: true // Enabling compass control
        }
    });


    const regionPoints = await fetchRegionPoints();

    if (regionPoints && regionPoints.length > 2) {
        // Compute convex hull
        const hull = computeConvexHull(regionPoints);

        // Calculate centroid of the convex hull
        const centroid = calculateCentroid(hull);

        // Set the map center to the centroid
        map.setCenter({lat: centroid.lat, lng: centroid.lng});

        polygon = new google.maps.Polygon({
            paths: hull,
            strokeColor: "#FF0000",
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillOpacity: 0,
        });
        polygon.setMap(map);
        polygon.addListener('click', function (event) {
            // Event inside the polygon
            const latLng = event.latLng;
            console.log('Clicked inside polygon at:', latLng.lat(), latLng.lng());
            // Further logic for handling clicks inside the polygon
        });


        const edges = hull.map((point, i) => [point, hull[(i + 1) % hull.length]]);

        map.addListener("click", (e) => {
            console.log("Latitude: " + e.latLng.lat());
            console.log("Longitude: " + e.latLng.lng());

            const clickLatLng = e.latLng.toJSON();

            const {closestEdge, projection} = findClosestEdge(clickLatLng, edges);
            const angle = calculateAzimuth(
                projection.lat,
                projection.lng,
                closestEdge[1].lat,
                closestEdge[1].lng
            );

            const interpolatedGPS = `${projection.lat.toFixed(4)}° N, ${projection.lng.toFixed(4)}° E`;
            document.getElementById("gps").textContent = interpolatedGPS;
            document.getElementById("angle").textContent = `${angle.toFixed(2)}°`;

            placeBot(projection, angle);
        });
    } else {
        alert("No valid region points available.");
    }
}

// Helper function to calculate the centroid of a polygon
function calculateCentroid(points) {
    let latSum = 0, lngSum = 0;
    const n = points.length;

    points.forEach((point) => {
        latSum += point.lat;
        lngSum += point.lng;
    });

    return {
        lat: latSum / n,
        lng: lngSum / n,
    };
}

async function fetchRegionPoints() {
    try {
        const response = await fetch("/api/region/");
        if (!response.ok) throw new Error("Network response was not ok");
        const data = await response.json();
        return data.points;
    } catch (error) {
        console.error("Error fetching region points:", error);
        alert("Failed to load region points. Please try again later.");
        return null;
    }
}

window.initMap = initMap;
