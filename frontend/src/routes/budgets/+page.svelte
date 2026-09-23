<script lang="ts">
	import { budgetsApi, categoriesApi, reportsApi } from '$lib/api';
	import type { Budget, Category, Summary, TrendPoint } from '$lib/types';
	import { formatRupiah, monthName, monthShort, nowMonthYear } from '$lib/format';
	import Modal from '$lib/components/Modal.svelte';
	import BudgetProgress from '$lib/components/BudgetProgress.svelte';

	const { month: initMonth, year: initYear } = nowMonthYear();

	let month = $state(initMonth);
	let year = $state(initYear);
	let budgets = $state<Budget[]>([]);
	let expenseCategories = $state<Category[]>([]);
	let summary = $state<Summary | null>(null);
	let trend = $state<TrendPoint[]>([]);
	let error = $state('');
	let notice = $state('');
	let showForm = $state(false);
	let editing = $state<Budget | null>(null);
	let deleting = $state<Budget | null>(null);

	let formCategory = $state('');
	let formAmount = $state('');

	async function load() {
		error = '';
		try {
			const [b, cats, s, t] = await Promise.all([
				budgetsApi.list(month, year),
				categoriesApi.list('expense'),
				reportsApi.summary(year, month),
				reportsApi.trend(6)
			]);
			budgets = b;
			expenseCategories = cats;
			summary = s;
			trend = t;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load';
		}
	}

	$effect(() => {
		void load();
	});

	function shift(delta: number) {
		let m = month + delta;
		let y = year;
		if (m < 1) {
			m = 12;
			y -= 1;
		} else if (m > 12) {
			m = 1;
			y += 1;
		}
		month = m;
		year = y;
	}

	function openCreate() {
		editing = null;
		formCategory = expenseCategories.find((c) => !budgets.some((b) => b.category_id === c.id))?.id
			?? expenseCategories[0]?.id
			?? '';
		formAmount = '';
		showForm = true;
	}

	function openEdit(b: Budget) {
		editing = b;
		formCategory = b.category_id;
		formAmount = String(b.amount);
		showForm = true;
	}

	async function save() {
		error = '';
		const amount = Number(formAmount);
		if (!formCategory || Number.isNaN(amount) || amount < 0) {
			error = 'Pick a category and a valid amount';
			return;
		}
		try {
			if (editing) {
				await budgetsApi.update(editing.id, { amount });
			} else {
				await budgetsApi.create({ category_id: formCategory, month, year, amount });
			}
			showForm = false;
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save';
		}
	}

	async function confirmDelete() {
		if (!deleting) return;
		try {
			await budgetsApi.remove(deleting.id);
			deleting = null;
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete';
		}
	}

	const availableCategories = $derived(
		expenseCategories.filter(
			(c) => !editing || c.id === editing.category_id || !budgets.some((b) => b.category_id === c.id)
		)
	);
</script>

<div class="page-head">
	<div class="row">
		<h1>Budgets</h1>
		<div class="seg">
			<button onclick={() => shift(-1)} type="button">‹</button>
			<button class="active" type="button">{monthName(month)} {year}</button>
			<button onclick={() => shift(1)} type="button">›</button>
		</div>
	</div>
	<button class="primary" onclick={openCreate} disabled={expenseCategories.length === 0}>
		+ Add Budget
	</button>
</div>

{#if error}<div class="error">{error}</div>{/if}
{#if notice}<div class="muted">{notice}</div>{/if}

<div class="grid grid-2" style="margin-bottom: 14px">
	<div class="card">
		<h2>Budget vs Spending</h2>
		<BudgetProgress budgets={budgets} />
	</div>

	<div>
		{#if summary}
			<div class="card" style="margin-bottom: 14px">
				<h2>Monthly Summary — {monthName(summary.month)} {summary.year}</h2>
				<table>
					<tbody>
						<tr>
							<td class="muted">Income</td>
							<td style="text-align: right; color: var(--green); font-weight: 600">
								{formatRupiah(summary.income)}
							</td>
						</tr>
						<tr>
							<td class="muted">Expenses</td>
							<td style="text-align: right; color: var(--red); font-weight: 600">
								{formatRupiah(summary.expenses)}
							</td>
						</tr>
						<tr>
							<td class="muted"><strong>Net</strong></td>
							<td style="text-align: right; font-weight: 700">{formatRupiah(summary.net)}</td>
						</tr>
					</tbody>
				</table>
			</div>
		{/if}

		<div class="card">
			<h2>Monthly Trend</h2>
			<table>
				<thead>
					<tr>
						<th>Month</th>
						<th style="text-align: right">Income</th>
						<th style="text-align: right">Expense</th>
					</tr>
				</thead>
				<tbody>
					{#each trend as t (t.year * 100 + t.month)}
						<tr>
							<td>{monthShort(t.month)} {t.year}</td>
							<td style="text-align: right; color: var(--green)">{formatRupiah(t.income)}</td>
							<td style="text-align: right; color: var(--red)">{formatRupiah(t.expense)}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>

{#if showForm}
	<Modal title={editing ? 'Edit Budget' : `Add Budget — ${monthName(month)} ${year}`} onclose={() => (showForm = false)}>
		<div class="field">
			<label for="b-cat">Category</label>
			<select id="b-cat" bind:value={formCategory} disabled={!!editing}>
				{#each availableCategories as c (c.id)}
					<option value={c.id}>{c.name}</option>
				{/each}
			</select>
		</div>
		<div class="field">
			<label for="b-amount">Monthly Limit</label>
			<input id="b-amount" type="number" min="0" placeholder="1500000" bind:value={formAmount} />
		</div>
		{#if error}<div class="error">{error}</div>{/if}
		<div class="row" style="justify-content: flex-end; margin-top: 8px">
			<button onclick={() => (showForm = false)}>Cancel</button>
			<button class="primary" onclick={save}>Save</button>
		</div>
	</Modal>
{/if}

<div class="card">
	<div class="row" style="justify-content: space-between; margin-bottom: 6px">
		<h2>All Budgets — {monthName(month)} {year}</h2>
	</div>
	{#if budgets.length === 0}
		<div class="empty">No budgets for this month. Set a spending limit per expense category.</div>
	{:else}
		<table>
			<thead>
				<tr>
					<th>Category</th>
					<th style="text-align: right">Budget</th>
					<th style="text-align: right">Spent</th>
					<th style="text-align: right">Remaining</th>
					<th style="text-align: right">Usage</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				{#each budgets as b (b.id)}
					<tr class="clickable" onclick={() => openEdit(b)}>
						<td>{b.category_name}</td>
						<td style="text-align: right">{formatRupiah(b.amount)}</td>
						<td style="text-align: right">{formatRupiah(b.spent)}</td>
						<td
							style="text-align: right; color: {b.remaining < 0 ? 'var(--red)' : 'inherit'}"
						>
							{formatRupiah(b.remaining)}
						</td>
						<td style="text-align: right">{b.usage_percent}%</td>
						<td style="text-align: right">
							<button
								class="small danger"
								onclick={(e) => {
									e.stopPropagation();
									deleting = b;
								}}
							>
								Delete
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>

{#if deleting}
	<Modal title="Delete budget?" onclose={() => (deleting = null)}>
		<p>Remove the {deleting.category_name} budget for {monthName(month)} {year}?</p>
		<div class="row" style="justify-content: flex-end; margin-top: 16px">
			<button onclick={() => (deleting = null)}>Cancel</button>
			<button class="danger" onclick={confirmDelete}>Delete</button>
		</div>
	</Modal>
{/if}
