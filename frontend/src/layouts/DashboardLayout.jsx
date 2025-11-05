
import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

export default function DashboardLayout({ children }){
  const [open, setOpen] = useState(false);
  return (
    <div className="container">
      <Sidebar open={open} onClose={()=>setOpen(false)} />
      <main className="main">
        <Topbar onMenu={()=>setOpen(o=>!o)} />
        <div className="content">
          {children}
        </div>
      </main>
    </div>
  );
}
