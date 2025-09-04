// client/src/api/agents.js
export async function askFAQ(question) {
  const res = await fetch('/api/v1/agents/faq', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ question })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
