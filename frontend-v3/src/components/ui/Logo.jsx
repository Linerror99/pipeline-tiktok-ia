export default function Logo({ className = 'h-8' }) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg viewBox="0 0 40 40" fill="none" className="h-full w-auto" xmlns="http://www.w3.org/2000/svg">
        <circle cx="20" cy="20" r="18" stroke="currentColor" strokeWidth="1.5" />
        <path d="M15 12l12 8-12 8V12z" fill="currentColor" />
      </svg>
      <span className="font-serif text-xl font-semibold tracking-wide">REETIK</span>
    </div>
  )
}
