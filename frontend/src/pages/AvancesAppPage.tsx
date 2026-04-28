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
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import type { AvanceApp } from '@/types';

const API = import.meta.env.VITE_API_URL || '/api/v1';

const AvancesAppPage: React.FC = () => {
  const [avances, setAvances] = useState<AvanceApp[]>([]);
  const [loading, setLoading] = useState(true);
  const [filtroCom, setFiltroCom] = useState('');
  const [ultimaSync, setUltimaSync] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<{ sincronizados: number; errores: number } | null>(null);

  async function cargar() {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/avances-app/`, {
        params: filtroCom ? { comisaria_codigo: filtroCom } : {},
      });
      setAvances(res.data);
      setUltimaSync(new Date().toLocaleTimeString('es-PE'));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { cargar(); }, [filtroCom]);

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

  // Comisarías únicas presentes en los avances
  const comisariasUnicas = [...new Set(avances.map(a => a.comisaria_codigo))].sort();

  // Stats
  const confirmados = avances.filter(a => a.acuerdo_con_avance === true).length;
  const corregidos = avances.filter(a => a.acuerdo_con_avance === false).length;
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
          <p className="text-2xl font-bold text-white">{avances.length}</p>
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

      {/* Filter */}
      <div className="flex items-center gap-3 mb-4">
        <FunnelIcon className="w-4 h-4 text-nemaec-gray-400" />
        <span className="text-nemaec-gray-400 text-sm">Filtrar por comisaría:</span>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFiltroCom('')}
            className={clsx(
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              !filtroCom
                ? 'bg-nemaec-green-700 text-white'
                : 'bg-nemaec-gray-700 text-nemaec-gray-300 hover:bg-nemaec-gray-600'
            )}
          >
            Todas
          </button>
          {comisariasUnicas.map(cod => (
            <button
              key={cod}
              onClick={() => setFiltroCom(cod)}
              className={clsx(
                'px-3 py-1 rounded-full text-xs font-medium transition-colors',
                filtroCom === cod
                  ? 'bg-nemaec-green-700 text-white'
                  : 'bg-nemaec-gray-700 text-nemaec-gray-300 hover:bg-nemaec-gray-600'
              )}
            >
              {cod}
            </button>
          ))}
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
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Comisaría</th>
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Partida</th>
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Residente</th>
                <th className="text-center px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">% Reportado</th>
                <th className="text-center px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Verificación</th>
                <th className="text-center px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">% Final</th>
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Observaciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-nemaec-gray-700/50">
              {avances.map(av => {
                const corregido = av.acuerdo_con_avance === false;
                const confirmado = av.acuerdo_con_avance === true;

                return (
                  <tr key={av.id} className="hover:bg-nemaec-gray-700/30 transition-colors">
                    <td className="px-4 py-3 text-nemaec-gray-300 whitespace-nowrap">
                      <p>{av.fecha}</p>
                      {av.hora && <p className="text-xs text-nemaec-gray-500">{av.hora}</p>}
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 bg-nemaec-gray-700 rounded text-xs text-nemaec-gray-300 font-mono">
                        {av.comisaria_codigo}
                      </span>
                    </td>
                    <td className="px-4 py-3 max-w-[200px]">
                      <p className="text-white font-mono text-xs">{av.codigo_partida}</p>
                      {av.descripcion_partida && (
                        <p className="text-nemaec-gray-400 text-xs truncate" title={av.descripcion_partida}>
                          {av.descripcion_partida}
                        </p>
                      )}
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
    </div>
  );
};

export default AvancesAppPage;
