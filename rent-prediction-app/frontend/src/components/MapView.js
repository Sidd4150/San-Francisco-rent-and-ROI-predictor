import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const MapView = ({ onLocationSelect, currentLocation }) => {
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const mapInstanceRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current) return;

    // Initialize map
    const map = L.map(mapRef.current).setView(
      [currentLocation.lat, currentLocation.lng],
      13
    );

    mapInstanceRef.current = map;

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);

    // Add marker
    markerRef.current = L.marker([currentLocation.lat, currentLocation.lng], {
      draggable: true,
    }).addTo(map);

    // Handle marker drag
    markerRef.current.on('dragend', (e) => {
      const { lat, lng } = e.target.getLatLng();
      onLocationSelect(lat, lng);
    });

    // Handle map click
    map.on('click', (e) => {
      const { lat, lng } = e.latlng;
      markerRef.current.setLatLng([lat, lng]);
      onLocationSelect(lat, lng);
    });

    // Cleanup
    return () => {
      map.remove();
    };
  }, []);

  // Update marker position when currentLocation changes
  useEffect(() => {
    if (markerRef.current && mapInstanceRef.current) {
      markerRef.current.setLatLng([currentLocation.lat, currentLocation.lng]);
      mapInstanceRef.current.setView([currentLocation.lat, currentLocation.lng], 13);
    }
  }, [currentLocation]);

  return (
    <div className="map-container">
      <div ref={mapRef} className="map" style={{ height: '400px', width: '100%' }} />
      <p className="map-help">Click on the map or drag the marker to select a location</p>
    </div>
  );
};

export default MapView;