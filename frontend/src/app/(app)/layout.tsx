import { Sidebar } from "@/components/ui/nav";
import { SessionRefresher } from "@/components/ui/session-refresher";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <SessionRefresher />
      <Sidebar />
      <main className="flex-1 overflow-auto bg-gray-50">
        {children}
      </main>
    </div>
  );
}
