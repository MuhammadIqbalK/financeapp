export class ApiError extends Error {
	status: number;
	detail: string;

	constructor(status: number, detail: string) {
		super(detail);
		this.status = status;
		this.detail = detail;
	}
}

// Dev: talk to the local API directly. Prod: same-origin (uvicorn serves the SPA).
export const BASE = import.meta.env.PUBLIC_API_URL ?? (import.meta.env.DEV ? 'http://127.0.0.1:8001' : '');

export function getToken(): string | null {
	if (typeof localStorage === 'undefined') return null;
	return localStorage.getItem('token');
}

export function setToken(token: string | null) {
	if (token) localStorage.setItem('token', token);
	else localStorage.removeItem('token');
}

type Options = {
	method?: string;
	body?: unknown;
};

export async function api<T>(path: string, opts: Options = {}): Promise<T> {
	const headers: Record<string, string> = {};
	if (opts.body !== undefined) headers['Content-Type'] = 'application/json';
	const token = getToken();
	if (token) headers['Authorization'] = `Bearer ${token}`;

	const res = await fetch(`${BASE}${path}`, {
		method: opts.method ?? 'GET',
		headers,
		body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined
	});

	if (res.status === 401 && typeof localStorage !== 'undefined') {
		setToken(null);
	}

	let data: unknown = null;
	try {
		data = await res.json();
	} catch {
		/* empty body */
	}

	if (!res.ok) {
		let detail = `Request failed (${res.status})`;
		if (data && typeof data === 'object' && 'detail' in data) {
			const d = (data as { detail: unknown }).detail;
			detail = typeof d === 'string' ? d : JSON.stringify(d);
		}
		throw new ApiError(res.status, detail);
	}
	return data as T;
}

export function qs(params: Record<string, string | number | undefined | null>): string {
	const search = new URLSearchParams();
	for (const [k, v] of Object.entries(params)) {
		if (v !== undefined && v !== null && v !== '') search.set(k, String(v));
	}
	const s = search.toString();
	return s ? `?${s}` : '';
}
