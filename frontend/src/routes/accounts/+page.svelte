<script lang="ts">
	import { accountsApi, transfersApi } from '$lib/api';
	import type { Account, AccountType, Transfer } from '$lib/types';
	import { formatDate, formatRupiah, todayIso } from '$lib/format';
	import Modal from '$lib/components/Modal.svelte';

	let accounts = $state<Account[]>([]);
	let transfers = $state<Transfer[]>([]);
	let error = $state('');
	let notice = $state('');
	let showForm = $state(false);
	let editing = $state<Account | null>(null);
	let deleting = $state<Account | null>(null);
	let showTransfer = $state(false);

	let name = $state('');
	let type = $state<AccountType>('cash');
	let initial = $state('0');

	let tFrom = $state('');
	let tTo = $state('');
	let tAmount = $state('');
	let tDesc = $state('');
	let tDate = $state(todayIso());
	let tError = $state('');
	let tBusy = $state(false);

	const TYPES: AccountType[] = ['cash', 'bank', 'e-wallet', 'other'];

	let started = false;

	async function load() {
		error = '';
		try {
			[accounts, transfers] = await Promise.all([accountsApi.list(true), transfersApi.list()]);
			if (!tFrom && accounts.length) tFrom = accounts[0].id;
			if (!tTo && accounts.length > 1) tTo = accounts[1].id;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load';
		}
	}

	$effect(() => {
		if (started) return;
		started = true;
		void load();
	});

	function openCreate() {
		editing = null;
		name = '';
		type = 'cash';
		initial = '0';
		showForm = true;
	}

	function openEdit(a: Account) {
		editing = a;
		name = a.name;
		type = a.type;
		initial = String(a.initial_balance);
		showForm = true;
	}

	async function saveAccount() {
		error = '';
		try {
			if (editing) {
				await accountsApi.update(editing.id, {
					name,
					type,
					initial_balance: Number(initial) || 0
				});
			} else {
				await accountsApi.create({ name, type, initial_balance: Number(initial) || 0 });
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
			const res = await accountsApi.remove(deleting.id);
			notice = res.detail;
			deleting = null;
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete';
		}
	}

	async function saveTransfer() {
		tError = '';
		const amount = Number(tAmount);
		if (!amount || amount <= 0) {
			tError = 'Amount must be greater than 0';
			return;
		}
		if (tFrom === tTo) {
			tError = 'Source and destination must differ';
			return;
		}
		tBusy = true;
		try {
			await transfersApi.create({
				from_account_id: tFrom,
				to_account_id: tTo,
				amount,
				description: tDesc,
				transfer_date: tDate
			});
			showTransfer = false;
			tAmount = '';
			tDesc = '';
			await load();
		} catch (e) {
			tError = e instanceof Error ? e.message : 'Failed to transfer';
		} finally {
			tBusy = false;
		}
	}

	async function deleteTransfer(t: Transfer) {
		try {
			await transfersApi.remove(t.id);
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to delete';
		}
	}

	const activeAccounts = $derived(accounts.filter((a) => a.is_active));
	const total = $derived(activeAccounts.reduce((s, a) => s + a.balance, 0));
</script>

<div class="page-head">
	<div>
		<h1>Accounts</h1>
		<div class="muted" style="font-size: 13px">Total balance: {formatRupiah(total)}</div>
	</div>
	<div class="row">
		<button
			onclick={() => {
				showTransfer = true;
				tError = '';
			}}
			disabled={accounts.length < 2}
		>
			⇄ Transfer
		</button>
		<button class="primary" onclick={openCreate}>+ Add Account</button>
	</div>
</div>

{#if error}<div class="error">{error}</div>{/if}
{#if notice}<div class="muted" style="margin-bottom: 10px">{notice}</div>{/if}

{#if accounts.length === 0 && !error}
	<div class="card empty">No accounts yet. Create your first account (cash, bank, or e-wallet).</div>
{:else}
	<div class="grid grid-3" style="margin-bottom: 18px">
		{#each accounts as a (a.id)}
			<div class="card" class:muted={!a.is_active}>
				<div class="row" style="justify-content: space-between">
					<div>
						<strong>{a.name}</strong>
						<span class="badge type" style="margin-left: 6px">{a.type}</span>
						{#if !a.is_active}<span class="muted" style="font-size: 11px"> (inactive)</span>{/if}
					</div>
				</div>
				<div style="font-size: 20px; font-weight: 700; margin-top: 10px">
					{formatRupiah(a.balance)}
				</div>
				<div class="muted" style="font-size: 12px; margin-top: 4px">
					Initial: {formatRupiah(a.initial_balance)}
				</div>
				<div class="row" style="margin-top: 12px; justify-content: flex-end">
					<button class="small" onclick={() => openEdit(a)}>Edit</button>
					{#if a.is_active}
						<button class="small danger" onclick={() => (deleting = a)}>Delete</button>
					{/if}
				</div>
			</div>
		{/each}
	</div>
{/if}

<div class="card">
	<h2>Transfers</h2>
	{#if transfers.length === 0}
		<div class="empty">No transfers yet.</div>
	{:else}
		<table>
			<thead>
				<tr>
					<th>Date</th>
					<th>From</th>
					<th>To</th>
					<th>Description</th>
					<th style="text-align: right">Amount</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				{#each transfers as t (t.id)}
					<tr>
						<td class="muted">{formatDate(t.transfer_date)}</td>
						<td>{t.from_account_name}</td>
						<td>{t.to_account_name}</td>
						<td>{t.description || '—'}</td>
						<td style="text-align: right; font-weight: 600">{formatRupiah(t.amount)}</td>
						<td style="text-align: right">
							<button class="small danger" onclick={() => deleteTransfer(t)}>Delete</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>

{#if showForm}
	<Modal title={editing ? 'Edit Account' : 'Add Account'} onclose={() => (showForm = false)}>
		<div class="field">
			<label for="a-name">Name</label>
			<input id="a-name" type="text" placeholder="BCA" bind:value={name} />
		</div>
		<div class="field">
			<label for="a-type">Type</label>
			<select id="a-type" bind:value={type}>
				{#each TYPES as t (t)}
					<option value={t}>{t}</option>
				{/each}
			</select>
		</div>
		<div class="field">
			<label for="a-initial">Initial Balance</label>
			<input id="a-initial" type="number" bind:value={initial} />
		</div>
		{#if error}<div class="error">{error}</div>{/if}
		<div class="row" style="justify-content: flex-end; margin-top: 8px">
			<button onclick={() => (showForm = false)}>Cancel</button>
			<button class="primary" onclick={saveAccount}>Save</button>
		</div>
	</Modal>
{/if}

{#if showTransfer}
	<Modal title="Transfer Between Accounts" onclose={() => (showTransfer = false)}>
		<div class="field">
			<label for="t-from">From</label>
			<select id="t-from" bind:value={tFrom}>
				{#each activeAccounts as a (a.id)}
					<option value={a.id}>{a.name}</option>
				{/each}
			</select>
		</div>
		<div class="field">
			<label for="t-to">To</label>
			<select id="t-to" bind:value={tTo}>
				{#each activeAccounts as a (a.id)}
					<option value={a.id}>{a.name}</option>
				{/each}
			</select>
		</div>
		<div class="field">
			<label for="t-amount">Amount</label>
			<input id="t-amount" type="number" min="1" placeholder="1000000" bind:value={tAmount} />
		</div>
		<div class="field">
			<label for="t-desc">Description</label>
			<input id="t-desc" type="text" bind:value={tDesc} />
		</div>
		<div class="field">
			<label for="t-date">Date</label>
			<input id="t-date" type="date" bind:value={tDate} />
		</div>
		{#if tError}<div class="error">{tError}</div>{/if}
		<div class="row" style="justify-content: flex-end; margin-top: 8px">
			<button onclick={() => (showTransfer = false)}>Cancel</button>
			<button class="primary" onclick={saveTransfer} disabled={tBusy}>
				{tBusy ? 'Saving…' : 'Transfer'}
			</button>
		</div>
	</Modal>
{/if}

{#if deleting}
	<Modal title="Delete account?" onclose={() => (deleting = null)}>
		<p>
			Delete “{deleting.name}”? Accounts with transaction history will be deactivated instead.
		</p>
		<div class="row" style="justify-content: flex-end; margin-top: 16px">
			<button onclick={() => (deleting = null)}>Cancel</button>
			<button class="danger" onclick={confirmDelete}>Delete</button>
		</div>
	</Modal>
{/if}
