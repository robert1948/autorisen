
import { ReactNode } from 'react'
export default function Card({title, subtitle, children}:{title:string, subtitle?:string, children?:ReactNode}){
  return <div className="card p-4">
    <div className="font-semibold">{title}</div>
    {subtitle && <div className="muted text-xs mt-1">{subtitle}</div>}
    {children && <div className="mt-3 text-sm">{children}</div>}
  </div>
}
