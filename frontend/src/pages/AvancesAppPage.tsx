/**
 * 📱 AVANCES DESDE APP MÓVIL - NEMAEC ERP
 * Visualiza los avances verificados recibidos desde la app de monitoreo de campo.
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  DevicePhoneMobileIcon,
  FunnelIcon,
  CheckBadgeIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  ArrowsRightLeftIcon,
  XMarkIcon,
  PhotoIcon,
  DocumentTextIcon,
  UserIcon,
  ClockIcon,
  MapPinIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import type { AvanceApp } from '@/types';

const API = import.meta.env.VITE_API_URL || '/api/v1';

// Mapeo de códigos/IDs de comisaría a nombres
const COMISARIA_NOMBRES: Record<string, string> = {
  // Mapeo por código (compatibilidad con app móvil)
  'ENS': 'Ensenada',
  'CAR': 'Carabayllo',
  'SCA': 'San Cayetano',
  'SMP': 'San Martín de Porres',
  'VES': 'Villa el Salvador',
  // Mapeo por ID numérico (desde la BD)
  '62': 'Alfonso Ugarte',
  '63': 'Carabayllo',
  '64': 'Chancay',
  '65': 'Ciudad y Campo',
  '66': 'Collique',
  '67': 'Ensenada',
  '68': 'Jicamarca',
  '69': 'José Gálvez',
  '70': 'Mariscal Cáceres',
  '71': 'Pamplona',
  '72': 'Pro',
  '73': 'San Antonio de Jicamarca',
  '74': 'San Cayetano',
  '75': 'San Cosme',
  '76': 'San Genaro',
  '77': 'Santa Anita',
  '78': 'Santa Clara',
  '79': 'San Martín de Porres',
  '80': 'Tahuantinsuyo',
  '81': 'Villa El Salvador',
};

function obtenerNombreComisaria(codigo: string): string {
  return COMISARIA_NOMBRES[codigo] || codigo;
}

const AvancesAppPage: React.FC = () => {
  const [avances, setAvances] = useState<AvanceApp[]>([]);
  const [loading, setLoading] = useState(true);
  const [ultimaSync, setUltimaSync] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<{ sincronizados: number; errores: number } | null>(null);
  const [selectedAvance, setSelectedAvance] = useState<AvanceApp | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [filtros, setFiltros] = useState({
    comisaria: '',
    partida: '',
    residente: '',
  });
  const [filtrosVisible, setFiltrosVisible] = useState({
    comisaria: false,
    partida: false,
    residente: false,
  });

  async function cargar() {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/avances-app/`);
      setAvances(res.data);
      setUltimaSync(new Date().toLocaleTimeString('es-PE'));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { cargar(); }, []);

  // Cerrar filtros cuando se hace click fuera
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      const target = event.target as Element;
      if (!target.closest('th')) {
        setFiltrosVisible({ comisaria: false, partida: false, residente: false });
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  async function resincronizar() {
    setSyncing(true);
    setSyncResult(null);
    try {
      const res = await axios.post(`${API}/avances-app/resincronizar`);
      setSyncResult(res.data);
      await cargar();
    } catch (e) {
      console.error(e);
    } finally {
      setSyncing(false);
    }
  }

  // Aplicar filtros
  const avancesFiltrados = avances.filter(av => {
    const nombreComisaria = obtenerNombreComisaria(av.comisaria_codigo).toLowerCase();
    const descripcionPartida = (av.descripcion_partida || '').toLowerCase();
    const codigoPartida = av.codigo_partida.toLowerCase();
    const residenteLogin = (av.residente_login || '').toLowerCase();

    return (
      (!filtros.comisaria || nombreComisaria.includes(filtros.comisaria.toLowerCase())) &&
      (!filtros.partida || descripcionPartida.includes(filtros.partida.toLowerCase()) || codigoPartida.includes(filtros.partida.toLowerCase())) &&
      (!filtros.residente || residenteLogin.includes(filtros.residente.toLowerCase()))
    );
  });

  // Comisarías únicas presentes en los avances
  const comisariasUnicas = [...new Set(avances.map(a => a.comisaria_codigo))].sort();

  // Stats
  const confirmados = avancesFiltrados.filter(a => a.acuerdo_con_avance === true).length;
  const corregidos = avancesFiltrados.filter(a => a.acuerdo_con_avance === false).length;
  const sinVerificar = avances.filter(a => a.acuerdo_con_avance == null && a.monitor_verificador).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-nemaec-gray-900 to-black p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <DevicePhoneMobileIcon className="w-8 h-8 text-nemaec-green-400" />
            <h1 className="text-2xl font-bold text-white">Avances desde App Móvil</h1>
          </div>
          <p className="text-nemaec-gray-300 text-sm">
            Registros verificados por el monitor de obra en campo
            {ultimaSync && <span className="ml-2 text-nemaec-gray-500">· Última actualización: {ultimaSync}</span>}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {syncResult && (
            <span className="text-xs text-nemaec-green-400">
              ✓ {syncResult.sincronizados} avances sincronizados al ERP
              {syncResult.errores > 0 && ` · ${syncResult.errores} errores`}
            </span>
          )}
          <button
            onClick={resincronizar}
            disabled={syncing || loading}
            title="Sincroniza los avances de la app al Registro de Avances del ERP. Usar una sola vez si los avances no aparecen en el ERP."
            className="flex items-center gap-2 px-4 py-2 bg-nemaec-green-700 hover:bg-nemaec-green-600 text-white rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            <ArrowsRightLeftIcon className={clsx('w-4 h-4', syncing && 'animate-spin')} />
            {syncing ? 'Sincronizando...' : 'Sincronizar al ERP'}
          </button>
          <button
            onClick={cargar}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-nemaec-gray-700 hover:bg-nemaec-gray-600 text-nemaec-gray-200 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            <ArrowPathIcon className={clsx('w-4 h-4', loading && 'animate-spin')} />
            Actualizar
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-nemaec-gray-800/60 border border-nemaec-green-500/20 rounded-xl p-4">
          <p className="text-nemaec-gray-400 text-xs uppercase tracking-wide mb-1">Total registros</p>
          <p className="text-2xl font-bold text-white">{avancesFiltrados.length}</p>
          {avancesFiltrados.length !== avances.length && (
            <p className="text-xs text-nemaec-gray-500">de {avances.length} total</p>
          )}
        </div>
        <div className="bg-nemaec-gray-800/60 border border-green-500/20 rounded-xl p-4">
          <p className="text-nemaec-gray-400 text-xs uppercase tracking-wide mb-1">Confirmados</p>
          <p className="text-2xl font-bold text-green-400">{confirmados}</p>
          <p className="text-xs text-nemaec-gray-500">Monitor estuvo de acuerdo</p>
        </div>
        <div className="bg-nemaec-gray-800/60 border border-orange-500/20 rounded-xl p-4">
          <p className="text-nemaec-gray-400 text-xs uppercase tracking-wide mb-1">Corregidos</p>
          <p className="text-2xl font-bold text-orange-400">{corregidos}</p>
          <p className="text-xs text-nemaec-gray-500">Monitor ajustó el %</p>
        </div>
        <div className="bg-nemaec-gray-800/60 border border-nemaec-gray-600/30 rounded-xl p-4">
          <p className="text-nemaec-gray-400 text-xs uppercase tracking-wide mb-1">Comisarías activas</p>
          <p className="text-2xl font-bold text-nemaec-gray-200">{comisariasUnicas.length}</p>
        </div>
      </div>


      {/* Table */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-2 border-nemaec-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : avances.length === 0 ? (
        <div className="text-center py-20 text-nemaec-gray-500">
          <DevicePhoneMobileIcon className="w-12 h-12 mx-auto mb-3 opacity-20" />
          <p className="text-lg font-medium text-nemaec-gray-400">Sin avances sincronizados</p>
          <p className="text-sm mt-1">Los avances verificados en la app aparecerán aquí automáticamente</p>
        </div>
      ) : (
        <div className="bg-nemaec-gray-800/60 border border-nemaec-green-500/20 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-nemaec-green-500/20">
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Fecha</th>

                {/* Comisaría con filtro */}
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide relative">
                  <div className="flex items-center justify-between">
                    <span>Comisaría</span>
                    <button
                      onClick={() => setFiltrosVisible(prev => ({ ...prev, comisaria: !prev.comisaria }))}
                      className="p-1 hover:bg-nemaec-gray-700 rounded transition-colors"
                    >
                      <ChevronDownIcon className="w-3 h-3" />
                    </button>
                  </div>
                  {filtrosVisible.comisaria && (
                    <div className="absolute top-full left-0 mt-1 bg-nemaec-gray-800 border border-nemaec-gray-600 rounded-lg shadow-lg z-10 min-w-[200px]">
                      <input
                        type="text"
                        placeholder="Buscar comisaría..."
                        value={filtros.comisaria}
                        onChange={(e) => setFiltros(prev => ({ ...prev, comisaria: e.target.value }))}
                        className="w-full p-2 bg-nemaec-gray-700 text-white text-sm border-0 rounded-t-lg focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
                      />
                      {filtros.comisaria && (
                        <button
                          onClick={() => setFiltros(prev => ({ ...prev, comisaria: '' }))}
                          className="w-full text-left p-2 text-sm text-nemaec-gray-300 hover:bg-nemaec-gray-700 transition-colors border-t border-nemaec-gray-600"
                        >
                          Limpiar filtro
                        </button>
                      )}
                    </div>
                  )}
                </th>

                {/* Partida con filtro */}
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide relative">
                  <div className="flex items-center justify-between">
                    <span>Partida</span>
                    <button
                      onClick={() => setFiltrosVisible(prev => ({ ...prev, partida: !prev.partida }))}
                      className="p-1 hover:bg-nemaec-gray-700 rounded transition-colors"
                    >
                      <ChevronDownIcon className="w-3 h-3" />
                    </button>
                  </div>
                  {filtrosVisible.partida && (
                    <div className="absolute top-full left-0 mt-1 bg-nemaec-gray-800 border border-nemaec-gray-600 rounded-lg shadow-lg z-10 min-w-[250px]">
                      <input
                        type="text"
                        placeholder="Buscar por nombre o código..."
                        value={filtros.partida}
                        onChange={(e) => setFiltros(prev => ({ ...prev, partida: e.target.value }))}
                        className="w-full p-2 bg-nemaec-gray-700 text-white text-sm border-0 rounded-t-lg focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
                      />
                      {filtros.partida && (
                        <button
                          onClick={() => setFiltros(prev => ({ ...prev, partida: '' }))}
                          className="w-full text-left p-2 text-sm text-nemaec-gray-300 hover:bg-nemaec-gray-700 transition-colors border-t border-nemaec-gray-600"
                        >
                          Limpiar filtro
                        </button>
                      )}
                    </div>
                  )}
                </th>

                {/* Residente con filtro */}
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide relative">
                  <div className="flex items-center justify-between">
                    <span>Residente</span>
                    <button
                      onClick={() => setFiltrosVisible(prev => ({ ...prev, residente: !prev.residente }))}
                      className="p-1 hover:bg-nemaec-gray-700 rounded transition-colors"
                    >
                      <ChevronDownIcon className="w-3 h-3" />
                    </button>
                  </div>
                  {filtrosVisible.residente && (
                    <div className="absolute top-full left-0 mt-1 bg-nemaec-gray-800 border border-nemaec-gray-600 rounded-lg shadow-lg z-10 min-w-[200px]">
                      <input
                        type="text"
                        placeholder="Buscar residente..."
                        value={filtros.residente}
                        onChange={(e) => setFiltros(prev => ({ ...prev, residente: e.target.value }))}
                        className="w-full p-2 bg-nemaec-gray-700 text-white text-sm border-0 rounded-t-lg focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
                      />
                      {filtros.residente && (
                        <button
                          onClick={() => setFiltros(prev => ({ ...prev, residente: '' }))}
                          className="w-full text-left p-2 text-sm text-nemaec-gray-300 hover:bg-nemaec-gray-700 transition-colors border-t border-nemaec-gray-600"
                        >
                          Limpiar filtro
                        </button>
                      )}
                    </div>
                  )}
                </th>

                <th className="text-center px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">% Reportado</th>
                <th className="text-center px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Verificación</th>
                <th className="text-center px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">% Final</th>
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Observaciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-nemaec-gray-700/50">
              {avancesFiltrados.map(av => {
                const corregido = av.acuerdo_con_avance === false;
                const confirmado = av.acuerdo_con_avance === true;

                return (
                  <tr key={av.id} className="hover:bg-nemaec-gray-700/30 transition-colors">
                    <td className="px-4 py-3 text-nemaec-gray-300 whitespace-nowrap">
                      <p>{av.fecha}</p>
                      {av.hora && <p className="text-xs text-nemaec-gray-500">{av.hora}</p>}
                    </td>
                    <td className="px-4 py-3">
                      <p className="text-white font-medium text-sm">{obtenerNombreComisaria(av.comisaria_codigo)}</p>
                    </td>
                    <td
                      className="px-4 py-3 max-w-[300px] cursor-pointer hover:bg-nemaec-green-900/20 transition-colors"
                      onClick={() => {
                        setSelectedAvance(av);
                        setShowModal(true);
                      }}
                    >
                      <div className="space-y-1">
                        {av.descripcion_partida ? (
                          <>
                            <p className="text-white text-sm font-medium line-clamp-2">
                              {av.descripcion_partida}
                            </p>
                            <p className="text-nemaec-gray-400 text-xs font-mono">({av.codigo_partida})</p>
                          </>
                        ) : (
                          <p className="text-white font-mono text-sm font-semibold">{av.codigo_partida}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-nemaec-gray-300 text-xs">
                      {av.residente_login || '—'}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={clsx(
                        'font-bold',
                        corregido ? 'text-nemaec-gray-500 line-through' : 'text-nemaec-gray-200'
                      )}>
                        +{av.porcentaje_dia}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {confirmado && (
                        <span className="inline-flex items-center gap-1 text-green-400 text-xs font-medium">
                          <CheckBadgeIcon className="w-3.5 h-3.5" />
                          Confirmado
                        </span>
                      )}
                      {corregido && (
                        <div>
                          <span className="inline-flex items-center gap-1 text-orange-400 text-xs font-medium">
                            <ExclamationTriangleIcon className="w-3.5 h-3.5" />
                            Corregido
                          </span>
                          <p className="text-xs text-orange-300 font-semibold">+{av.porcentaje_dia_monitor}%</p>
                        </div>
                      )}
                      {!confirmado && !corregido && (
                        <span className="text-nemaec-gray-500 text-xs">
                          {av.monitor_verificador ? 'Directo monitor' : '—'}
                        </span>
                      )}
                      {av.monitor_verificador && (
                        <p className="text-nemaec-gray-600 text-xs mt-0.5">{av.monitor_verificador}</p>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={clsx(
                        'text-lg font-bold',
                        av.acumulado_final >= 100 ? 'text-blue-400' :
                        av.acumulado_final >= 70 ? 'text-green-400' :
                        av.acumulado_final >= 40 ? 'text-nemaec-yellow-400' : 'text-red-400'
                      )}>
                        {av.acumulado_final}%
                      </span>
                    </td>
                    <td className="px-4 py-3 max-w-[200px]">
                      {av.obs_monitor ? (
                        <p className="text-orange-300 text-xs truncate" title={av.obs_monitor}>
                          📋 {av.obs_monitor}
                        </p>
                      ) : av.obs_residente ? (
                        <p className="text-nemaec-gray-400 text-xs truncate" title={av.obs_residente}>
                          {av.obs_residente}
                        </p>
                      ) : (
                        <span className="text-nemaec-gray-600 text-xs">—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal de detalles */}
      {showModal && selectedAvance && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="bg-nemaec-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* Header del modal */}
            <div className="flex items-center justify-between p-6 border-b border-nemaec-gray-700">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <DocumentTextIcon className="w-6 h-6 text-nemaec-green-400" />
                  Detalle del Avance
                </h3>
                <p className="text-nemaec-gray-400 text-sm mt-1">
                  {obtenerNombreComisaria(selectedAvance.comisaria_codigo)} - {selectedAvance.fecha}
                </p>
              </div>
              <button
                onClick={() => {
                  setShowModal(false);
                  setSelectedAvance(null);
                }}
                className="p-2 hover:bg-nemaec-gray-700 rounded-lg transition-colors"
              >
                <XMarkIcon className="w-6 h-6 text-nemaec-gray-400" />
              </button>
            </div>

            {/* Contenido del modal */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Información de la partida */}
              <div className="bg-nemaec-gray-900/50 rounded-xl p-4 border border-nemaec-green-500/20">
                <h4 className="text-sm font-semibold text-nemaec-green-400 mb-3">Información de Partida</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-nemaec-gray-500 mb-1">Código</p>
                    <p className="text-white font-mono font-semibold">{selectedAvance.codigo_partida}</p>
                  </div>
                  <div>
                    <p className="text-xs text-nemaec-gray-500 mb-1">Avance acumulado</p>
                    <p className="text-2xl font-bold text-nemaec-green-400">{selectedAvance.acumulado_final}%</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-xs text-nemaec-gray-500 mb-1">Descripción</p>
                    <p className="text-white">
                      {selectedAvance.descripcion_partida || 'Sin descripción disponible'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Datos del Residente */}
                <div className="bg-nemaec-gray-900/50 rounded-xl p-4 border border-orange-500/20">
                  <h4 className="text-sm font-semibold text-orange-400 mb-3 flex items-center gap-2">
                    <UserIcon className="w-4 h-4" />
                    Registro del Residente
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-nemaec-gray-500 mb-1">Usuario</p>
                      <p className="text-white">{selectedAvance.residente_login || 'No registrado'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-nemaec-gray-500 mb-1">Porcentaje reportado</p>
                      <p className="text-lg font-bold text-orange-400">+{selectedAvance.porcentaje_dia}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-nemaec-gray-500 mb-1">Observaciones</p>
                      <p className="text-white bg-nemaec-gray-800 rounded-lg p-3 text-sm">
                        {selectedAvance.obs_residente || 'Sin observaciones'}
                      </p>
                    </div>
                    {selectedAvance.foto_residente && (
                      <div>
                        <p className="text-xs text-nemaec-gray-500 mb-2">Fotografía adjunta</p>
                        <div className="bg-nemaec-gray-800 rounded-lg p-3 flex items-center gap-2">
                          <PhotoIcon className="w-5 h-5 text-orange-400" />
                          <a
                            href={selectedAvance.foto_residente}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-orange-400 hover:text-orange-300 text-sm underline"
                          >
                            Ver imagen del residente
                          </a>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Verificación del Monitor */}
                <div className="bg-nemaec-gray-900/50 rounded-xl p-4 border border-green-500/20">
                  <h4 className="text-sm font-semibold text-green-400 mb-3 flex items-center gap-2">
                    <CheckBadgeIcon className="w-4 h-4" />
                    Verificación del Monitor
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-nemaec-gray-500 mb-1">Monitor verificador</p>
                      <p className="text-white">{selectedAvance.monitor_verificador || 'Registro directo'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-nemaec-gray-500 mb-1">Estado de verificación</p>
                      {selectedAvance.acuerdo_con_avance === true && (
                        <span className="inline-flex items-center gap-1 text-green-400 font-medium">
                          <CheckBadgeIcon className="w-4 h-4" />
                          Confirmado
                        </span>
                      )}
                      {selectedAvance.acuerdo_con_avance === false && (
                        <div>
                          <span className="inline-flex items-center gap-1 text-orange-400 font-medium">
                            <ExclamationTriangleIcon className="w-4 h-4" />
                            Corregido
                          </span>
                          <p className="text-sm text-orange-300 mt-1">
                            Porcentaje ajustado: +{selectedAvance.porcentaje_dia_monitor}%
                          </p>
                        </div>
                      )}
                      {selectedAvance.acuerdo_con_avance == null && (
                        <span className="text-nemaec-gray-400">Registro directo del monitor</span>
                      )}
                    </div>
                    <div>
                      <p className="text-xs text-nemaec-gray-500 mb-1">Observaciones del monitor</p>
                      <p className="text-white bg-nemaec-gray-800 rounded-lg p-3 text-sm">
                        {selectedAvance.obs_monitor || 'Sin observaciones del monitor'}
                      </p>
                    </div>
                    {selectedAvance.foto_monitor && (
                      <div>
                        <p className="text-xs text-nemaec-gray-500 mb-2">Fotografía del monitor</p>
                        <div className="bg-nemaec-gray-800 rounded-lg p-3 flex items-center gap-2">
                          <PhotoIcon className="w-5 h-5 text-green-400" />
                          <a
                            href={selectedAvance.foto_monitor}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-green-400 hover:text-green-300 text-sm underline"
                          >
                            Ver imagen del monitor
                          </a>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Metadatos adicionales */}
              <div className="bg-nemaec-gray-900/50 rounded-xl p-4 border border-nemaec-gray-700">
                <h4 className="text-sm font-semibold text-nemaec-gray-400 mb-3">Información adicional</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-xs text-nemaec-gray-500 mb-1 flex items-center gap-1">
                      <ClockIcon className="w-3 h-3" /> Hora
                    </p>
                    <p className="text-white">{selectedAvance.hora || '--:--'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-nemaec-gray-500 mb-1">Fecha verificación</p>
                    <p className="text-white">{selectedAvance.fecha_verificacion || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-nemaec-gray-500 mb-1 flex items-center gap-1">
                      <MapPinIcon className="w-3 h-3" /> Coordenadas
                    </p>
                    <p className="text-white text-xs">
                      {selectedAvance.lat && selectedAvance.lng
                        ? `${selectedAvance.lat.toFixed(4)}, ${selectedAvance.lng.toFixed(4)}`
                        : 'No disponible'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-nemaec-gray-500 mb-1">ID App</p>
                    <p className="text-white font-mono">#{selectedAvance.app_id}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AvancesAppPage;
