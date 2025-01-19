let map;
let polygon;

// Helper function: Calculate distance between two points in kilometers
function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Radius of Earth in kilometers
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return (R * c).toFixed(2); // Distance in kilometers, rounded to 2 decimal places
}

// Helper function: Compute convex hull using the Graham scan algorithm
function computeConvexHull(points) {
    points.sort((a, b) => a.lat === b.lat ? a.lng - b.lng : a.lat - b.lat);
    const cross = (o, a, b) => (a.lat - o.lat) * (b.lng - o.lng) - (a.lng - o.lng) * (b.lat - o.lat);
    const hull = [];
    for (let point of points) {
        while (hull.length >= 2 && cross(hull[hull.length - 2], hull[hull.length - 1], point) <= 0) {
            hull.pop();
        }
        hull.push(point);
    }
    const t = hull.length + 1;
    for (let i = points.length - 1; i >= 0; i--) {
        const point = points[i];
        while (hull.length >= t && cross(hull[hull.length - 2], hull[hull.length - 1], point) <= 0) {
            hull.pop();
        }
        hull.push(point);
    }
    hull.pop();
    return hull;
}

// Initialize the map
async function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: {lat: 16.4913, lng: 80.4963},
        zoom: 13,
        mapTypeId: "satellite",
    });

    const regionPoints = await fetchRegionPoints();

    if (regionPoints && regionPoints.length > 2) {
        // Compute the convex hull
        const hull = computeConvexHull(regionPoints);

        // Draw the polygon
        polygon = new google.maps.Polygon({
            paths: hull,
            strokeColor: "#FF0000",
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillOpacity: 0, // No shading inside
        });
        polygon.setMap(map);

        // Label vertices and edges
        const bounds = new google.maps.LatLngBounds();
        for (let i = 0; i < hull.length; i++) {
            const current = hull[i];
            const next = hull[(i + 1) % hull.length];

            // Place a marker on the vertex with the label
            const marker = new google.maps.Marker({
                position: current,
                map: map,
            });

            // Calculate the distance for the edge
            const distance = calculateDistance(current.lat, current.lng, next.lat, next.lng);

            // Add a label at the midpoint of the edge
            const midPoint = {
                lat: (current.lat + next.lat) / 2,
                lng: (current.lng + next.lng) / 2,
            };
            new google.maps.Marker({
                position: midPoint,
                map: map,
                label: {
                    text: `${distance} km`,
                    fontSize: "8px",
                    fontWeight: "bold",
                    color: "black",
                    className: "edge-label"
                },
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 1, // Small dot
                    fillColor: "black",
                    fillOpacity: 1,
                    strokeWeight: 0
                },
            });

            // Add custom CSS for the background
            const style = document.createElement('style');
            style.innerHTML = `
                    .edge-label {
                        background-color: white;
                        padding: 2px 4px;
                        border-radius: 3px;
                    }
                `;
            document.head.appendChild(style);


            // Extend bounds to include the current vertex
            bounds.extend(current);
        }

        // Adjust the map to fit the bounds of the convex hull
        map.fitBounds(bounds);
    } else {
        alert('No valid region points available.');
    }
}

// Fetch region points from API
async function fetchRegionPoints() {
    try {
        const response = await fetch('/api/region/');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        return data.points;
    } catch (error) {
        console.error('Error fetching region points:', error);
        alert('Failed to load region points. Please try again later.');
        return null;
    }
}

window.initMap = initMap;