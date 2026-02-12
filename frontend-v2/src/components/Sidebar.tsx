import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Zap,
  LayoutDashboard,
  PlusCircle,
  Film,
  LogOut,
  Home } from
'lucide-react';
import { User } from '../hooks/useAuth';
interface SidebarProps {
  user: User | null;
  onLogout: () => void;
}
export function Sidebar({ user, onLogout }: SidebarProps) {
  const location = useLocation();
  const links = [
  {
    to: '/',
    icon: Home,
    label: 'Home'
  },
  {
    to: '/dashboard',
    icon: LayoutDashboard,
    label: 'Dashboard'
  },
  {
    to: '/create',
    icon: PlusCircle,
    label: 'Create'
  },
  {
    to: '/library',
    icon: Film,
    label: 'Library'
  }];

  return (
    <aside className="hidden md:flex flex-col w-72 h-screen glass-green fixed left-0 top-0 z-40 border-r border-emerald-500/10">
      {/* Logo */}
      <div className="p-8 border-b border-emerald-500/10">
        <div className="flex items-center space-x-3">
          <motion.div
            className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-lime-500 flex items-center justify-center"
            animate={{
              rotate: [0, 5, -5, 0]
            }}
            transition={{
              duration: 4,
              repeat: Infinity
            }}>

            <Zap className="w-5 h-5 text-dark-900" />
          </motion.div>
          <div>
            <h1 className="font-display font-bold text-xl text-white">
              Reetik
            </h1>
            <p className="text-xs text-emerald-400/60">Studio Pro</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {links.map((link) => {
          const isActive = location.pathname === link.to;
          return (
            <NavLink key={link.to} to={link.to} className="relative block">
              <motion.div
                className={`
                  flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300
                  ${isActive ? 'bg-emerald-500/10 text-emerald-400' : 'text-white/50 hover:text-white hover:bg-white/5'}
                `}
                whileHover={{
                  x: 4
                }}>

                <link.icon size={20} />
                <span className="font-medium">{link.label}</span>

                {isActive &&
                <motion.div
                  layoutId="sidebarActive"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-emerald-400 to-lime-400 rounded-r-full"
                  transition={{
                    type: 'spring',
                    stiffness: 300,
                    damping: 30
                  }} />

                }
              </motion.div>
            </NavLink>);

        })}
      </nav>

      {/* User Section */}
      {user &&
      <div className="p-4 border-t border-emerald-500/10">
          <div className="glass-green rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <img
                  src={user.avatar}
                  alt={user.name}
                  className="w-10 h-10 rounded-xl object-cover" />

                  <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-dark-900" />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{user.name}</p>
                  <p className="text-xs text-emerald-400/60">Pro Plan</p>
                </div>
              </div>
              <button
              onClick={onLogout}
              className="p-2 text-white/40 hover:text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-all">

                <LogOut size={18} />
              </button>
            </div>
          </div>
        </div>
      }
    </aside>);

}