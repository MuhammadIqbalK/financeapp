<script lang="ts">
	import { accountsApi, categoriesApi, transactionsApi } from '$lib/api';
	import type { Account, Category, Transaction } from '$lib/types';
	import { formatDate, formatRupiah, todayIso } from '$lib/format';
	import TransactionForm from '$lib/components/TransactionForm.svelte';
	import Modal from '$lib/components/Modal.svelte';

	let items = $state<Transaction[]>([]);
	let accounts = $state<Account[]>([]);
	let categories = $state<Category[]>([]);
	let error = $state('');
	let showForm = $state(false);
	let editing = $state<Transaction | null>(null);
	let deleting = $state<Transaction | null>(null);
	let loaded = $state(false);

	let q = $state('');
	let type = $state('');
	let categoryId = $state('');
	let startDate = $state('');
	let endDate = $state('');

	async function load() {
		error = '';
		try {
			items = await transactionsApi.list({
				q: q || undefined,
				type: type || undefined,
				category_id: categoryId || undefined,
				start_date: startDate || undefined,
				end_date: endDate || undefined
			});
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load';
		}
	}

	async function init() {
		try {
			[accounts, categories] = await Promise.all([accountsApi.list(), categoriesApi.list()]);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load';
		} finally {
			loaded = true;
		}
	}

	let started = false;
	$effect(() => {
		if (started) return;
		started = true;
		void init();
	});

	$effect(() => {
		if (!loaded) return;
		void load();
	});

	async function confirmDelete() {
		if (!deleting) return;
		try {
			await transactionsApi.remove(deleting.id);
			deleting = null;
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete';
		}
	}
</script>

<div class="page-head">
	<h1>Transactions</h1>
	<button
		class="primary"
		onclick={() => {
			editing = null;
			showForm = true;
		}}
	>
		+ Add Transaction
	</button>
</div>

<div class="toolbar card" style="padding: 12px">
	<div class="field">
		<label for="f-q">Search</label>
		<input id="f-q" type="search" placeholder="Description…" bind:value={q} />
	</div>
	<div class="field">
		<label for="f-type">Type</label>
		<select id="f-type" bind:value={type}>
			<option value="">All</option>
			<option value="income">Income</option>
			<option value="expense">Expense</option>
		</select>
	</div>
	<div class="field">
		<label for="f-cat">Category</label>
		<select id="f-cat" bind:value={categoryId}>
			<option value="">All</option>
			{#each categories as c (c.id)}
				<option value={c.id}>{c.name}</option>
			{/each}
		</select>
	</div>
	<div class="field">
		<label for="f-from">From</label>
		<input id="f-from" type="date" bind:value={startDate} />
	</div>
	<div class="field">
		<label for="f-to">To</label>
		<input id="f-to" type="date" bind:value={endDate} />
	</div>
	<button
		onclick={() => {
			q = '';
			type = '';
			categoryId = '';
			startDate = '';
			endDate = '';
		}}
	>
		Reset
	</button>
</div>

{#if error}<div class="error">{error}</div>{/if}

<div class="card" style="margin-top: 14px; padding: 0">
	{#if items.length === 0}
		<div class="empty">No transactions found.</div>
	{:else}
		<table>
			<thead>
				<tr>
					<th>Date</th>
					<th>Description</th>
					<th>Category</th>
					<th>Account</th>
					<th>Type</th>
					<th style="text-align: right">Amount</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				{#each items as tx (tx.id)}
					<tr class="clickable" onclick={() => { editing = tx; showForm = true; }}>
						<td class="muted" style="white-space: nowrap">{formatDate(tx.transaction_date)}</td>
						<td>{tx.description || '—'}</td>
						<td>{tx.category_name}</td>
						<td>{tx.account_name}</td>
						<td><span class="badge {tx.type}">{tx.type}</span></td>
						<td
							style="text-align: right; font-weight: 600; color: {tx.type === 'income'
								? 'var(--green)'
								: 'var(--red)'}"
						>
							{tx.type === 'income' ? '+' : '−'}{formatRupiah(tx.amount)}
						</td>
						<td style="text-align: right">
							<button
								class="small danger"
								onclick={(e) => {
									e.stopPropagation();
									deleting = tx;
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

{#if showForm}
	<TransactionForm
		{accounts}
		{categories}
		transaction={editing}
		onclose={() => (showForm = false)}
		onsaved={async () => await load()}
	/>
{/if}

{#if deleting}
	<Modal title="Delete transaction?" onclose={() => (deleting = null)}>
		<p>
			Delete “{deleting.description || deleting.category_name}”
			({formatRupiah(deleting.amount)})? This cannot be undone.
		</p>
		<div class="row" style="justify-content: flex-end; margin-top: 16px">
			<button onclick={() => (deleting = null)}>Cancel</button>
			<button class="danger" onclick={confirmDelete}>Delete</button>
		</div>
	</Modal>
{/if}
