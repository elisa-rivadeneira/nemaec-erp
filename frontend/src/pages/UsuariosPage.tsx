/**
 * 👷 USUARIOS DE OBRA - NEMAEC ERP
 * Gestión de Monitores de Obra e Ingenieros Residentes por comisaría.
 */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  UserGroupIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ShieldCheckIcon,
  UserIcon,
  BuildingOfficeIcon,
  XMarkIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import type { UsuarioObra, UsuarioObraCreate, RolUsuarioObra } from '@/types';

const API = import.meta.env.VITE_API_URL || '/api/v1';

interface ComisariaSimple {
  id: number;
  nombre: string;
  codigo: string;
  estado: string;
}

interface ComisariaConUsuarios {
  comisaria: ComisariaSimple;
  monitor?: UsuarioObra;
  residente?: UsuarioObra;
}

const ROL_LABEL: Record<RolUsuarioObra, string> = {
  monitor: 'Monitor de Obra',
  residente: 'Ingeniero Residente',
};

const ROL_COLOR: Record<RolUsuarioObra, string> = {
  monitor: 'bg-nemaec-green-700 text-white',
  residente: 'bg-blue-700 text-white',
};

// ─── Modal Form ──────────────────────────────────────────────────────────────

interface ModalProps {
  open: boolean;
  comisaria: ComisariaSimple | null;
  usuario: UsuarioObra | null;
  rolPredefinido?: RolUsuarioObra;
  todosUsuarios: UsuarioObra[];
  onClose: () => void;
  onSaved: () => void;
}

