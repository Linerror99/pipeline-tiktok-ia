import React from 'react';
import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Home, LayoutDashboard, PlusCircle, Film, User } from 'lucide-react';
export function MobileNav() {
  const links = [
  {
    to: '/',
    icon: Home,
    label: 'Home'
  },
  {
    to: '/dashboard',
    icon: LayoutDashboard,
    label: 'Dash'
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
    <div className="md:hidden fixed bottom-0 left-0 w-full glass-green border-t border-emerald-500/10 z-50 px-4 py-2">
      <div className="flex justify-around items-center">
        {links.map((link) =>
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) => `
              relative flex flex-col items-center py-2 px-4 rounded-xl transition-all
              ${isActive ? 'text-emerald-400' : 'text-white/40'}
            `}>

            {({ isActive }) =>
          <>
                <motion.div
              animate={{
                scale: isActive ? 1.1 : 1
              }}
              transition={{
                type: 'spring',
                stiffness: 300
              }}>

                  <link.icon size={22} />
                </motion.div>
                <span className="text-[10px] mt-1 font-medium">
                  {link.label}
                </span>
                {isActive &&
            <motion.div
              layoutId="mobileNav"
              className="absolute -top-2 left-1/2 -translate-x-1/2 w-8 h-1 bg-gradient-to-r from-emerald-400 to-lime-400 rounded-full"
              transition={{
                type: 'spring',
                stiffness: 300,
                damping: 30
              }} />

            }
              </>
          }
          </NavLink>
        )}
      </div>
    </div>);

}