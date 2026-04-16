import Link from "next/link";

const cardStyle: React.CSSProperties = {
  background: "#fff",
  padding: 20,
  borderRadius: 12,
  boxShadow: "0 1px 4px rgba(0,0,0,0.08)"
};

const linkStyle: React.CSSProperties = {
  display: "inline-block",
  padding: "10px 14px",
  background: "#111827",
  color: "#fff",
  borderRadius: 8,
  textDecoration: "none",
  marginRight: 12,
  marginBottom: 12
};

export default function HomePage() {
  return (
    <main>
      <h1 style={{ fontSize: 32, marginBottom: 8 }}>Auto SAS Analytics</h1>
      <p style={{ color: "#444", marginBottom: 24 }}>
        Automated SAS Analytics Platform MVP for upload, task creation, task run,
        and report inspection.
      </p>

      <div style={cardStyle}>
        <h2>Quick Actions</h2>
        <div style={{ marginTop: 16 }}>
          <Link href="/tasks/new" style={linkStyle}>
            Go to New Task
          </Link>
          <Link href="/tasks" style={linkStyle}>
            Go to Task List
          </Link>
          <Link href="/system" style={linkStyle}>
            Go to System Check
          </Link>
        </div>
      </div>
    </main>
  );
}
