/**
 * 🗺️ LEAFLET MAP - NEMAEC ERP
 * Mapa gratuito usando OpenStreetMap con Leaflet como dependencia npm
 */
import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface MapLocation {
  id: string;
  name: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  address: string;
  tipo?: string;
  estado?: string;
}

interface LeafletMapProps {
  locations: MapLocation[];
  onLocationClick?: (location: MapLocation) => void;
  center?: { lat: number; lng: number };
  zoom?: number;
  className?: string;
}

// Fix for default markers in Leaflet - using only custom icons
delete (L.Icon.Default.prototype as any)._getIconUrl;

const LeafletMap: React.FC<LeafletMapProps> = ({
  locations,
  onLocationClick,
  center = { lat: -12.0464, lng: -77.0428 }, // Lima, Perú
  zoom = 11,
  className = "w-full h-96"
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);

  // Inicializar el mapa
  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) return;

    try {
      // Crear el mapa
      const map = L.map(mapRef.current, {
        center: [center.lat, center.lng],
        zoom: zoom,
        scrollWheelZoom: true,
        doubleClickZoom: true,
        boxZoom: true,
        touchZoom: true,
        zoomControl: true
      });

      // Agregar capa de OpenStreetMap
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      mapInstanceRef.current = map;
      console.log('🗺️ Leaflet Map inicializado correctamente');

    } catch (error) {
      console.error('Error inicializando Leaflet map:', error);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [center.lat, center.lng, zoom]);

  // Actualizar marcadores cuando cambien las locations
  useEffect(() => {
    if (!mapInstanceRef.current) return;

    const map = mapInstanceRef.current;

    // Limpiar marcadores existentes
    markersRef.current.forEach(marker => {
      map.removeLayer(marker);
    });
    markersRef.current = [];

    // Agregar nuevos marcadores
    locations.forEach(location => {
      // Crear icono personalizado basado en el estado
      const getMarkerColor = (estado?: string) => {
        switch (estado) {
          case 'completada': return '#10B981'; // Verde
          case 'en_proceso': return '#3B82F6'; // Azul
          case 'pendiente': return '#F59E0B'; // Amarillo
          default: return '#2563eb'; // Azul por defecto
        }
      };

      const customIcon = L.divIcon({
        html: `<div style="
          background: ${getMarkerColor(location.estado)};
          width: 24px;
          height: 24px;
          border-radius: 50% 50% 50% 0;
          transform: rotate(-45deg);
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
        ">
          <div style="
            color: white;
            font-size: 12px;
            font-weight: bold;
            transform: rotate(45deg);
          ">🏛️</div>
        </div>`,
        className: 'custom-marker',
        iconSize: [24, 24],
        iconAnchor: [12, 24],
      });

      const marker = L.marker([
        location.coordinates.lat,
        location.coordinates.lng
      ], { icon: customIcon });

      // Popup con información de la comisaría
      const popupContent = `
        <div style="min-width: 200px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
          <h3 style="margin: 0 0 8px 0; color: #1f2937; font-size: 14px; font-weight: 600;">
            ${location.name}
          </h3>
          <p style="margin: 0 0 8px 0; color: #6b7280; font-size: 12px;">
            📍 ${location.address}
          </p>
          ${location.tipo ? `
            <div style="margin: 4px 0;">
              <span style="
                background: #dbeafe;
                color: #1e40af;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 500;
              ">
                ${location.tipo}
              </span>
            </div>
          ` : ''}
          ${location.estado ? `
            <div style="margin: 4px 0;">
              <span style="
                background: ${location.estado === 'completada' ? '#dcfce7' : location.estado === 'en_proceso' ? '#fef3c7' : '#fee2e2'};
                color: ${location.estado === 'completada' ? '#166534' : location.estado === 'en_proceso' ? '#92400e' : '#991b1b'};
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 500;
              ">
                ${location.estado.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          ` : ''}
        </div>
      `;

      marker.bindPopup(popupContent);

      // Event listener para click
      if (onLocationClick) {
        marker.on('click', () => {
          onLocationClick(location);
        });
      }

      // Agregar al mapa y guardar referencia
      marker.addTo(map);
      markersRef.current.push(marker);
    });

    // Ajustar vista para mostrar todos los marcadores
    if (locations.length > 0) {
      const group = new L.FeatureGroup(markersRef.current);
      map.fitBounds(group.getBounds(), {
        padding: [20, 20],
        maxZoom: 13
      });
    }
  }, [locations, onLocationClick]);

  return (
    <div
      ref={mapRef}
      className={className}
      style={{
        borderRadius: '8px',
        border: '1px solid #e5e7eb',
        overflow: 'hidden'
      }}
    />
  );
};

export default LeafletMap;