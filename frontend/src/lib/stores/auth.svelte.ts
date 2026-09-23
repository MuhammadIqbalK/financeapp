import { authApi } from '$lib/api';
import { getToken, setToken } from '$lib/api/client';
import type { User } from '$lib/types';

class AuthState {
	token = $state<string | null>(null);
	user = $state<User | null>(null);
	ready = $state(false);

	constructor() {
		if (typeof localStorage !== 'undefined') {
			this.token = getToken();
		}
	}

	get isAuthenticated(): boolean {
		return this.token !== null;
	}

	async init(): Promise<void> {
		if (!this.token) {
			this.ready = true;
			return;
		}
		try {
			this.user = await authApi.me();
		} catch {
			this.token = null;
			setToken(null);
			this.user = null;
		} finally {
			this.ready = true;
		}
	}

	async login(email: string, password: string): Promise<void> {
		const { access_token } = await authApi.login(email, password);
		setToken(access_token);
		this.token = access_token;
		this.user = await authApi.me();
	}

	async register(email: string, password: string): Promise<void> {
		const { access_token } = await authApi.register(email, password);
		setToken(access_token);
		this.token = access_token;
		this.user = await authApi.me();
	}

	logout(): void {
		setToken(null);
		this.token = null;
		this.user = null;
	}
}

export const auth = new AuthState();
