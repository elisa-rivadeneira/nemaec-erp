/**
 * 🗺️ LEAFLET MAP - NEMAEC ERP
 * Mapa gratuito usando OpenStreetMap sin dependencias externas
 */
import React, { useEffect, useRef } from 'react';

// Cargar Leaflet dinámicamente
declare global {
  interface Window {
    L: any;
  }
}

interface MapLocation {
  id: number;
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

const LeafletMap: React.FC<LeafletMapProps> = ({
  locations,
  onLocationClick,
  center = { lat: -12.0464, lng: -77.0428 }, // Lima, Perú
  zoom = 11,
  className = "w-full h-96"
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const isInitialized = useRef(false);

  // Cargar Leaflet CSS y JS dinámicamente
  useEffect(() => {
    if (isInitialized.current) return;

    const loadLeaflet = async () => {
      try {
        // Cargar CSS
        if (!document.querySelector('link[href*="leaflet.css"]')) {
          const cssLink = document.createElement('link');
          cssLink.rel = 'stylesheet';
          cssLink.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
          cssLink.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
          cssLink.crossOrigin = '';
          document.head.appendChild(cssLink);
        }

        // Cargar JavaScript
        if (!window.L) {
          const script = document.createElement('script');
          script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
          script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
          script.crossOrigin = '';

          await new Promise((resolve, reject) => {
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
          });
        }

        // Esperar un poco para que Leaflet esté completamente cargado
        await new Promise(resolve => setTimeout(resolve, 100));

        initializeMap();
      } catch (error) {
        console.error('Error cargando Leaflet:', error);
      }
    };

    loadLeaflet();
  }, []);

  const initializeMap = () => {
    if (!mapRef.current || isInitialized.current || !window.L) return;

    try {
      // Crear el mapa
      const map = window.L.map(mapRef.current, {
        center: [center.lat, center.lng],
        zoom: zoom,
        scrollWheelZoom: true,
        doubleClickZoom: true,
        boxZoom: true,
        touchZoom: true,
        zoomControl: true
      });

      // Agregar capa de OpenStreetMap
      window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      mapInstanceRef.current = map;
      isInitialized.current = true;

      console.log('🗺️ Leaflet Map inicializado correctamente');

      // Agregar marcadores iniciales
      updateMarkers();

    } catch (error) {
      console.error('Error inicializando Leaflet map:', error);
    }
  };

  const updateMarkers = () => {
    if (!mapInstanceRef.current || !window.L) return;

    // Limpiar marcadores existentes
    markersRef.current.forEach(marker => {
      mapInstanceRef.current.removeLayer(marker);
    });
    markersRef.current = [];

    // Agregar nuevos marcadores
    locations.forEach(location => {
      const marker = window.L.marker([
        location.coordinates.lat,
        location.coordinates.lng
      ]);

      // Icono personalizado para comisarías
      const customIcon = window.L.divIcon({
        html: `<div style="
          background: #2563eb;
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

      marker.setIcon(customIcon);

      // Popup con información de la comisaría
      const popupContent = `
        <div style="min-width: 200px;">
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

      // Agregar al mapa
      marker.addTo(mapInstanceRef.current);
      markersRef.current.push(marker);
    });

    // Ajustar vista para mostrar todos los marcadores
    if (locations.length > 0 && markersRef.current.length > 0) {
      const group = new window.L.featureGroup(markersRef.current);
      mapInstanceRef.current.fitBounds(group.getBounds(), {
        padding: [20, 20],
        maxZoom: 13
      });
    }
  };

  // Actualizar marcadores cuando cambien las locations
  useEffect(() => {
    if (isInitialized.current) {
      updateMarkers();
    }
  }, [locations]);

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