function UsuarioModal({ open, comisaria, usuario, rolPredefinido, todosUsuarios, onClose, onSaved }: ModalProps) {
  const rolInicial = rolPredefinido || 'monitor';
  const [form, setForm] = useState<UsuarioObraCreate>({
    nombre: '', dni: '', login: '', contrasena: '',
    rol: rolInicial,
    comisaria_id: comisaria?.id,
    comisaria_codigo: comisaria?.codigo,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [busqueda, setBusqueda] = useState('');
  const [mostrarSugerencias, setMostrarSugerencias] = useState(false);

  useEffect(() => {
    if (usuario) {
      setForm({ nombre: usuario.nombre, dni: usuario.dni, login: usuario.login, rol: usuario.rol, comisaria_id: usuario.comisaria_id, comisaria_codigo: usuario.comisaria_codigo });
    } else {
      setForm({ nombre: '', dni: '', login: '', contrasena: '', rol: rolInicial, comisaria_id: comisaria?.id, comisaria_codigo: comisaria?.codigo });
    }
    setError('');
    setBusqueda('');
  }, [usuario, comisaria, rolPredefinido, open]);

  if (!open) return null;

  // Usuarios existentes del mismo rol, filtrados por búsqueda
  const usuariosDelRol = todosUsuarios.filter(u => u.rol === form.rol);
  const sugerencias = busqueda.length >= 2
    ? usuariosDelRol.filter(u =>
        u.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
        u.login.toLowerCase().includes(busqueda.toLowerCase())
      ).slice(0, 6)
    : [];

  // Usuarios únicos por login (para el buscador)
  const usuariosUnicos = Array.from(new Map(usuariosDelRol.map(u => [u.login, u])).values());
  const sugerenciasUnicas = busqueda.length >= 2
    ? usuariosUnicos.filter(u =>
        u.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
        u.login.toLowerCase().includes(busqueda.toLowerCase())
      ).slice(0, 6)
    : [];

  function seleccionarExistente(u: UsuarioObra) {
    setForm(f => ({ ...f, nombre: u.nombre, dni: u.dni, login: u.login }));
    setBusqueda(u.nombre);
    setMostrarSugerencias(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (usuario) {
        await axios.put(`${API}/usuarios-obra/${usuario.id}`, form);
      } else {
        await axios.post(`${API}/usuarios-obra/`, form);
      }
      onSaved();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al guardar');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-nemaec-gray-800 border border-nemaec-green-500/30 rounded-2xl shadow-2xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b border-nemaec-green-500/20">
          <h2 className="text-white font-bold text-lg">
            {usuario ? 'Editar Usuario' : `Asignar ${ROL_LABEL[form.rol as RolUsuarioObra]}`}
          </h2>
          <button onClick={onClose} className="text-nemaec-gray-300 hover:text-white">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          {comisaria && (
            <div className="flex items-center gap-2 bg-nemaec-gray-700/50 rounded-lg px-3 py-2">
              <BuildingOfficeIcon className="w-4 h-4 text-nemaec-green-400" />
              <span className="text-nemaec-gray-200 text-sm font-medium">{comisaria.nombre}</span>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-nemaec-gray-300 mb-1 uppercase tracking-wide">Rol</label>
            <select
              value={form.rol}
              onChange={e => setForm(f => ({ ...f, rol: e.target.value as RolUsuarioObra }))}
              className="w-full bg-nemaec-gray-700 border border-nemaec-gray-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
            >
              <option value="monitor">Monitor de Obra</option>
              <option value="residente">Ingeniero Residente</option>
            </select>
          </div>

          {/* Buscador de usuario existente — solo para monitores (pueden cubrir varias comisarías) */}
          {!usuario && form.rol === 'monitor' && usuariosDelRol.length > 0 && (
            <div className="relative">
              <label className="block text-xs font-semibold text-nemaec-gray-300 mb-1 uppercase tracking-wide">
                Buscar usuario existente
              </label>
              <input
                type="text"
                value={busqueda}
                onChange={e => { setBusqueda(e.target.value); setMostrarSugerencias(true); }}
                onFocus={() => setMostrarSugerencias(true)}
                placeholder="Escribe nombre o login..."
                className="w-full bg-nemaec-gray-700 border border-nemaec-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-nemaec-gray-500 focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
              />
              {mostrarSugerencias && sugerenciasUnicas.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-nemaec-gray-700 border border-nemaec-gray-600 rounded-lg shadow-xl overflow-hidden">
                  {sugerenciasUnicas.map(u => (
                    <button
                      key={u.login}
                      type="button"
                      onClick={() => seleccionarExistente(u)}
                      className="w-full text-left px-3 py-2.5 hover:bg-nemaec-gray-600 transition-colors border-b border-nemaec-gray-600/50 last:border-0"
                    >
                      <p className="text-white text-sm font-medium">{u.nombre}</p>
                      <p className="text-nemaec-gray-400 text-xs">{u.login} · DNI {u.dni}</p>
                    </button>
                  ))}
                </div>
              )}
              <p className="text-xs text-nemaec-gray-500 mt-1">
                O deja vacío para crear uno nuevo abajo
              </p>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-nemaec-gray-300 mb-1 uppercase tracking-wide">Nombre completo</label>
            <input
              required
              value={form.nombre}
              onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))}
              placeholder="Ej: Nivardo Quispe Huanca"
              className="w-full bg-nemaec-gray-700 border border-nemaec-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-nemaec-gray-500 focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-nemaec-gray-300 mb-1 uppercase tracking-wide">DNI</label>
              <input
                required
                maxLength={8}
                value={form.dni}
                onChange={e => setForm(f => ({ ...f, dni: e.target.value }))}
                placeholder="45678901"
                className="w-full bg-nemaec-gray-700 border border-nemaec-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-nemaec-gray-500 focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-nemaec-gray-300 mb-1 uppercase tracking-wide">Login (usuario)</label>
              <input
                required
                value={form.login}
                onChange={e => setForm(f => ({ ...f, login: e.target.value.toLowerCase().replace(/\s/g, '') }))}
                placeholder="nquispe"
                className="w-full bg-nemaec-gray-700 border border-nemaec-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-nemaec-gray-500 focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-nemaec-gray-300 mb-1 uppercase tracking-wide">
              Contraseña
            </label>
            <input
              type="password"
              value={form.contrasena || ''}
              onChange={e => setForm(f => ({ ...f, contrasena: e.target.value }))}
              placeholder="Dejar vacío para usar el DNI"
              className="w-full bg-nemaec-gray-700 border border-nemaec-gray-600 rounded-lg px-3 py-2 text-white text-sm placeholder-nemaec-gray-500 focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
            />
            <p className="text-xs text-nemaec-gray-500 mt-1">Si no se ingresa, la contraseña será el DNI.</p>
          </div>

          {error && (
            <div className="bg-red-900/40 border border-red-500/40 rounded-lg px-3 py-2 text-red-300 text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 rounded-lg border border-nemaec-gray-600 text-nemaec-gray-300 hover:bg-nemaec-gray-700 text-sm font-medium transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 px-4 py-2.5 rounded-lg bg-nemaec-green-700 hover:bg-nemaec-green-600 text-white text-sm font-semibold transition-colors disabled:opacity-50"
            >
              {saving ? 'Guardando...' : usuario ? 'Actualizar' : 'Asignar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

const UsuariosPage: React.FC = () => {
  const [comisariasConUsuarios, setComisariasConUsuarios] = useState<ComisariaConUsuarios[]>([]);
  const [todosUsuarios, setTodosUsuarios] = useState<UsuarioObra[]>([]);
  const [loading, setLoading] = useState(true);
  const [busqueda, setBusqueda] = useState('');
  const [modal, setModal] = useState<{
    open: boolean;
    comisaria: ComisariaSimple | null;
    usuario: UsuarioObra | null;
    rol?: RolUsuarioObra;
  }>({ open: false, comisaria: null, usuario: null });

  async function cargarDatos() {
    setLoading(true);
    try {
      const [comRes, usrRes] = await Promise.all([
        axios.get(`${API}/comisarias/`),
        axios.get(`${API}/usuarios-obra/`),
      ]);

      const comisarias: ComisariaSimple[] = comRes.data;
      const usuarios: UsuarioObra[] = usrRes.data;

      setTodosUsuarios(usuarios);

      const resultado: ComisariaConUsuarios[] = comisarias.map(com => ({
        comisaria: com,
        monitor: usuarios.find(u => u.comisaria_id === com.id && u.rol === 'monitor'),
        residente: usuarios.find(u => u.comisaria_id === com.id && u.rol === 'residente'),
      }));

      setComisariasConUsuarios(resultado);
    } catch (e) {
      console.error('Error cargando datos:', e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { cargarDatos(); }, []);

  async function handleEliminar(usuario: UsuarioObra) {
    if (!confirm(`¿Eliminar a ${usuario.nombre}?`)) return;
    try {
      await axios.delete(`${API}/usuarios-obra/${usuario.id}`);
      cargarDatos();
    } catch (e) {
      console.error(e);
    }
  }

  const filtradas = comisariasConUsuarios.filter(c =>
    !busqueda ||
    c.comisaria.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    c.comisaria.codigo.toLowerCase().includes(busqueda.toLowerCase()) ||
    c.monitor?.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    c.residente?.nombre.toLowerCase().includes(busqueda.toLowerCase())
  );

  const totalMonitores = comisariasConUsuarios.filter(c => c.monitor).length;
  const totalResidentes = comisariasConUsuarios.filter(c => c.residente).length;
  const sinAsignar = comisariasConUsuarios.filter(c => !c.monitor || !c.residente).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-nemaec-gray-900 to-black p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <UserGroupIcon className="w-8 h-8 text-nemaec-green-400" />
          <h1 className="text-2xl font-bold text-white">Usuarios de Obra</h1>
        </div>
        <p className="text-nemaec-gray-300 text-sm">
          Monitores de obra e Ingenieros residentes asignados por comisaría
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-nemaec-gray-800/60 border border-nemaec-green-500/20 rounded-xl p-4">
          <p className="text-nemaec-gray-400 text-xs uppercase tracking-wide mb-1">Monitores asignados</p>
          <p className="text-2xl font-bold text-nemaec-green-400">{totalMonitores}</p>
          <p className="text-xs text-nemaec-gray-500">de {comisariasConUsuarios.length} comisarías</p>
        </div>
        <div className="bg-nemaec-gray-800/60 border border-blue-500/20 rounded-xl p-4">
          <p className="text-nemaec-gray-400 text-xs uppercase tracking-wide mb-1">Residentes asignados</p>
          <p className="text-2xl font-bold text-blue-400">{totalResidentes}</p>
          <p className="text-xs text-nemaec-gray-500">de {comisariasConUsuarios.length} comisarías</p>
        </div>
        <div className="bg-nemaec-gray-800/60 border border-yellow-500/20 rounded-xl p-4">
          <p className="text-nemaec-gray-400 text-xs uppercase tracking-wide mb-1">Pendientes completar</p>
          <p className="text-2xl font-bold text-nemaec-yellow-400">{sinAsignar}</p>
          <p className="text-xs text-nemaec-gray-500">sin monitor o residente</p>
        </div>
      </div>

      {/* Search */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Buscar por comisaría o nombre de usuario..."
          value={busqueda}
          onChange={e => setBusqueda(e.target.value)}
          className="w-full max-w-md bg-nemaec-gray-800 border border-nemaec-gray-600 rounded-lg px-4 py-2 text-white text-sm placeholder-nemaec-gray-500 focus:outline-none focus:ring-2 focus:ring-nemaec-green-500"
        />
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-2 border-nemaec-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="bg-nemaec-gray-800/60 border border-nemaec-green-500/20 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-nemaec-green-500/20">
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Comisaría</th>
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Monitor de Obra</th>
                <th className="text-left px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Ing. Residente</th>
                <th className="text-right px-4 py-3 text-nemaec-gray-400 font-semibold uppercase text-xs tracking-wide">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-nemaec-gray-700/50">
              {filtradas.map(({ comisaria, monitor, residente }) => (
                <tr key={comisaria.id} className="hover:bg-nemaec-gray-700/30 transition-colors">
                  {/* Comisaría */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <BuildingOfficeIcon className="w-4 h-4 text-nemaec-green-400 flex-shrink-0" />
                      <div>
                        <p className="text-white font-medium truncate max-w-[180px]">{comisaria.nombre}</p>
                        <p className="text-nemaec-gray-500 text-xs">{comisaria.codigo}</p>
                      </div>
                    </div>
                  </td>

                  {/* Monitor */}
                  <td className="px-4 py-3">
                    {monitor ? (
                      <div className="flex items-center gap-2">
                        <ShieldCheckIcon className="w-4 h-4 text-nemaec-green-400 flex-shrink-0" />
                        <div>
                          <p className="text-white font-medium">{monitor.nombre}</p>
                          <p className="text-nemaec-gray-500 text-xs">{monitor.login} · DNI {monitor.dni}</p>
                        </div>
                        <div className="ml-auto flex gap-1">
                          <button
                            onClick={() => setModal({ open: true, comisaria, usuario: monitor, rol: 'monitor' })}
                            className="p-1 text-nemaec-gray-400 hover:text-nemaec-green-400"
                            title="Editar"
                          >
                            <PencilIcon className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleEliminar(monitor)}
                            className="p-1 text-nemaec-gray-400 hover:text-red-400"
                            title="Eliminar"
                          >
                            <TrashIcon className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button
                        onClick={() => setModal({ open: true, comisaria, usuario: null, rol: 'monitor' })}
                        className="flex items-center gap-1.5 text-nemaec-gray-500 hover:text-nemaec-green-400 text-xs transition-colors"
                      >
                        <PlusIcon className="w-3.5 h-3.5" />
                        Asignar monitor
                      </button>
                    )}
                  </td>

                  {/* Residente */}
                  <td className="px-4 py-3">
                    {residente ? (
                      <div className="flex items-center gap-2">
                        <UserIcon className="w-4 h-4 text-blue-400 flex-shrink-0" />
                        <div>
                          <p className="text-white font-medium">{residente.nombre}</p>
                          <p className="text-nemaec-gray-500 text-xs">{residente.login} · DNI {residente.dni}</p>
                        </div>
                        <div className="ml-auto flex gap-1">
                          <button
                            onClick={() => setModal({ open: true, comisaria, usuario: residente, rol: 'residente' })}
                            className="p-1 text-nemaec-gray-400 hover:text-blue-400"
                            title="Editar"
                          >
                            <PencilIcon className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleEliminar(residente)}
                            className="p-1 text-nemaec-gray-400 hover:text-red-400"
                            title="Eliminar"
                          >
                            <TrashIcon className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ) : (
                      <button
                        onClick={() => setModal({ open: true, comisaria, usuario: null, rol: 'residente' })}
                        className="flex items-center gap-1.5 text-nemaec-gray-500 hover:text-blue-400 text-xs transition-colors"
                      >
                        <PlusIcon className="w-3.5 h-3.5" />
                        Asignar residente
                      </button>
                    )}
                  </td>

                  {/* Estado */}
                  <td className="px-4 py-3 text-right">
                    {monitor && residente ? (
                      <span className="inline-flex items-center gap-1 text-xs text-nemaec-green-400">
                        <CheckCircleIcon className="w-3.5 h-3.5" /> Completo
                      </span>
                    ) : (
                      <span className="text-xs text-nemaec-yellow-400">Incompleto</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filtradas.length === 0 && (
            <div className="text-center py-12 text-nemaec-gray-500">
              <UserGroupIcon className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p>No se encontraron comisarías</p>
            </div>
          )}
        </div>
      )}

      {/* Modal */}
      <UsuarioModal
        open={modal.open}
        comisaria={modal.comisaria}
        usuario={modal.usuario}
        rolPredefinido={modal.rol}
        todosUsuarios={todosUsuarios}
        onClose={() => setModal({ open: false, comisaria: null, usuario: null })}
        onSaved={cargarDatos}
      />
    </div>
  );
};

export default UsuariosPage;
