import { api, qs } from './client';
import type {
	Account,
	Budget,
	Category,
	Dashboard,
	Period,
	Summary,
	TrendPoint,
	Transaction,
	Transfer,
	User
} from '$lib/types';

// Auth
export const authApi = {
	register: (email: string, password: string) =>
		api<{ access_token: string }>('/api/auth/register', {
			method: 'POST',
			body: { email, password }
		}),
	login: (email: string, password: string) =>
		api<{ access_token: string }>('/api/auth/login', {
			method: 'POST',
			body: { email, password }
		}),
	me: () => api<User>('/api/auth/me'),
	updateMe: (data: {
		email?: string;
		current_password?: string;
		new_password?: string;
	}) => api<User>('/api/auth/me', { method: 'PUT', body: data })
};

// Accounts
export const accountsApi = {
	list: (includeInactive = false) =>
		api<Account[]>(`/api/accounts${qs({ include_inactive: includeInactive ? 'true' : undefined })}`),
	create: (data: { name: string; type: string; initial_balance: number }) =>
		api<Account>('/api/accounts', { method: 'POST', body: data }),
	update: (id: string, data: Partial<{ name: string; type: string; initial_balance: number; is_active: boolean }>) =>
		api<Account>(`/api/accounts/${id}`, { method: 'PUT', body: data }),
	remove: (id: string) => api<{ detail: string }>(`/api/accounts/${id}`, { method: 'DELETE' })
};

// Categories
export const categoriesApi = {
	list: (type?: string) => api<Category[]>(`/api/categories${qs({ type })}`),
	create: (data: { name: string; type: string }) =>
		api<Category>('/api/categories', { method: 'POST', body: data }),
	update: (id: string, data: Partial<{ name: string; type: string; is_active: boolean }>) =>
		api<Category>(`/api/categories/${id}`, { method: 'PUT', body: data }),
	remove: (id: string) => api<{ detail: string }>(`/api/categories/${id}`, { method: 'DELETE' })
};

// Transactions
export const transactionsApi = {
	list: (filters: Record<string, string | number | undefined> = {}) =>
		api<Transaction[]>(`/api/transactions${qs(filters)}`),
	create: (data: {
		type: string;
		amount: number;
		category_id: string;
		account_id: string;
		description: string;
		transaction_date: string;
	}) => api<Transaction>('/api/transactions', { method: 'POST', body: data }),
	update: (
		id: string,
		data: Partial<{
			type: string;
			amount: number;
			category_id: string;
			account_id: string;
			description: string;
			transaction_date: string;
		}>
	) => api<Transaction>(`/api/transactions/${id}`, { method: 'PUT', body: data }),
	remove: (id: string) => api<{ detail: string }>(`/api/transactions/${id}`, { method: 'DELETE' })
};

// Transfers
export const transfersApi = {
	list: () => api<Transfer[]>('/api/transfers'),
	create: (data: {
		from_account_id: string;
		to_account_id: string;
		amount: number;
		description: string;
		transfer_date: string;
	}) => api<Transfer>('/api/transfers', { method: 'POST', body: data }),
	remove: (id: string) => api<{ detail: string }>(`/api/transfers/${id}`, { method: 'DELETE' })
};

// Budgets
export const budgetsApi = {
	list: (month: number, year: number) =>
		api<Budget[]>(`/api/budgets${qs({ month, year })}`),
	create: (data: { category_id: string; month: number; year: number; amount: number }) =>
		api<Budget>('/api/budgets', { method: 'POST', body: data }),
	update: (id: string, data: Partial<{ amount: number; month: number; year: number }>) =>
		api<Budget>(`/api/budgets/${id}`, { method: 'PUT', body: data }),
	remove: (id: string) => api<{ detail: string }>(`/api/budgets/${id}`, { method: 'DELETE' })
};

// Dashboard & reports
export const dashboardApi = {
	get: (period: Period, start?: string, end?: string) =>
		api<Dashboard>(`/api/dashboard${qs({ period, start, end })}`)
};

export const reportsApi = {
	summary: (year?: number, month?: number) =>
		api<Summary>(`/api/reports/summary${qs({ year, month })}`),
	trend: (months = 6) => api<TrendPoint[]>(`/api/reports/trend${qs({ months })}`)
};
