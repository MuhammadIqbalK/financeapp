export type AccountType = 'cash' | 'bank' | 'e-wallet' | 'other';
export type TxType = 'income' | 'expense';

export interface User {
	id: string;
	email: string;
	created_at: string;
}

export interface Account {
	id: string;
	name: string;
	type: AccountType;
	initial_balance: number;
	is_active: boolean;
	created_at: string;
	balance: number;
}

export interface Category {
	id: string;
	name: string;
	type: TxType;
	is_active: boolean;
}

export interface Transaction {
	id: string;
	type: TxType;
	amount: number;
	description: string;
	transaction_date: string;
	created_at: string;
	category_id: string;
	account_id: string;
	category_name: string;
	account_name: string;
}

export interface Transfer {
	id: string;
	amount: number;
	description: string;
	transfer_date: string;
	created_at: string;
	from_account_id: string;
	to_account_id: string;
	from_account_name: string;
	to_account_name: string;
}

export interface Budget {
	id: string;
	category_id: string;
	category_name: string;
	month: number;
	year: number;
	amount: number;
	spent: number;
	remaining: number;
	usage_percent: number;
}

export interface Point {
	label: string;
	income: number;
	expense: number;
}

export interface CategoryShare {
	category_id: string;
	category_name: string;
	amount: number;
	percent: number;
}

export interface Dashboard {
	period: { start: string; end: string };
	balance: number;
	income: number;
	expenses: number;
	savings: number;
	income_vs_expense: Point[];
	expense_by_category: CategoryShare[];
	recent_transactions: Transaction[];
	budgets: Budget[];
}

export interface Summary {
	year: number;
	month: number;
	income: number;
	expenses: number;
	net: number;
}

export interface TrendPoint {
	year: number;
	month: number;
	income: number;
	expense: number;
}

export type Period = 'today' | 'week' | 'month' | 'custom';
