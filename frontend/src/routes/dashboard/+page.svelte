<script lang="ts">
	import { dashboardApi } from '$lib/api';
	import type { Dashboard, Period } from '$lib/types';
	import { formatDate, formatRupiah, monthName, todayIso } from '$lib/format';
	import TrendChart from '$lib/components/TrendChart.svelte';
	import CategoryShares from '$lib/components/CategoryShares.svelte';
	import BudgetProgress from '$lib/components/BudgetProgress.svelte';

	let data = $state<Dashboard | null>(null);
	let error = $state('');
	let period = $state<Period>('month');
	let customStart = $state('');
	let customEnd = $state(todayIso());

	const PERIODS: { key: Period; label: string }[] = [
		{ key: 'today', label: 'Today' },
		{ key: 'week', label: 'This Week' },
		{ key: 'month', label: 'This Month' },
		{ key: 'custom', label: 'Custom' }
	];

	async function load() {
		error = '';
		try {
			data = await dashboardApi.get(
				period,
				period === 'custom' ? customStart : undefined,
				period === 'custom' ? customEnd : undefined
			);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load dashboard';
		}
	}

	$effect(() => {
		if (period !== 'custom' || (customStart && customEnd)) {
			void load();
		}
	});

	const periodLabel = $derived(
		data
			? `${formatDate(data.period.start)} – ${formatDate(data.period.end)}`
			: ''
	);
	const now = new Date();
</script>

<div class="page-head">
	<div>
		<h1>Dashboard</h1>
		<div class="muted" style="font-size: 13px">
			{monthName(now.getMonth() + 1)} {now.getFullYear()} · {periodLabel}
		</div>
	</div>
	<div class="seg">
		{#each PERIODS as p (p.key)}
			<button class:active={period === p.key} onclick={() => (period = p.key)} type="button">
				{p.label}
			</button>
		{/each}
	</div>
</div>

{#if period === 'custom'}
	<div class="toolbar">
		<div class="field">
			<label for="d-start">From</label>
			<input id="d-start" type="date" bind:value={customStart} />
		</div>
		<div class="field">
			<label for="d-end">To</label>
			<input id="d-end" type="date" bind:value={customEnd} />
		</div>
	</div>
{/if}

{#if error}
	<div class="error">{error}</div>
{/if}

{#if data}
	<div class="grid grid-4" style="margin-bottom: 14px">
		<div class="card stat">
			<div class="label">Balance</div>
			<div class="value">{formatRupiah(data.balance)}</div>
		</div>
		<div class="card stat">
			<div class="label">Income</div>
			<div class="value pos">{formatRupiah(data.income)}</div>
		</div>
		<div class="card stat">
			<div class="label">Expenses</div>
			<div class="value neg">{formatRupiah(data.expenses)}</div>
		</div>
		<div class="card stat">
			<div class="label">Savings</div>
			<div class="value" class:pos={data.savings >= 0} class:neg={data.savings < 0}>
				{formatRupiah(data.savings)}
			</div>
		</div>
	</div>

	<div class="card" style="margin-bottom: 14px">
		<h2>Income vs Expense</h2>
		<TrendChart points={data.income_vs_expense} />
	</div>

	<div class="grid grid-2" style="margin-bottom: 14px">
		<div class="card">
			<h2>Expense by Category</h2>
			<CategoryShares shares={data.expense_by_category} />
		</div>
		<div class="card">
			<h2>Recent Transactions</h2>
			{#if data.recent_transactions.length === 0}
				<div class="empty">No transactions yet. Add one from the Transactions page.</div>
			{:else}
				<table>
					<thead>
						<tr>
							<th>Description</th>
							<th>Date</th>
							<th style="text-align: right">Amount</th>
						</tr>
					</thead>
					<tbody>
						{#each data.recent_transactions as tx (tx.id)}
							<tr>
								<td>
									{tx.description || tx.category_name}
									<span class="badge {tx.type}" style="margin-left: 6px">{tx.type}</span>
								</td>
								<td class="muted">{formatDate(tx.transaction_date)}</td>
								<td
									style="text-align: right; font-weight: 600; color: {tx.type === 'income'
										? 'var(--green)'
										: 'var(--red)'}"
								>
									{tx.type === 'income' ? '+' : '−'}{formatRupiah(tx.amount)}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{/if}
		</div>
	</div>

	<div class="card">
		<div class="row" style="justify-content: space-between">
			<h2>Budget Usage — {monthName(now.getMonth() + 1)}</h2>
			<a href="/budgets" class="muted" style="font-size: 13px">Manage budgets →</a>
		</div>
		<BudgetProgress budgets={data.budgets} />
	</div>
{:else if !error}
	<div class="empty">Loading dashboard…</div>
{/if}
