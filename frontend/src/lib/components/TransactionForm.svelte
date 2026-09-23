<script lang="ts">
	import { untrack } from 'svelte';
	import Modal from './Modal.svelte';
	import type { Account, Category, Transaction } from '$lib/types';
	import { transactionsApi } from '$lib/api';
	import { todayIso } from '$lib/format';

	let {
		accounts,
		categories,
		transaction = null,
		onclose,
		onsaved
	}: {
		accounts: Account[];
		categories: Category[];
		transaction?: Transaction | null;
		onclose: () => void;
		onsaved?: () => void;
	} = $props();

	const seed = untrack(() => ({
		type: transaction?.type ?? 'expense',
		amount: transaction ? String(transaction.amount) : '',
		category_id: transaction?.category_id ?? '',
		account_id: transaction?.account_id ?? (accounts.find((a) => a.is_active)?.id ?? ''),
		description: transaction?.description ?? '',
		date: transaction?.transaction_date ?? todayIso()
	}));

	let type = $state(seed.type);
	let amount = $state(seed.amount);
	let category_id = $state(seed.category_id);
	let account_id = $state(seed.account_id);
	let description = $state(seed.description);
	let date = $state(seed.date);
	let error = $state('');
	let saving = $state(false);

	const filteredCategories = $derived(categories.filter((c) => c.type === type));

	$effect(() => {
		if (!filteredCategories.some((c) => c.id === category_id)) {
			category_id = filteredCategories[0]?.id ?? '';
		}
	});

	async function save() {
		error = '';
		const num = Number(amount);
		if (!num || num <= 0) {
			error = 'Amount must be greater than 0';
			return;
		}
		if (!category_id || !account_id) {
			error = 'Category and account are required';
			return;
		}
		saving = true;
		try {
			const payload = {
				type,
				amount: num,
				category_id,
				account_id,
				description,
				transaction_date: date
			};
			if (transaction) await transactionsApi.update(transaction.id, payload);
			else await transactionsApi.create(payload);
			onsaved?.();
			onclose();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to save';
		} finally {
			saving = false;
		}
	}
</script>

<Modal title={transaction ? 'Edit Transaction' : 'Add Transaction'} {onclose}>
	<div class="field">
		<div class="lbl">Type</div>
		<div class="seg" role="group" aria-label="Transaction type">
			<button class:active={type === 'expense'} onclick={() => (type = 'expense')} type="button">
				Expense
			</button>
			<button class:active={type === 'income'} onclick={() => (type = 'income')} type="button">
				Income
			</button>
		</div>
	</div>

	<div class="field">
		<label for="tx-amount">Amount</label>
		<input id="tx-amount" type="number" min="1" placeholder="50000" bind:value={amount} />
	</div>

	<div class="field">
		<label for="tx-category">Category</label>
		<select id="tx-category" bind:value={category_id}>
			{#each filteredCategories as c (c.id)}
				<option value={c.id}>{c.name}</option>
			{/each}
		</select>
	</div>

	<div class="field">
		<label for="tx-account">Account</label>
		<select id="tx-account" bind:value={account_id}>
			{#each accounts.filter((a) => a.is_active) as a (a.id)}
				<option value={a.id}>{a.name}</option>
			{/each}
		</select>
	</div>

	<div class="field">
		<label for="tx-desc">Description</label>
		<input id="tx-desc" type="text" placeholder="Lunch" bind:value={description} />
	</div>

	<div class="field">
		<label for="tx-date">Date</label>
		<input id="tx-date" type="date" bind:value={date} />
	</div>

	{#if error}<div class="error">{error}</div>{/if}

	<div class="row" style="justify-content: flex-end; margin-top: 8px">
		<button onclick={onclose} type="button">Cancel</button>
		<button class="primary" onclick={save} disabled={saving} type="button">
			{saving ? 'Saving…' : 'Save'}
		</button>
	</div>
</Modal>
