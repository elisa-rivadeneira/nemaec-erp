/**
 * 🗺️ INTERACTIVE MAP COMPONENT - NEMAEC ERP
 * Componente de mapa interactivo para selección de ubicaciones de comisarías.
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  MapPinIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  CheckIcon,
  ArrowsPointingOutIcon
} from '@heroicons/react/24/outline';
import { MapPinIcon as MapPinIconSolid } from '@heroicons/react/24/solid';
import { mockLocations, type MapLocation } from '@/data/mockLocations';

interface InteractiveMapProps {
  onLocationSelect: (location: MapLocation) => void;
  initialQuery?: string;
  selectedLocation?: MapLocation | null;
  googleMapsResults?: MapLocation[];
  className?: string;
}

const InteractiveMap: React.FC<InteractiveMapProps> = ({
  onLocationSelect,
  initialQuery = '',
  selectedLocation,
  googleMapsResults = [],
  className = ''
}) => {
  const [searchQuery, setSearchQuery] = useState(initialQuery);

  // Sincronizar searchQuery con initialQuery cuando cambie
  useEffect(() => {
    setSearchQuery(initialQuery);
  }, [initialQuery]);
  const [filteredLocations, setFilteredLocations] = useState<MapLocation[]>([]);
  const [mapCenter, setMapCenter] = useState({ lat: -12.0464, lng: -77.0428 }); // Lima centro
  const [mapZoom, setMapZoom] = useState(11);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const mapRef = useRef<HTMLDivElement>(null);

  // Usar resultados de Google Maps si están disponibles, sino usar mock data
  const displayedLocations = googleMapsResults.length > 0 ? googleMapsResults : mockLocations;

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = displayedLocations.filter(location =>
        location.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        location.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
        location.distrito.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredLocations(filtered);

      // Si hay resultados, centrar el mapa en el primero
      if (filtered.length > 0) {
        setMapCenter(filtered[0].coordinates);
        setMapZoom(14);
      }
    } else {
      setFilteredLocations(displayedLocations);
    }
  }, [searchQuery, displayedLocations]);

  const handleLocationClick = (location: MapLocation) => {
    setMapCenter(location.coordinates);
    setMapZoom(16);
    onLocationSelect(location);
  };

  const getMarkerColor = (type: string, isSelected: boolean) => {
    if (isSelected) return '#EF4444'; // Rojo para seleccionado

    switch (type) {
      case 'cpnp': return '#10B981'; // Verde para CPNP
      case 'comisaria': return '#3B82F6'; // Azul para comisarías
      case 'sectorial': return '#8B5CF6'; // Púrpura para sectoriales
      default: return '#6B7280'; // Gris por defecto
    }
  };

  const getBadgeColor = (type: string) => {
    switch (type) {
      case 'cpnp': return 'bg-green-100 text-green-700';
      case 'comisaria': return 'bg-blue-100 text-blue-700';
      case 'sectorial': return 'bg-purple-100 text-purple-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Header del Mapa */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <MapPinIcon className="w-5 h-5 text-nemaec-green-600" />
            <span className="font-medium text-gray-800">Seleccionar Ubicación</span>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-1 text-gray-500 hover:text-gray-700 transition-colors"
            >
              <ArrowsPointingOutIcon className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Búsqueda */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Buscar: CPNP Carabayllo, Comisaría Alfonso Ugarte..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-nemaec-green-500 focus:border-transparent text-sm"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <div className="flex">
        {/* Lista de Resultados */}
        <div className="w-80 border-r border-gray-200 bg-gray-50">
          <div className="p-3 border-b border-gray-200">
            <div className="text-sm font-medium text-gray-700">
              {filteredLocations.length} ubicaciones encontradas
            </div>
          </div>

          <div className="h-80 overflow-y-auto">
            {filteredLocations.map((location) => {
              const isSelected = selectedLocation?.id === location.id;
              return (
                <div
                  key={location.id}
                  onClick={() => handleLocationClick(location)}
                  className={`p-3 border-b border-gray-200 cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-nemaec-green-50 border-l-4 border-l-nemaec-green-500'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <div className="font-medium text-gray-900 text-sm truncate">
                          {location.name}
                        </div>
                        <span className={`px-2 py-0.5 text-xs rounded-full ${getBadgeColor(location.type)}`}>
                          {location.type.toUpperCase()}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600 mb-1">
                        {location.address}
                      </div>
                      <div className="text-xs text-gray-500">
                        {location.distrito}, {location.provincia}
                      </div>
                    </div>
                    <div className="flex items-center ml-2">
                      {isSelected ? (
                        <CheckIcon className="w-4 h-4 text-nemaec-green-600" />
                      ) : (
                        <MapPinIconSolid
                          className="w-4 h-4"
                          style={{ color: getMarkerColor(location.type, false) }}
                        />
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Mapa Simulado */}
        <div className="flex-1 relative">
          <div
            ref={mapRef}
            className="h-80 bg-gradient-to-br from-blue-100 to-green-100 relative overflow-hidden"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='0.05'%3E%3Cpath d='m36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            }}
          >
            {/* Overlay del mapa */}
            <div className="absolute inset-0 bg-gray-100">

              {/* Simulación de calles y elementos urbanos */}
              <div className="absolute inset-0">
                {/* Calles principales - horizontales */}
                {[...Array(6)].map((_, i) => (
                  <div
                    key={`h-street-${i}`}
                    className="absolute w-full bg-gray-400"
                    style={{
                      top: `${15 * (i + 1)}%`,
                      height: '3px',
                      opacity: 0.8
                    }}
                  />
                ))}
                {/* Calles principales - verticales */}
                {[...Array(6)].map((_, i) => (
                  <div
                    key={`v-street-${i}`}
                    className="absolute h-full bg-gray-400"
                    style={{
                      left: `${15 * (i + 1)}%`,
                      width: '3px',
                      opacity: 0.8
                    }}
                  />
                ))}

                {/* Calles secundarias - horizontales */}
                {[...Array(12)].map((_, i) => (
                  <div
                    key={`h-secondary-${i}`}
                    className="absolute w-full bg-gray-300"
                    style={{
                      top: `${8 * (i + 1)}%`,
                      height: '1px',
                      opacity: 0.6
                    }}
                  />
                ))}
                {/* Calles secundarias - verticales */}
                {[...Array(12)].map((_, i) => (
                  <div
                    key={`v-secondary-${i}`}
                    className="absolute h-full bg-gray-300"
                    style={{
                      left: `${8 * (i + 1)}%`,
                      width: '1px',
                      opacity: 0.6
                    }}
                  />
                ))}

                {/* Parques y áreas verdes */}
                <div className="absolute bg-green-200 rounded-lg opacity-70"
                     style={{ top: '20%', left: '15%', width: '12%', height: '15%' }}></div>
                <div className="absolute bg-green-200 rounded-lg opacity-70"
                     style={{ top: '60%', left: '70%', width: '18%', height: '20%' }}></div>
                <div className="absolute bg-green-200 rounded-lg opacity-70"
                     style={{ top: '10%', left: '60%', width: '15%', height: '12%' }}></div>

                {/* Edificios importantes */}
                <div className="absolute bg-blue-200 rounded opacity-60"
                     style={{ top: '35%', left: '25%', width: '8%', height: '10%' }}></div>
                <div className="absolute bg-blue-200 rounded opacity-60"
                     style={{ top: '45%', left: '45%', width: '10%', height: '12%' }}></div>
                <div className="absolute bg-purple-200 rounded opacity-60"
                     style={{ top: '25%', left: '75%', width: '9%', height: '8%' }}></div>

                {/* Río o cuerpo de agua */}
                <div className="absolute bg-blue-300 opacity-50 rounded-full"
                     style={{
                       top: '5%',
                       left: '10%',
                       width: '80%',
                       height: '8%',
                       transform: 'rotate(-15deg)'
                     }}></div>
              </div>

              {/* Marcadores en el mapa */}
              {filteredLocations.map((location) => {
                const isSelected = selectedLocation?.id === location.id;
                // Calcular posición relativa en el mapa (simulado)
                const relativeX = ((location.coordinates.lng + 77.2) * 100) % 100;
                const relativeY = ((location.coordinates.lat + 12.5) * 100) % 100;

                return (
                  <div
                    key={`marker-${location.id}`}
                    className={`absolute transform -translate-x-1/2 -translate-y-full cursor-pointer transition-all duration-200 ${
                      isSelected ? 'scale-125 z-20' : 'z-10 hover:scale-110'
                    }`}
                    style={{
                      left: `${Math.max(10, Math.min(90, relativeX))}%`,
                      top: `${Math.max(10, Math.min(90, relativeY))}%`,
                    }}
                    onClick={() => handleLocationClick(location)}
                  >
                    {/* Pin del marcador */}
                    <div className="relative">
                      <div
                        className={`w-6 h-6 rounded-full border-2 border-white shadow-lg flex items-center justify-center ${
                          isSelected ? 'animate-pulse' : ''
                        }`}
                        style={{ backgroundColor: getMarkerColor(location.type, isSelected) }}
                      >
                        <MapPinIcon className="w-3 h-3 text-white" />
                      </div>

                      {/* Etiqueta del marcador */}
                      {(isSelected || searchQuery) && (
                        <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                          <div className="bg-gray-900 text-white text-xs px-2 py-1 rounded shadow-lg">
                            {location.name}
                          </div>
                          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              {/* Centro del mapa */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <div className="w-2 h-2 bg-gray-400 rounded-full opacity-50"></div>
              </div>
            </div>

            {/* Controles de zoom */}
            <div className="absolute top-4 right-4 flex flex-col space-y-1">
              <button
                onClick={() => setMapZoom(Math.min(18, mapZoom + 1))}
                className="w-8 h-8 bg-white border border-gray-300 rounded shadow text-gray-600 hover:bg-gray-50 flex items-center justify-center text-sm font-bold"
              >
                +
              </button>
              <button
                onClick={() => setMapZoom(Math.max(8, mapZoom - 1))}
                className="w-8 h-8 bg-white border border-gray-300 rounded shadow text-gray-600 hover:bg-gray-50 flex items-center justify-center text-sm font-bold"
              >
                −
              </button>
            </div>

            {/* Nivel de zoom */}
            <div className="absolute bottom-4 left-4 bg-white bg-opacity-90 px-2 py-1 rounded text-xs text-gray-600">
              Zoom: {mapZoom}
            </div>
          </div>
        </div>
      </div>

      {/* Ubicación Seleccionada */}
      {selectedLocation && (
        <div className="p-4 bg-nemaec-green-50 border-t border-nemaec-green-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-nemaec-green-600 flex items-center justify-center">
                <CheckIcon className="w-4 h-4 text-white" />
              </div>
              <div>
                <div className="font-medium text-nemaec-green-800">
                  Ubicación Seleccionada
                </div>
                <div className="text-sm text-nemaec-green-700">
                  {selectedLocation.name} - {selectedLocation.address}
                </div>
              </div>
            </div>
            <div className="text-right text-xs text-nemaec-green-600">
              <div>Lat: {selectedLocation.coordinates.lat.toFixed(4)}</div>
              <div>Lng: {selectedLocation.coordinates.lng.toFixed(4)}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InteractiveMap;