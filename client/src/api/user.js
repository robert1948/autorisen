export async function getCurrentUser() {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('No token found');
  }

  const res = await fetch('/api/auth/me', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await res.json(); // call only once

  if (!res.ok) {
    throw new Error(data.detail || 'Failed to fetch user');
  }

  return data;
}
